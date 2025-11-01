"""
Complete data acquisition pipeline runner
Runs all data processing steps in sequence
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from data.scripts.download_movielens import download_movielens, standardize_movielens_data
from data.scripts.fetch_tmdb import enrich_movies_with_tmdb, TMDbClient
from data.scripts.merge_datasets import merge_datasets
from data.scripts.clean_data import clean_and_prepare_datasets

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_complete_pipeline(
    dataset_size: str = "small",
    use_tmdb: bool = True,
    limit_tmdb: int = 100
):
    """
    Run complete data acquisition and processing pipeline
    
    Args:
        dataset_size: MovieLens dataset size ("small", "1m", "10m", "25m")
        use_tmdb: Whether to enrich with TMDb data
        limit_tmdb: Limit number of movies to enrich (for testing)
    """
    logger.info("=" * 60)
    logger.info("CinemaCompass Data Acquisition Pipeline")
    logger.info("=" * 60)
    
    # Step 1: Download MovieLens
    logger.info("\n[Step 1/4] Downloading MovieLens dataset...")
    try:
        movies_df, ratings_df, tags_df = download_movielens(
            dataset_size=dataset_size,
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
        
        logger.info(f"✓ Downloaded {len(movies_df)} movies and {len(ratings_df)} ratings")
        
    except Exception as e:
        logger.error(f"✗ Failed to download MovieLens: {e}")
        return False
    
    # Step 2: Enrich with TMDb (optional)
    if use_tmdb:
        logger.info("\n[Step 2/4] Enriching with TMDb metadata...")
        try:
            import os
            if not os.getenv("TMDB_API_KEY"):
                logger.warning("TMDB_API_KEY not set. Skipping TMDb enrichment.")
                logger.info("Set TMDB_API_KEY environment variable to enable TMDb enrichment.")
                use_tmdb = False
            else:
                # Limit movies for testing if specified
                movies_to_enrich = movies_df.head(limit_tmdb) if limit_tmdb else movies_df
                
                enriched_df = enrich_movies_with_tmdb(
                    movies_to_enrich,
                    output_file="data/processed/movies_enriched.csv",
                    rate_limit=0.25  # 4 requests per second
                )
                
                logger.info(f"✓ Enriched {len(enriched_df)} movies with TMDb data")
        except Exception as e:
            logger.warning(f"⚠ TMDb enrichment failed: {e}")
            logger.info("Continuing without TMDb enrichment...")
            use_tmdb = False
    
    # Step 3: Merge datasets
    logger.info("\n[Step 3/4] Merging datasets...")
    try:
        merged_movies, merged_ratings = merge_datasets(
            movielens_movies_path="data/processed/movielens_movies.csv",
            movielens_ratings_path="data/processed/movielens_ratings.csv",
            tmdb_enriched_path="data/processed/movies_enriched.csv" if use_tmdb else None,
            output_dir="data/processed"
        )
        
        logger.info(f"✓ Merged {len(merged_movies)} movies and {len(merged_ratings)} ratings")
        
    except Exception as e:
        logger.error(f"✗ Failed to merge datasets: {e}")
        return False
    
    # Step 4: Clean data
    logger.info("\n[Step 4/4] Cleaning and validating data...")
    try:
        cleaned_movies, cleaned_ratings = clean_and_prepare_datasets(
            movies_path="data/processed/movies_merged.csv",
            ratings_path="data/processed/ratings_merged.csv",
            output_dir="data/processed"
        )
        
        logger.info(f"✓ Cleaned {len(cleaned_movies)} movies and {len(cleaned_ratings)} ratings")
        
    except Exception as e:
        logger.error(f"✗ Failed to clean data: {e}")
        return False
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Pipeline Complete!")
    logger.info("=" * 60)
    logger.info(f"Final datasets:")
    logger.info(f"  - Movies: {len(cleaned_movies)}")
    logger.info(f"  - Ratings: {len(cleaned_ratings)}")
    logger.info(f"  - Users: {cleaned_ratings['user_id'].nunique()}")
    logger.info(f"\nOutput files:")
    logger.info(f"  - data/processed/movies_cleaned.csv")
    logger.info(f"  - data/processed/ratings_cleaned.csv")
    logger.info("=" * 60)
    
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run CinemaCompass data pipeline")
    parser.add_argument(
        "--dataset-size",
        type=str,
        default="small",
        choices=["small", "1m", "10m", "25m"],
        help="MovieLens dataset size"
    )
    parser.add_argument(
        "--no-tmdb",
        action="store_true",
        help="Skip TMDb enrichment"
    )
    parser.add_argument(
        "--limit-tmdb",
        type=int,
        default=100,
        help="Limit number of movies to enrich with TMDb (for testing)"
    )
    
    args = parser.parse_args()
    
    success = run_complete_pipeline(
        dataset_size=args.dataset_size,
        use_tmdb=not args.no_tmdb,
        limit_tmdb=args.limit_tmdb
    )
    
    sys.exit(0 if success else 1)

