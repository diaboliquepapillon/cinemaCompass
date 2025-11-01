"""
Fetch movie metadata from TMDb (The Movie Database) API
Enriches MovieLens data with posters, descriptions, cast, and other metadata
"""

import requests
import pandas as pd
import time
import logging
from pathlib import Path
from typing import List, Dict, Optional
import os
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TMDbClient:
    """Client for TMDb API"""
    
    BASE_URL = "https://api.themoviedb.org/3"
    IMAGE_BASE_URL = "https://image.tmdb.org/t/p"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize TMDb client
        
        Args:
            api_key: TMDb API key. If None, reads from TMDB_API_KEY env variable
        """
        self.api_key = api_key or os.getenv("TMDB_API_KEY")
        if not self.api_key:
            raise ValueError(
                "TMDb API key required. Set TMDB_API_KEY environment variable or "
                "pass api_key parameter. Get key from https://www.themoviedb.org/settings/api"
            )
        self.session = requests.Session()
    
    def search_movie(self, title: str, year: Optional[int] = None) -> Optional[Dict]:
        """
        Search for movie by title
        
        Args:
            title: Movie title
            year: Release year (optional)
        
        Returns:
            Movie data dict or None if not found
        """
        url = f"{self.BASE_URL}/search/movie"
        params = {
            "api_key": self.api_key,
            "query": title,
            "language": "en-US"
        }
        if year:
            params["year"] = year
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("results"):
                return data["results"][0]  # Return first match
            return None
        except Exception as e:
            logger.warning(f"Error searching for '{title}': {e}")
            return None
    
    def get_movie_details(self, tmdb_id: int) -> Optional[Dict]:
        """
        Get detailed movie information by TMDb ID
        
        Args:
            tmdb_id: TMDb movie ID
        
        Returns:
            Detailed movie data dict
        """
        url = f"{self.BASE_URL}/movie/{tmdb_id}"
        params = {
            "api_key": self.api_key,
            "language": "en-US",
            "append_to_response": "credits,keywords,videos"
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning(f"Error fetching details for TMDb ID {tmdb_id}: {e}")
            return None
    
    def get_poster_url(self, poster_path: Optional[str], size: str = "w500") -> Optional[str]:
        """
        Get full poster URL
        
        Args:
            poster_path: Poster path from TMDb
            size: Image size (w92, w154, w185, w342, w500, w780, original)
        
        Returns:
            Full poster URL or None
        """
        if not poster_path:
            return None
        return f"{self.IMAGE_BASE_URL}/{size}{poster_path}"
    
    def extract_metadata(self, movie_data: Dict) -> Dict:
        """
        Extract relevant metadata from TMDb movie data
        
        Args:
            movie_data: Raw TMDb movie data
        
        Returns:
            Extracted metadata dict
        """
        credits = movie_data.get("credits", {})
        cast = credits.get("cast", [])
        crew = credits.get("crew", [])
        
        # Get director
        director = None
        for person in crew:
            if person.get("job") == "Director":
                director = person.get("name")
                break
        
        # Get top 5 cast members
        top_cast = [actor.get("name") for actor in cast[:5]]
        
        # Get genres
        genres = [g.get("name") for g in movie_data.get("genres", [])]
        
        # Get keywords/tags
        keywords = movie_data.get("keywords", {}).get("keywords", [])
        tags = [k.get("name") for k in keywords[:10]]
        
        return {
            "tmdb_id": movie_data.get("id"),
            "title": movie_data.get("title"),
            "original_title": movie_data.get("original_title"),
            "overview": movie_data.get("overview"),
            "release_date": movie_data.get("release_date"),
            "runtime": movie_data.get("runtime"),
            "budget": movie_data.get("budget"),
            "revenue": movie_data.get("revenue"),
            "vote_average": movie_data.get("vote_average"),
            "vote_count": movie_data.get("vote_count"),
            "popularity": movie_data.get("popularity"),
            "poster_path": movie_data.get("poster_path"),
            "backdrop_path": movie_data.get("backdrop_path"),
            "poster_url": self.get_poster_url(movie_data.get("poster_path")),
            "backdrop_url": self.get_poster_url(movie_data.get("backdrop_path"), "w1280"),
            "director": director,
            "cast": ", ".join(top_cast) if top_cast else None,
            "genres": ", ".join(genres) if genres else None,
            "tags": ", ".join(tags) if tags else None,
            "production_companies": ", ".join([c.get("name") for c in movie_data.get("production_companies", [])[:3]]),
            "spoken_languages": ", ".join([l.get("name") for l in movie_data.get("spoken_languages", [])]),
        }


def enrich_movies_with_tmdb(
    movies_df: pd.DataFrame,
    output_file: Optional[str] = None,
    rate_limit: float = 0.25  # 4 requests per second (TMDb limit is 40/10s)
) -> pd.DataFrame:
    """
    Enrich MovieLens movies with TMDb metadata
    
    Args:
        movies_df: DataFrame with movies (must have 'title' and optionally 'year')
        output_file: Optional path to save enriched data
        rate_limit: Delay between requests in seconds
    
    Returns:
        Enriched movies DataFrame
    """
    client = TMDbClient()
    
    enriched_data = []
    failed_matches = []
    
    logger.info(f"Enriching {len(movies_df)} movies with TMDb data...")
    
    for idx, row in tqdm(movies_df.iterrows(), total=len(movies_df), desc="Fetching TMDb data"):
        title = row.get('title_clean') or row.get('title', '')
        year = row.get('year')
        
        if not title:
            continue
        
        # Search for movie
        search_result = client.search_movie(title, year)
        
        if search_result:
            # Get detailed info
            tmdb_id = search_result.get("id")
            details = client.get_movie_details(tmdb_id)
            
            if details:
                metadata = client.extract_metadata(details)
                # Merge with original data
                enriched_row = row.to_dict()
                enriched_row.update(metadata)
                enriched_data.append(enriched_row)
            else:
                failed_matches.append(title)
        else:
            failed_matches.append(title)
        
        # Rate limiting
        time.sleep(rate_limit)
    
    logger.info(f"Successfully enriched {len(enriched_data)} movies")
    if failed_matches:
        logger.warning(f"Failed to match {len(failed_matches)} movies")
        logger.debug(f"Failed titles: {failed_matches[:10]}")
    
    enriched_df = pd.DataFrame(enriched_data)
    
    if output_file:
        enriched_df.to_csv(output_file, index=False)
        logger.info(f"Saved enriched data to {output_file}")
    
    return enriched_df


if __name__ == "__main__":
    import sys
    
    # Check for API key
    if not os.getenv("TMDB_API_KEY"):
        logger.error("TMDB_API_KEY environment variable not set")
        logger.info("Get your API key from: https://www.themoviedb.org/settings/api")
        logger.info("Then set it: export TMDB_API_KEY='your_key_here'")
        sys.exit(1)
    
    # Load MovieLens movies
    movies_file = Path("data/processed/movielens_movies.csv")
    if not movies_file.exists():
        logger.error(f"Movies file not found: {movies_file}")
        logger.info("Run download_movielens.py first")
        sys.exit(1)
    
    movies_df = pd.read_csv(movies_file)
    
    # For testing, limit to first 50 movies
    if len(movies_df) > 50:
        logger.info("Limiting to first 50 movies for testing")
        movies_df = movies_df.head(50)
    
    # Enrich with TMDb data
    enriched_df = enrich_movies_with_tmdb(
        movies_df,
        output_file="data/processed/movies_enriched.csv",
        rate_limit=0.25
    )
    
    logger.info(f"Enrichment complete. Enriched {len(enriched_df)} movies.")

