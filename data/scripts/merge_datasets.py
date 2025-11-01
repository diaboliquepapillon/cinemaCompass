"""
Merge MovieLens and TMDb datasets
Creates unified movie and ratings datasets
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def merge_datasets(
    movielens_movies_path: str,
    movielens_ratings_path: str,
    tmdb_enriched_path: Optional[str] = None,
    output_dir: str = "data/processed"
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Merge MovieLens and TMDb datasets
    
    Args:
        movielens_movies_path: Path to MovieLens movies CSV
        movielens_ratings_path: Path to MovieLens ratings CSV
        tmdb_enriched_path: Optional path to TMDb enriched movies CSV
        output_dir: Directory to save merged datasets
    
    Returns:
        Tuple of (merged_movies_df, ratings_df)
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Load MovieLens data
    logger.info(f"Loading MovieLens movies from {movielens_movies_path}")
    ml_movies = pd.read_csv(movielens_movies_path)
    
    logger.info(f"Loading MovieLens ratings from {movielens_ratings_path}")
    ratings_df = pd.read_csv(movielens_ratings_path)
    
    # Start with MovieLens movies as base
    movies_df = ml_movies.copy()
    
    # Merge TMDb data if available
    if tmdb_enriched_path and Path(tmdb_enriched_path).exists():
        logger.info(f"Loading TMDb enriched data from {tmdb_enriched_path}")
        tmdb_df = pd.read_csv(tmdb_enriched_path)
        
        # Merge on movie_id (assuming TMDb data has original MovieLens movie_id)
        # If TMDb data uses tmdb_id, we need to match by title/year
        if 'movie_id' in tmdb_df.columns:
            # Direct merge on movie_id
            merge_on = 'movie_id'
        elif 'tmdb_id' in tmdb_df.columns:
            # Need to match by title/year
            logger.info("Matching movies by title and year")
            movies_df = movies_df.merge(
                tmdb_df,
                left_on=['title_clean', 'year'],
                right_on=['title', 'year'],
                how='left',
                suffixes=('', '_tmdb')
            )
        else:
            # Try to match by title
            logger.info("Matching movies by title")
            movies_df = movies_df.merge(
                tmdb_df,
                left_on='title_clean',
                right_on='title',
                how='left',
                suffixes=('', '_tmdb')
            )
        
        # Prioritize TMDb data for enriched fields
        enriched_fields = [
            'overview', 'runtime', 'director', 'cast', 'poster_url', 
            'backdrop_url', 'vote_average', 'vote_count', 'popularity',
            'tags', 'production_companies', 'spoken_languages'
        ]
        
        for field in enriched_fields:
            if field in movies_df.columns:
                # Use TMDb value if available, otherwise keep MovieLens value
                movies_df[field] = movies_df[field].fillna(movies_df.get(f'{field}_tmdb', pd.Series()))
    
    # Ensure movie_id is string for consistency
    movies_df['movie_id'] = movies_df['movie_id'].astype(str)
    ratings_df['movie_id'] = ratings_df['movie_id'].astype(str)
    
    # Standardize column names
    movies_df = standardize_column_names(movies_df)
    
    # Fill missing values
    movies_df = fill_missing_values(movies_df)
    
    # Ensure ratings match movies
    valid_movie_ids = set(movies_df['movie_id'].unique())
    ratings_df = ratings_df[ratings_df['movie_id'].isin(valid_movie_ids)]
    
    logger.info(f"Merged dataset: {len(movies_df)} movies, {len(ratings_df)} ratings")
    
    # Save merged datasets
    movies_output = output_path / "movies_merged.csv"
    ratings_output = output_path / "ratings_merged.csv"
    
    movies_df.to_csv(movies_output, index=False)
    ratings_df.to_csv(ratings_output, index=False)
    
    logger.info(f"Saved merged movies to {movies_output}")
    logger.info(f"Saved merged ratings to {ratings_output}")
    
    return movies_df, ratings_df


def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize column names to consistent format"""
    # Standardize to lowercase with underscores
    df.columns = [col.lower().replace(' ', '_').replace('-', '_') for col in df.columns]
    
    # Rename common variations
    column_mapping = {
        'movieid': 'movie_id',
        'movie_id_tmdb': 'tmdb_id',
        'userid': 'user_id',
        'user_id_tmdb': 'user_id',
    }
    
    df = df.rename(columns=column_mapping)
    
    return df


def fill_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Fill missing values with appropriate defaults"""
    # Fill text fields
    text_fields = ['title', 'genres', 'director', 'cast', 'overview', 'tags']
    for field in text_fields:
        if field in df.columns:
            df[field] = df[field].fillna('')
    
    # Fill numeric fields
    numeric_fields = ['year', 'runtime', 'vote_average', 'vote_count', 'popularity']
    for field in numeric_fields:
        if field in df.columns:
            df[field] = pd.to_numeric(df[field], errors='coerce').fillna(0)
    
    return df


if __name__ == "__main__":
    # Default paths
    ml_movies_path = "data/processed/movielens_movies.csv"
    ml_ratings_path = "data/processed/movielens_ratings.csv"
    tmdb_path = "data/processed/movies_enriched.csv"
    
    # Check if files exist
    if not Path(ml_movies_path).exists():
        logger.error(f"MovieLens movies file not found: {ml_movies_path}")
        logger.info("Run download_movielens.py first")
        exit(1)
    
    if not Path(ml_ratings_path).exists():
        logger.error(f"MovieLens ratings file not found: {ml_ratings_path}")
        logger.info("Run download_movielens.py first")
        exit(1)
    
    # Merge datasets
    movies_df, ratings_df = merge_datasets(
        movielens_movies_path=ml_movies_path,
        movielens_ratings_path=ml_ratings_path,
        tmdb_enriched_path=tmdb_path if Path(tmdb_path).exists() else None
    )
    
    logger.info("Dataset merge complete!")

