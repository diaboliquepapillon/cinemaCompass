"""
Data cleaning and preprocessing utilities
Handles missing values, duplicates, normalization, and validation
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Optional
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clean_movies_data(movies_df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and normalize movies dataset
    
    Args:
        movies_df: Raw movies DataFrame
    
    Returns:
        Cleaned movies DataFrame
    """
    df = movies_df.copy()
    
    logger.info(f"Cleaning {len(df)} movies...")
    
    # Remove duplicates
    initial_count = len(df)
    df = df.drop_duplicates(subset=['movie_id'], keep='first')
    if len(df) < initial_count:
        logger.info(f"Removed {initial_count - len(df)} duplicate movies")
    
    # Clean titles
    if 'title' in df.columns:
        df['title'] = df['title'].str.strip()
        df['title'] = df['title'].replace('', np.nan)
    
    # Parse and clean genres
    if 'genres' in df.columns:
        df['genres'] = df['genres'].fillna('')
        # Normalize genre separators (handle |, comma, etc.)
        df['genres'] = df['genres'].str.replace('|', ',')
        df['genres'] = df['genres'].str.replace('  ', ' ')
        df['genres'] = df['genres'].str.strip()
        # Remove empty genre entries
        df['genres'] = df['genres'].apply(
            lambda x: ', '.join([g.strip() for g in x.split(',') if g.strip()]) if x else ''
        )
    
    # Clean and validate years
    if 'year' in df.columns:
        df['year'] = pd.to_numeric(df['year'], errors='coerce')
        # Remove invalid years (too old or future)
        df = df[(df['year'].isna()) | ((df['year'] >= 1880) & (df['year'] <= 2030))]
    
    # Clean director names
    if 'director' in df.columns:
        df['director'] = df['director'].str.strip()
        df['director'] = df['director'].fillna('')
    
    # Clean cast (limit to reasonable number)
    if 'cast' in df.columns:
        df['cast'] = df['cast'].fillna('')
        # Limit to first 10 cast members if comma-separated
        df['cast'] = df['cast'].apply(
            lambda x: ', '.join([c.strip() for c in x.split(',')[:10]]) if x else ''
        )
    
    # Clean overview/description
    if 'overview' in df.columns:
        df['overview'] = df['overview'].fillna('')
        df['overview'] = df['overview'].str.strip()
        # Remove excessive whitespace
        df['overview'] = df['overview'].str.replace(r'\s+', ' ', regex=True)
    
    # Validate and clean URLs
    url_columns = ['poster_url', 'backdrop_url']
    for col in url_columns:
        if col in df.columns:
            df[col] = df[col].apply(validate_url)
    
    # Clean numeric columns
    numeric_cols = ['runtime', 'vote_average', 'vote_count', 'popularity', 'budget', 'revenue']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            # Replace negative values with NaN
            if col in ['vote_average', 'vote_count', 'popularity']:
                df[col] = df[col].where(df[col] >= 0)
    
    # Remove movies with no essential data
    essential_cols = ['title']
    df = df.dropna(subset=essential_cols)
    
    logger.info(f"Cleaned dataset: {len(df)} movies")
    
    return df


