# CinemaCompass Data Pipeline

This directory contains scripts and data for the CinemaCompass recommendation system.

## Directory Structure

```
data/
├── raw/              # Raw downloaded datasets
├── processed/        # Cleaned and merged datasets
└── scripts/          # Data acquisition and processing scripts
    ├── download_movielens.py
    ├── fetch_tmdb.py
    ├── merge_datasets.py
    └── clean_data.py
```

## Data Acquisition Pipeline

### 1. Download MovieLens Dataset

```bash
python data/scripts/download_movielens.py
```

Downloads the MovieLens dataset (default: small/100K version) and extracts it to `data/raw/`.

**Options:**
- `dataset_size`: "small" (100K), "1m" (1M), "10m" (10M), or "25m" (25M)

**Output:**
- `data/processed/movielens_movies.csv`
- `data/processed/movielens_ratings.csv`

### 2. Fetch TMDb Metadata

```bash
export TMDB_API_KEY='your_api_key_here'
python data/scripts/fetch_tmdb.py
```

Enriches MovieLens movies with metadata from TMDb API (posters, descriptions, cast, etc.).

**Requirements:**
- TMDb API key from https://www.themoviedb.org/settings/api
- Set environment variable: `export TMDB_API_KEY='your_key'`

**Note:** TMDb API has rate limits (40 requests per 10 seconds). The script includes rate limiting.

**Output:**
- `data/processed/movies_enriched.csv`

### 3. Merge Datasets

```bash
python data/scripts/merge_datasets.py
```

Merges MovieLens and TMDb data into unified datasets.

**Output:**
- `data/processed/movies_merged.csv`
- `data/processed/ratings_merged.csv`

### 4. Clean Data

```bash
python data/scripts/clean_data.py
```

Cleans and validates the merged datasets (removes duplicates, normalizes formats, validates relationships).

**Output:**
- `data/processed/movies_cleaned.csv`
- `data/processed/ratings_cleaned.csv`

## Complete Pipeline

Run all steps in sequence:

```bash
# Step 1: Download MovieLens
python data/scripts/download_movielens.py

# Step 2: Fetch TMDb enrichment (requires API key)
export TMDB_API_KEY='your_key'
python data/scripts/fetch_tmdb.py

# Step 3: Merge datasets
python data/scripts/merge_datasets.py

# Step 4: Clean data
python data/scripts/clean_data.py
```

## Data Formats

### Movies CSV Columns
- `movie_id`: Unique movie identifier
- `title`: Movie title
- `title_clean`: Cleaned title (without year)
- `year`: Release year
- `genres`: Comma-separated genres
- `director`: Director name
- `cast`: Comma-separated top cast members
- `overview`: Movie description/synopsis
- `poster_url`: TMDb poster image URL
- `backdrop_url`: TMDb backdrop image URL
- `vote_average`: Average TMDb rating
- `vote_count`: Number of TMDb votes
- `runtime`: Movie runtime in minutes
- `tags`: Comma-separated keywords/tags

### Ratings CSV Columns
- `user_id`: User identifier
- `movie_id`: Movie identifier
- `rating`: Rating value (0.5-5.0 scale)
- `timestamp`: Rating timestamp

## Notes

- The TMDb enrichment step is optional but recommended for better metadata
- Large datasets (10M, 25M) may take significant time to process
- TMDb API rate limiting is handled automatically
- Data files are saved in CSV format for easy loading with pandas

