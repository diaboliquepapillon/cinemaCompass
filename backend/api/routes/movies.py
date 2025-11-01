"""
Movie routes
"""

import sys
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from recommendation_system.data_loader import load_from_csv, load_cleaned_datasets

from ..database import get_db
from ..models import Movie, Rating
from ..cache import get_cached_movie, cache_movie

router = APIRouter()

# Load movies dataframe
movies_df = None


def load_movies():
    """Load movies dataframe"""
    global movies_df
    if movies_df is None:
        try:
            movies_df, _ = load_cleaned_datasets()
        except FileNotFoundError:
            movies_df, _ = load_from_csv()


class MovieResponse(BaseModel):
    movie_id: str
    title: str
    genres: Optional[str] = None
    director: Optional[str] = None
    cast: Optional[str] = None
    overview: Optional[str] = None
    poster_url: Optional[str] = None
    backdrop_url: Optional[str] = None
    year: Optional[int] = None
    runtime: Optional[int] = None
    vote_average: Optional[float] = None
    vote_count: Optional[int] = None


@router.get("/{movie_id}", response_model=MovieResponse)
async def get_movie(movie_id: str, db=Depends(get_db)):
    """Get movie details"""
    load_movies()
    
    # Check cache
    cache_key = f"movie:{movie_id}"
    cached = get_cached_movie(cache_key)
    if cached:
        return cached
    
    movie_info = movies_df[movies_df['movie_id'] == movie_id]
    if movie_info.empty:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    movie = movie_info.iloc[0]
    
    response = MovieResponse(
        movie_id=str(movie['movie_id']),
        title=movie.get('title', 'Unknown'),
        genres=movie.get('genres'),
        director=movie.get('director'),
        cast=movie.get('cast'),
        overview=movie.get('overview'),
        poster_url=movie.get('poster_url'),
        backdrop_url=movie.get('backdrop_url'),
        year=int(movie.get('year')) if pd.notna(movie.get('year')) else None,
        runtime=int(movie.get('runtime')) if pd.notna(movie.get('runtime')) else None,
        vote_average=float(movie.get('vote_average')) if pd.notna(movie.get('vote_average')) else None,
        vote_count=int(movie.get('vote_count')) if pd.notna(movie.get('vote_count')) else None
    )
    
    # Cache result
    cache_movie(cache_key, response, ttl=86400)  # 24 hours
    
    return response


@router.get("/search/list")
async def search_movies(
    q: Optional[str] = Query(None, description="Search query"),
    genre: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db=Depends(get_db)
):
    """Search movies"""
    load_movies()
    
    filtered_df = movies_df.copy()
    
    # Apply filters
    if q:
        filtered_df = filtered_df[
            filtered_df['title'].str.contains(q, case=False, na=False)
        ]
    
    if genre:
        filtered_df = filtered_df[
            filtered_df['genres'].str.contains(genre, case=False, na=False)
        ]
    
    if year:
        filtered_df = filtered_df[filtered_df['year'] == year]
    
    # Limit results
    filtered_df = filtered_df.head(limit)
    
    results = []
    for _, movie in filtered_df.iterrows():
        results.append({
            "movie_id": str(movie['movie_id']),
            "title": movie.get('title', 'Unknown'),
            "genres": movie.get('genres'),
            "poster_url": movie.get('poster_url'),
            "year": int(movie.get('year')) if pd.notna(movie.get('year')) else None
        })
    
    return {"results": results, "count": len(results)}


@router.get("/trending/list")
async def get_trending_movies(
    limit: int = Query(10, ge=1, le=50),
    db=Depends(get_db)
):
    """Get trending movies"""
    load_movies()
    
    # Sort by vote_average and vote_count (popularity)
    trending = movies_df.copy()
    trending = trending.sort_values(
        by=['vote_average', 'vote_count'],
        ascending=False
    ).head(limit)
    
    results = []
    for _, movie in trending.iterrows():
        results.append({
            "movie_id": str(movie['movie_id']),
            "title": movie.get('title', 'Unknown'),
            "genres": movie.get('genres'),
            "poster_url": movie.get('poster_url'),
            "vote_average": float(movie.get('vote_average')) if pd.notna(movie.get('vote_average')) else None
        })
    
    return {"results": results}


@router.post("/{movie_id}/rate")
async def rate_movie(
    movie_id: str,
    rating: float = Query(..., ge=0.5, le=5.0),
    user_id: str = Query(..., description="User ID"),
    db=Depends(get_db)
):
    """Rate a movie"""
    # Check if rating exists
    existing = db.query(Rating).filter(
        Rating.user_id == user_id,
        Rating.movie_id == movie_id
    ).first()
    
    if existing:
        existing.rating = rating
    else:
        new_rating = Rating(
            user_id=user_id,
            movie_id=movie_id,
            rating=rating
        )
        db.add(new_rating)
    
    db.commit()
    
    # Invalidate user recommendations cache
    # Clear cache for this user
    
    return {"message": "Rating saved", "movie_id": movie_id, "rating": rating}

