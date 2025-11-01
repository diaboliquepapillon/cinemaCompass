"""
Recommendation routes
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Dict, Optional
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from recommendation_system.hybrid_model import HybridRecommender
from recommendation_system.data_loader import load_from_csv, load_cleaned_datasets
import pandas as pd

from ..database import get_db
from ..models import Movie, Rating
from ..cache import get_cached_recommendations, cache_recommendations
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

router = APIRouter()

# Global recommender instance (loaded on startup)
recommender = None
movies_df = None
ratings_df = None


def init_recommender():
    """Initialize recommender system"""
    global recommender, movies_df, ratings_df
    
    try:
        # Try to load cleaned datasets
        movies_df, ratings_df = load_cleaned_datasets()
    except FileNotFoundError:
        # Fall back to sample data
        movies_df, ratings_df = load_from_csv()
    
    recommender = HybridRecommender(use_adaptive_weights=True)
    recommender.fit(movies_df, ratings_df)
    
    print(f"Recommender initialized with {len(movies_df)} movies")


class RecommendationResponse(BaseModel):
    movie_id: str
    title: str
    score: float
    reason: str
    poster_url: Optional[str] = None
    genres: Optional[str] = None


@router.get("/{user_id}", response_model=List[RecommendationResponse])
async def get_recommendations(
    user_id: str,
    top_k: int = Query(10, ge=1, le=50),
    diversity: float = Query(0.5, ge=0.0, le=1.0),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db=Depends(get_db)
):
    """Get recommendations for a user"""
    global recommender, movies_df
    
    if recommender is None:
        init_recommender()
    
    # Check cache first
    cache_key = f"recommendations:{user_id}:{top_k}"
    cached = get_cached_recommendations(cache_key)
    if cached:
        return cached
    
    # Get user's liked movies from ratings
    user_ratings = db.query(Rating).filter(Rating.user_id == user_id).all()
    liked_movies = [
        str(rating.movie_id) for rating in user_ratings 
        if rating.rating >= 4.0
    ]
    
    # Get recommendations
    recommendations = recommender.get_recommendations(
        user_id=user_id,
        liked_movies=liked_movies if liked_movies else None,
        top_n=top_k
    )
    
    # Enrich with movie data
    enriched_recs = []
    for rec in recommendations:
        movie_info = movies_df[movies_df['movie_id'] == rec['movie_id']]
        if not movie_info.empty:
            movie = movie_info.iloc[0]
            enriched_recs.append(RecommendationResponse(
                movie_id=rec['movie_id'],
                title=rec.get('title', movie.get('title', 'Unknown')),
                score=rec.get('score', 0.0),
                reason=rec.get('reason', ''),
                poster_url=movie.get('poster_url'),
                genres=movie.get('genres')
            ))
    
    # Cache results
    cache_recommendations(cache_key, enriched_recs, ttl=3600)  # 1 hour
    
    return enriched_recs


@router.get("/explain/{user_id}/{movie_id}")
async def explain_recommendation(
    user_id: str,
    movie_id: str,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db=Depends(get_db)
):
    """Get explanation for a specific recommendation"""
    global recommender, movies_df
    
    if recommender is None:
        init_recommender()
    
    # Get user's liked movies
    user_ratings = db.query(Rating).filter(Rating.user_id == user_id).all()
    liked_movies = [str(rating.movie_id) for rating in user_ratings if rating.rating >= 4.0]
    
    # Get recommendation to generate explanation
    recommendations = recommender.get_recommendations(
        user_id=user_id,
        liked_movies=liked_movies if liked_movies else None,
        top_n=50
    )
    
    # Find the specific movie
    target_rec = next((r for r in recommendations if r['movie_id'] == movie_id), None)
    
    if not target_rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    return {
        "movie_id": movie_id,
        "explanation": target_rec.get('reason', ''),
        "score": target_rec.get('score', 0.0),
        "reasoning_type": "hybrid"
    }


@router.post("/feedback")
async def submit_feedback(
    user_id: str,
    movie_id: str,
    feedback: str,  # "like" or "dislike"
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db=Depends(get_db)
):
    """Submit feedback on a recommendation"""
    # Invalidate cache for this user
    cache_key_pattern = f"recommendations:{user_id}:*"
    # Clear cache (implementation depends on Redis)
    
    return {"message": "Feedback received", "movie_id": movie_id, "feedback": feedback}

