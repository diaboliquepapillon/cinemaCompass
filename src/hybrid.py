"""
Hybrid Recommendation System
Combines content-based and collaborative filtering
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
try:
    from .content_based import ContentBasedRecommender, get_content_recommendations
    from .collaborative import CollaborativeFilter
except ImportError:
    # Fallback for direct imports
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from src.content_based import ContentBasedRecommender, get_content_recommendations
    from src.collaborative import CollaborativeFilter


class HybridRecommender:
    """Hybrid recommender combining content-based and collaborative filtering"""
    
    def __init__(
        self,
        content_recommender: Optional[ContentBasedRecommender] = None,
        collaborative_filter: Optional[CollaborativeFilter] = None,
        default_alpha: float = 0.5
    ):
        """
        Initialize hybrid recommender
        
        Args:
            content_recommender: Content-based recommender instance
            collaborative_filter: Collaborative filter instance
            default_alpha: Default weight for collaborative (1-alpha for content)
        """
        self.content_recommender = content_recommender
        self.collaborative_filter = collaborative_filter
        self.default_alpha = default_alpha
        self.movies_df = None
    
    def get_recommendations(
        self,
        user_id: str,
        liked_movies: List[str],
        movies_df: pd.DataFrame,
        top_n: int = 10,
        alpha: Optional[float] = None
    ) -> List[Dict]:
        """
        Get hybrid recommendations
        
        Args:
            user_id: User ID
            liked_movies: List of movie IDs the user likes
            movies_df: Movies dataframe
            top_n: Number of recommendations
            alpha: Weight for collaborative filtering (0-1, default uses self.default_alpha)
        
        Returns:
            List of recommendations
        """
        if alpha is None:
            alpha = self.default_alpha
        
        self.movies_df = movies_df
        
        # Get content-based recommendations
        content_recs = []
        if self.content_recommender and liked_movies:
            content_recs = self.content_recommender.get_recommendations_from_ids(
                liked_movies,
                top_n=top_n * 3  # Get more candidates
            )
        
        # Get all movie IDs
        all_movie_ids = movies_df['movie_id'].tolist()
        
        # Get collaborative scores
        collab_scores = {}
        if self.collaborative_filter:
            try:
                collab_recs = self.collaborative_filter.get_recommendations(
                    user_id,
                    all_movie_ids,
                    top_n=len(all_movie_ids)
                )
                collab_scores = {r['movie_id']: r['score'] for r in collab_recs}
            except Exception:
                collab_scores = {}
        
        # Normalize collaborative scores to 0-1 range
        if collab_scores:
            max_collab = max(collab_scores.values()) if collab_scores.values() else 1.0
            min_collab = min(collab_scores.values()) if collab_scores.values() else 0.0
            if max_collab > min_collab:
                collab_scores = {
                    mid: (score - min_collab) / (max_collab - min_collab)
                    for mid, score in collab_scores.items()
                }
        
        # Combine scores
        final_scores = {}
        
        # Add content-based scores
        for rec in content_recs:
            movie_id = rec['movie_id']
            content_score = rec.get('score', 0.0)
            collab_score = collab_scores.get(movie_id, 0.5)  # Default to 0.5 if no collab score
            
            # Hybrid score: weighted combination
            hybrid_score = alpha * collab_score + (1 - alpha) * content_score
            final_scores[movie_id] = {
                'movie_id': movie_id,
                'title': rec.get('title', ''),
                'score': hybrid_score,
                'content_score': content_score,
                'collab_score': collab_score,
                'reason': rec.get('reason', 'Recommended for you'),
                'genres': rec.get('genres', '')
            }
        
        # If we have collaborative scores but no content matches, use collab only
        if not final_scores and collab_scores:
            for movie_id, collab_score in list(collab_scores.items())[:top_n * 2]:
                movie = movies_df[movies_df['movie_id'] == movie_id]
                if len(movie) > 0:
                    movie = movie.iloc[0]
                    final_scores[movie_id] = {
                        'movie_id': movie_id,
                        'title': movie.get('title', ''),
                        'score': collab_score,
                        'content_score': 0.0,
                        'collab_score': collab_score,
                        'reason': 'Popular among similar users',
                        'genres': movie.get('genres', '')
                    }
        
        # Sort and return top N
        sorted_recs = sorted(final_scores.values(), key=lambda x: x['score'], reverse=True)
        
        return sorted_recs[:top_n]


def hybrid_recommend(
    user_id: str,
    title: str,
    movies: pd.DataFrame,
    ratings_df: pd.DataFrame,
    algo: Optional[CollaborativeFilter],
    similarity: Optional[np.ndarray],
    alpha: float = 0.5,
    top_n: int = 10
) -> List[tuple]:
    """
    Get hybrid recommendations (legacy function for compatibility)
    
    Args:
        user_id: User ID
        title: Movie title
        movies: Movies dataframe
        ratings_df: Ratings dataframe
        algo: Collaborative filter algorithm
        similarity: Content similarity matrix
        alpha: Weight for collaborative (0-1)
        top_n: Number of recommendations
    
    Returns:
        List of (title, score) tuples
    """
    # Get content recommendations
    content_recs = get_content_recommendations(title, movies, similarity, 20)
    
    # Get collaborative scores
    collab_scores = {}
    if algo:
        try:
            for _, row in movies.iterrows():
                movie_id = row['movie_id']
                try:
                    pred = algo.predict(user_id, movie_id)
                    collab_scores[row['title']] = pred if isinstance(pred, float) else pred.est
                except Exception:
                    collab_scores[row['title']] = 3.0  # Default rating
        except Exception:
            pass
    
    # Combine scores
    final = []
    for _, row in content_recs.iterrows():
        title = row['title']
        content_score = 1.0  # Simplified: assume content similarity is normalized
        
        collab_score = collab_scores.get(title, 3.0)
        # Normalize collaborative score to 0-1
        collab_norm = (collab_score - 0.5) / 4.5  # Map 0.5-5.0 to 0-1
        
        score = alpha * collab_norm + (1 - alpha) * content_score
        final.append((title, score))
    
    # Sort and return
    final = sorted(final, key=lambda x: x[1], reverse=True)
    return final[:top_n]