def clean_ratings_data(ratings_df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and normalize ratings dataset
    
    Args:
        ratings_df: Raw ratings DataFrame
    
    Returns:
        Cleaned ratings DataFrame
    """
    df = ratings_df.copy()
    
    logger.info(f"Cleaning {len(df)} ratings...")
    
    # Remove duplicates
    initial_count = len(df)
    df = df.drop_duplicates(subset=['user_id', 'movie_id'], keep='last')
    if len(df) < initial_count:
        logger.info(f"Removed {initial_count - len(df)} duplicate ratings")
    
    # Validate ratings (typically 1-5 or 1-10 scale)
    if 'rating' in df.columns:
        df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
        # MovieLens uses 0.5-5.0, normalize if needed
        if df['rating'].max() <= 5.0:
            # Already normalized
            pass
        elif df['rating'].max() <= 10.0:
            # Convert 1-10 to 1-5 scale
            df['rating'] = (df['rating'] / 2.0).round(1)
        
        # Remove invalid ratings
        df = df[(df['rating'] >= 0.5) & (df['rating'] <= 5.0)]
        df = df.dropna(subset=['rating'])
    
    # Clean user_id and movie_id
    for col in ['user_id', 'movie_id']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            df = df[df[col] != '']
    
    # Validate timestamp if present
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        # Remove future timestamps
        df = df[df['timestamp'] <= pd.Timestamp.now()]
    
    logger.info(f"Cleaned dataset: {len(df)} ratings")
    
    return df


def validate_url(url: Optional[str]) -> Optional[str]:
    """
    Validate and clean URL
    
    Args:
        url: URL string
    
    Returns:
        Validated URL or None
    """
    if pd.isna(url) or url == '':
        return None
    
    url = str(url).strip()
    
    # Check if it looks like a URL
    if not (url.startswith('http://') or url.startswith('https://')):
        return None
    
    # Basic validation
    if re.match(r'^https?://[^\s/$.?#].[^\s]*$', url):
        return url
    
    return None


def standardize_genres(genres_str: str) -> str:
    """
    Standardize genre names (e.g., "Sci-Fi" -> "Science Fiction")
    
    Args:
        genres_str: Comma-separated genre string
    
    Returns:
        Standardized genre string
    """
    if not genres_str:
        return ''
    
    # Common genre mappings
    genre_mappings = {
        'sci-fi': 'Science Fiction',
        'sci fi': 'Science Fiction',
        'scifi': 'Science Fiction',
        'sci-fi fiction': 'Science Fiction',
    }
    
    genres = [g.strip() for g in genres_str.split(',')]
    standardized = []
    
    for genre in genres:
        genre_lower = genre.lower()
        if genre_lower in genre_mappings:
            standardized.append(genre_mappings[genre_lower])
        else:
            # Capitalize properly
            standardized.append(genre.title())
    
    return ', '.join(standardized)


def validate_movie_ids(movies_df: pd.DataFrame, ratings_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Ensure all ratings reference valid movies
    
    Args:
        movies_df: Movies DataFrame
        ratings_df: Ratings DataFrame
    
    Returns:
        Validated (movies_df, ratings_df)
    """
    valid_movie_ids = set(movies_df['movie_id'].unique())
    initial_count = len(ratings_df)
    
    ratings_df = ratings_df[ratings_df['movie_id'].isin(valid_movie_ids)]
    
    if len(ratings_df) < initial_count:
        logger.warning(
            f"Removed {initial_count - len(ratings_df)} ratings with invalid movie IDs"
        )
    
    return movies_df, ratings_df


def clean_and_prepare_datasets(
    movies_path: str,
    ratings_path: str,
    output_dir: str = "data/processed"
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Complete data cleaning pipeline
    
    Args:
        movies_path: Path to movies CSV
        ratings_path: Path to ratings CSV
        output_dir: Output directory for cleaned data
    
    Returns:
        Tuple of (cleaned_movies_df, cleaned_ratings_df)
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Load data
    logger.info(f"Loading movies from {movies_path}")
    movies_df = pd.read_csv(movies_path)
    
    logger.info(f"Loading ratings from {ratings_path}")
    ratings_df = pd.read_csv(ratings_path)
    
    # Clean datasets
    movies_df = clean_movies_data(movies_df)
    ratings_df = clean_ratings_data(ratings_df)
    
    # Validate relationships
    movies_df, ratings_df = validate_movie_ids(movies_df, ratings_df)
    
    # Standardize genres
    if 'genres' in movies_df.columns:
        movies_df['genres'] = movies_df['genres'].apply(standardize_genres)
    
    # Save cleaned data
    movies_output = output_path / "movies_cleaned.csv"
    ratings_output = output_path / "ratings_cleaned.csv"
    
    movies_df.to_csv(movies_output, index=False)
    ratings_df.to_csv(ratings_output, index=False)
    
    logger.info(f"Saved cleaned movies to {movies_output}")
    logger.info(f"Saved cleaned ratings to {ratings_output}")
    
    # Print statistics
    logger.info("\nDataset Statistics:")
    logger.info(f"Movies: {len(movies_df)}")
    logger.info(f"Ratings: {len(ratings_df)}")
    logger.info(f"Users: {ratings_df['user_id'].nunique()}")
    logger.info(f"Average ratings per movie: {ratings_df.groupby('movie_id').size().mean():.2f}")
    logger.info(f"Average rating: {ratings_df['rating'].mean():.2f}")
    
    return movies_df, ratings_df


if __name__ == "__main__":
    # Default paths (assumes merge step completed)
    movies_path = "data/processed/movies_merged.csv"
    ratings_path = "data/processed/ratings_merged.csv"
    
    # If merged files don't exist, try raw MovieLens files
    if not Path(movies_path).exists():
        movies_path = "data/processed/movielens_movies.csv"
    if not Path(ratings_path).exists():
        ratings_path = "data/processed/movielens_ratings.csv"
    
    if not Path(movies_path).exists() or not Path(ratings_path).exists():
        logger.error("Input files not found. Run download_movielens.py and merge_datasets.py first")
        exit(1)
    
    # Clean data
    movies_df, ratings_df = clean_and_prepare_datasets(
        movies_path=movies_path,
        ratings_path=ratings_path
    )
    
    logger.info("Data cleaning complete!")

