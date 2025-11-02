"""
Hybrid recommendation system combining content-based and collaborative filtering
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from .content_based import ContentBasedRecommender
from .collaborative_filtering import CollaborativeFilter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HybridRecommender:
    """Hybrid recommender combining content-based and collaborative filtering"""
    
    def __init__(
        self,
        content_weight: float = 0.5,
        collaborative_weight: float = 0.5
    ):
        """
        Initialize hybrid recommender
        
        Args:
            content_weight: Weight for content-based recommendations (0-1)
            collaborative_weight: Weight for collaborative filtering (0-1)
        """
        assert abs(content_weight + collaborative_weight - 1.0) < 0.01, \
            "Weights must sum to 1.0"
        
        self.content_weight = content_weight
        self.collaborative_weight = collaborative_weight
        
        self.content_recommender = ContentBasedRecommender()
        self.collaborative_filter = CollaborativeFilter()
        
        self.movies_df = None
        self.ratings_df = None
        
    def fit(
        self,
        movies_df: pd.DataFrame,
        ratings_df: pd.DataFrame
    ):
        """Fit both recommendation models"""
        self.movies_df = movies_df.copy()
        self.ratings_df = ratings_df.copy()
        
        logger.info("Fitting content-based model...")
        self.content_recommender.fit(movies_df)
        
        logger.info("Fitting collaborative filtering model...")
        self.collaborative_filter.fit(ratings_df)
        
        logger.info("Hybrid model fitted successfully.")
        return self
    
    def get_recommendations(
        self,
        user_id: Optional[str] = None,
        liked_movie_ids: Optional[List[str]] = None,
        top_n: int = 10,
        explain: bool = True
    ) -> List[Dict]:
        """
        Get hybrid recommendations combining both approaches
        
        Args:
            user_id: User ID for collaborative filtering
            liked_movie_ids: List of movie IDs user liked
            top_n: Number of recommendations
            explain: Whether to include personalized explanations
            
        Returns:
            List of recommendation dictionaries with personalized explanations
        """
        if liked_movie_ids is None or len(liked_movie_ids) == 0:
            # No liked movies - use collaborative only or popular movies
            if user_id:
                all_movie_ids = self.movies_df['id'].tolist()
                collab_recs = self.collaborative_filter.get_recommendations(
                    user_id, all_movie_ids, top_n
                )
                return collab_recs
            else:
                # Fallback to popular movies
                popular = self.movies_df.nlargest(top_n, 'vote_average')
                return [{
                    'movie_id': row['id'],
                    'title': row['title'],
                    'score': row['vote_average'],
                    'reason': 'Popular highly-rated movie'
                } for _, row in popular.iterrows()]
        
        # Get content-based recommendations
        content_recs = self.content_recommender.get_recommendations_from_multiple(
            liked_movie_ids,
            top_n=top_n * 2  # Get more to blend
        )
        
        # Get collaborative recommendations
        if user_id:
            all_movie_ids = self.movies_df['id'].tolist()
            collab_recs = self.collaborative_filter.get_user_similar_movies(
                user_id,
                liked_movie_ids,
                all_movie_ids,
                top_n=top_n * 2
            )
        else:
            # No user ID - use content-based only
            collab_recs = []
        
        # Combine recommendations with weighted scores
        combined_scores = {}
        
        # Add content-based scores
        for rec in content_recs:
            movie_id = rec['movie_id']
            score = rec['similarity_score']
            combined_scores[movie_id] = {
                'movie_id': movie_id,
                'content_score': score,
                'collaborative_score': 0.0,
                'hybrid_score': score * self.content_weight,
                'title': rec['title'],
                'genres': rec.get('genres'),
                'poster_path': rec.get('poster_path'),
                'vote_average': rec.get('vote_average', 0)
            }
        
        # Add collaborative scores
        for rec in collab_recs:
            movie_id = rec['movie_id']
            score = rec['predicted_rating'] / 5.0  # Normalize to 0-1
            
            if movie_id in combined_scores:
                combined_scores[movie_id]['collaborative_score'] = score
                combined_scores[movie_id]['hybrid_score'] += score * self.collaborative_weight
            else:
                # Get movie info
                movie_info = self.movies_df[self.movies_df['id'] == movie_id]
                if len(movie_info) > 0:
                    movie = movie_info.iloc[0]
                    combined_scores[movie_id] = {
                        'movie_id': movie_id,
                        'content_score': 0.0,
                        'collaborative_score': score,
                        'hybrid_score': score * self.collaborative_weight,
                        'title': movie.get('title'),
                        'genres': movie.get('genres'),
                        'poster_path': movie.get('poster_path'),
                        'vote_average': movie.get('vote_average', 0)
                    }
        
        # Sort by hybrid score
        sorted_recs = sorted(
            combined_scores.values(),
            key=lambda x: x['hybrid_score'],
            reverse=True
        )[:top_n]
        
        # Format final recommendations with personalized explanations
        final_recommendations = []
        for rec in sorted_recs:
            # Generate personalized explanation
            if explain and liked_movie_ids:
                # Find the most similar liked movie
                liked_movie = self.movies_df[self.movies_df['id'] == liked_movie_ids[0]].iloc[0]
                liked_title = liked_movie.get('title', 'that movie')
                
                if rec['content_score'] > rec['collaborative_score']:
                    reason = f"Because you liked {liked_title}, you might enjoy {rec['title']} - they share similar genres, cast, and storyline."
                elif rec['collaborative_score'] > 0:
                    reason = f"Because you liked {liked_title}, try {rec['title']} - users with similar taste loved it!"
                else:
                    reason = f"Recommended based on your preference for {liked_title}."
            else:
                reason = "Personalized recommendation for you"
            
            final_recommendations.append({
                'movie_id': rec['movie_id'],
                'title': rec['title'],
                'score': rec['hybrid_score'],
                'genres': rec.get('genres'),
                'poster_path': rec.get('poster_path'),
                'vote_average': rec.get('vote_average', 0),
                'reason': reason
            })
        
        return final_recommendations

