"""
Download and extract MovieLens dataset
Supports both manual download and automated download from grouplens.org
"""

import os
import urllib.request
import zipfile
import pandas as pd
from pathlib import Path
from typing import Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def download_movielens(
    dataset_size: str = "small",
    output_dir: str = "data/raw",
    force_download: bool = False
) -> Tuple[pd.DataFrame, pd.DataFrame, Optional[pd.DataFrame]]:
    """
    Download MovieLens dataset
    
    Args:
        dataset_size: "small" (100K), "1m" (1M), "10m" (10M), or "25m" (25M)
        output_dir: Directory to save downloaded files
        force_download: If True, download even if files exist
    
    Returns:
        Tuple of (movies_df, ratings_df, tags_df)
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # MovieLens dataset URLs
    urls = {
        "small": "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip",
        "1m": "https://files.grouplens.org/datasets/movielens/ml-1m.zip",
        "10m": "https://files.grouplens.org/datasets/movielens/ml-10m.zip",
        "25m": "https://files.grouplens.org/datasets/movielens/ml-25m.zip"
    }
    
    if dataset_size not in urls:
        raise ValueError(f"Invalid dataset size: {dataset_size}. Choose from {list(urls.keys())}")
    
    url = urls[dataset_size]
    zip_path = output_path / f"movielens-{dataset_size}.zip"
    extract_dir = output_path / f"movielens-{dataset_size}"
    
    # Check if already downloaded
    if zip_path.exists() and not force_download:
        logger.info(f"MovieLens dataset already exists at {zip_path}")
    else:
        logger.info(f"Downloading MovieLens {dataset_size} dataset...")
        logger.info(f"URL: {url}")
        
        try:
            urllib.request.urlretrieve(url, zip_path)
            logger.info(f"Downloaded to {zip_path}")
        except Exception as e:
            logger.error(f"Failed to download: {e}")
            logger.info("Please download manually from https://grouplens.org/datasets/movielens/")
            raise
    
    # Extract if not already extracted
    if not extract_dir.exists() or force_download:
        logger.info(f"Extracting {zip_path}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(output_path)
        logger.info(f"Extracted to {extract_dir}")
    
    # Find CSV files
    csv_files = list(extract_dir.glob("*.csv"))
    
    if not csv_files:
        # Try nested directory (ml-latest-small structure)
        nested_dirs = [d for d in extract_dir.iterdir() if d.is_dir()]
        if nested_dirs:
            extract_dir = nested_dirs[0]
            csv_files = list(extract_dir.glob("*.csv"))
    
    logger.info(f"Found CSV files: {[f.name for f in csv_files]}")
    
    # Load movies.csv
    movies_file = extract_dir / "movies.csv"
    if not movies_file.exists():
        # Try alternative names
        for alt_name in ["movies.csv", "movies.dat"]:
            alt_file = extract_dir / alt_name
            if alt_file.exists():
                movies_file = alt_file
                break
    
    if movies_file.suffix == ".dat":
        # Handle .dat format (pipe-separated)
        movies_df = pd.read_csv(
            movies_file,
            sep="::",
            engine="python",
            names=["movie_id", "title", "genres"],
            encoding="latin-1"
        )
    else:
        movies_df = pd.read_csv(movies_file)
    
    logger.info(f"Loaded {len(movies_df)} movies")
    
    # Load ratings.csv
    ratings_file = extract_dir / "ratings.csv"
    if not ratings_file.exists():
        ratings_file = extract_dir / "ratings.dat"
    
    if ratings_file.suffix == ".dat":
        ratings_df = pd.read_csv(
            ratings_file,
            sep="::",
            engine="python",
            names=["user_id", "movie_id", "rating", "timestamp"],
            encoding="latin-1"
        )
    else:
        ratings_df = pd.read_csv(ratings_file)
        # Ensure timestamp column exists
        if "timestamp" not in ratings_df.columns:
            ratings_df["timestamp"] = pd.NaT
    
    logger.info(f"Loaded {len(ratings_df)} ratings")
    
    # Load tags.csv (optional)
    tags_df = None
    tags_file = extract_dir / "tags.csv"
    if tags_file.exists():
        if tags_file.suffix == ".dat":
            tags_df = pd.read_csv(
                tags_file,
                sep="::",
                engine="python",
                names=["user_id", "movie_id", "tag", "timestamp"],
                encoding="latin-1"
            )
        else:
            tags_df = pd.read_csv(tags_file)
        logger.info(f"Loaded {len(tags_df)} tags")
    
    return movies_df, ratings_df, tags_df


def parse_movie_title(title: str) -> Tuple[str, Optional[int]]:
    """
    Parse movie title to extract year
    
    Example: "Toy Story (1995)" -> ("Toy Story", 1995)
    """
    import re
    match = re.search(r'\((\d{4})\)', title)
    if match:
        year = int(match.group(1))
        clean_title = re.sub(r'\s*\(\d{4}\)\s*$', '', title).strip()
        return clean_title, year
    return title, None


def standardize_movielens_data(
    movies_df: pd.DataFrame,
    ratings_df: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Standardize MovieLens data format
    
    Args:
        movies_df: Raw movies dataframe
        ratings_df: Raw ratings dataframe
    
    Returns:
        Standardized (movies_df, ratings_df)
    """
    # Parse movie titles
    parsed = movies_df['title'].apply(parse_movie_title)
    movies_df['title_clean'] = [p[0] for p in parsed]
    movies_df['year'] = [p[1] for p in parsed]
    
    # Ensure movie_id is string for consistency
    movies_df['movie_id'] = movies_df['movie_id'].astype(str)
    ratings_df['movie_id'] = ratings_df['movie_id'].astype(str)
    
    # Convert timestamp to datetime
    if 'timestamp' in ratings_df.columns:
        ratings_df['timestamp'] = pd.to_datetime(ratings_df['timestamp'], unit='s', errors='coerce')
    
    # Standardize genres
    if 'genres' in movies_df.columns:
        movies_df['genres'] = movies_df['genres'].fillna('').str.replace('|', ', ')
    
    return movies_df, ratings_df


if __name__ == "__main__":
    # Download small dataset for testing
    movies_df, ratings_df, tags_df = download_movielens(
        dataset_size="small",
        output_dir="data/raw",
        force_download=False
    )
    
    # Standardize data
    movies_df, ratings_df = standardize_movielens_data(movies_df, ratings_df)
    
    # Save to processed directory
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    movies_df.to_csv(output_dir / "movielens_movies.csv", index=False)
    ratings_df.to_csv(output_dir / "movielens_ratings.csv", index=False)
    
    if tags_df is not None:
        tags_df.to_csv(output_dir / "movielens_tags.csv", index=False)
    
    logger.info(f"Saved processed data to {output_dir}")
    logger.info(f"Movies: {len(movies_df)}, Ratings: {len(ratings_df)}")

