"""
FastAPI backend for CinemaCompass recommendation system
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import logging

from recommendation_system import HybridRecommender
from recommendation_system.evaluation import precision_at_k, recall_at_k, ndcg_at_k

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="CinemaCompass API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize model (will be loaded with data)
recommender: Optional[HybridRecommender] = None
movies_df: Optional[pd.DataFrame] = None
ratings_df: Optional[pd.DataFrame] = None


# Pydantic models
class RecommendationRequest(BaseModel):
    user_id: Optional[str] = None
    liked_movie_ids: List[str]
    top_n: int = 10


class RecommendationResponse(BaseModel):
    movie_id: str
    title: str
    score: float
    reason: str
    genres: Optional[str] = None
    poster_path: Optional[str] = None
    vote_average: Optional[float] = None


class EvaluationRequest(BaseModel):
    user_id: Optional[str] = None
    liked_movies: List[str]
    relevant_movies: List[str]
    k: int = 10


@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    global recommender, movies_df, ratings_df
    
    logger.info("Loading data and initializing models...")
    # TODO: Load from actual data source (TMDb API or database)
    # For now, models will be initialized on first request
    logger.info("API ready (lazy model loading)")


def load_sample_data():
    """Load sample data - replace with actual data loading"""
    # This is a placeholder - in production, load from database/TMDb
    global movies_df, ratings_df
    
    if movies_df is None:
        # Create minimal sample data structure
        movies_df = pd.DataFrame({
            'id': [],
            'title': [],
            'genres': [],
            'director': [],
            'cast': [],
            'overview': [],
            'poster_path': [],
            'vote_average': []
        })
    
    if ratings_df is None:
        ratings_df = pd.DataFrame({
            'user_id': [],
            'movie_id': [],
            'rating': []
        })
    
    return movies_df, ratings_df


@app.post("/api/recommendations", response_model=List[RecommendationResponse])
async def get_recommendations(request: RecommendationRequest):
    """
    Get hybrid recommendations combining content-based and collaborative filtering
    """
    global recommender, movies_df, ratings_df
    
    try:
        # Lazy load data if needed
        if movies_df is None or len(movies_df) == 0:
            movies_df, ratings_df = load_sample_data()
        
        # Initialize model if needed
        if recommender is None and len(movies_df) > 0 and len(ratings_df) > 0:
            recommender = HybridRecommender(
                content_weight=0.5,
                collaborative_weight=0.5
            )
            recommender.fit(movies_df, ratings_df)
        
        if recommender is None:
            raise HTTPException(status_code=503, detail="Model not initialized - no data available")
        
        # Get recommendations
        recommendations = recommender.get_recommendations(
            user_id=request.user_id,
            liked_movie_ids=request.liked_movie_ids,
            top_n=request.top_n,
            explain=True
        )
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/evaluate")
async def evaluate_recommendations(request: EvaluationRequest):
    """
    Evaluate recommendation quality using Precision@K, Recall@K, NDCG@K
    """
    global recommender
    
    if recommender is None:
        raise HTTPException(status_code=503, detail="Model not initialized")
    
    try:
        # Get recommendations
        recommendations = recommender.get_recommendations(
            user_id=request.user_id,
            liked_movie_ids=request.liked_movies,
            top_n=request.k,
            explain=False
        )
        
        recommended_ids = [rec['movie_id'] for rec in recommendations]
        
        # Calculate metrics
        precision = precision_at_k(recommended_ids, request.relevant_movies, request.k)
        recall = recall_at_k(recommended_ids, request.relevant_movies, request.k)
        ndcg = ndcg_at_k(recommended_ids, request.relevant_movies, request.k)
        
        return {
            "precision@k": precision,
            "recall@k": recall,
            "ndcg@k": ndcg,
            "k": request.k
        }
        
    except Exception as e:
        logger.error(f"Error evaluating recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "model_loaded": recommender is not None}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

