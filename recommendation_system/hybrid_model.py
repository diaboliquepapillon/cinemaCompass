"""
Hybrid recommendation model combining content-based and collaborative filtering
"""

import pandas as pd
from typing import List, Dict, Optional
from .content_based import ContentBasedFilter
from .collaborative_filtering import CollaborativeFilter
from .adaptive_weights import AdaptiveWeightCalculator
from .cold_start import ColdStartHandler
from .explainability import ExplanationGenerator
import warnings
warnings.filterwarnings('ignore')


class HybridRecommender:
    """Hybrid recommendation system combining multiple approaches"""
    
    def __init__(self, 
                 content_weight: float = 0.5, 
                 collaborative_weight: float = 0.5,
                 use_adaptive_weights: bool = True):
        """
        Initialize hybrid recommender
        
        Args:
            content_weight: Default weight for content-based recommendations (0-1)
            collaborative_weight: Default weight for collaborative filtering (0-1)
            use_adaptive_weights: Whether to use adaptive weight calculation
        """
        assert abs(content_weight + collaborative_weight - 1.0) < 0.01, \
            "Weights must sum to 1.0"
        
        self.default_content_weight = content_weight
        self.default_collaborative_weight = collaborative_weight
        self.use_adaptive_weights = use_adaptive_weights
        
        self.content_filter = ContentBasedFilter()
        self.collaborative_filter = CollaborativeFilter(use_matrix_factorization=True)
        self.adaptive_weights = AdaptiveWeightCalculator(
            default_content_weight=content_weight,
            default_collaborative_weight=collaborative_weight
        )
        self.cold_start_handler = None
        self.explanation_generator = None
        
        self.movies_df = None
        self.ratings_df = None
        
    def fit(self, movies_df: pd.DataFrame, ratings_df: pd.DataFrame):
        """Fit both recommendation models"""
        self.movies_df = movies_df.copy()
        self.ratings_df = ratings_df.copy()
        
        # Fit content-based model
        self.content_filter.prepare_data(movies_df)
        
        # Fit collaborative filtering model
        self.collaborative_filter.prepare_data(ratings_df)
        
        # Initialize cold-start handler
        self.cold_start_handler = ColdStartHandler(movies_df, ratings_df)
        
        # Initialize explanation generator
        self.explanation_generator = ExplanationGenerator(movies_df, ratings_df)
        
        return self
    
    def get_recommendations(self, user_id: Optional[str] = None, 
                          liked_movies: Optional[List[str]] = None,
                          top_n: int = 10,
                          genre_preferences: Optional[List[str]] = None) -> List[Dict]:
        """
        Get hybrid recommendations with adaptive weighting
        
        Args:
            user_id: User ID for collaborative filtering (optional)
            liked_movies: List of movie IDs user liked (for content-based)
            top_n: Number of recommendations to return
            genre_preferences: List of genre preferences (for cold-start)
        """
        # Check for cold-start scenarios
        user_ratings_count = 0
        if user_id:
            user_ratings = self.ratings_df[self.ratings_df['user_id'] == user_id]
            user_ratings_count = len(user_ratings)
        
        # Cold-start: new user with no ratings
        if user_ratings_count == 0 and (not liked_movies or len(liked_movies) == 0):
            if self.cold_start_handler:
                return self.cold_start_handler.recommend_for_new_user(
                    genre_preferences=genre_preferences,
                    top_n=top_n
                )
        
        all_recommendations = {}
        
        # Calculate adaptive weights if enabled
        if self.use_adaptive_weights and user_id:
            weights = self.adaptive_weights.calculate_weights(
                user_id=user_id,
                user_ratings_count=user_ratings_count
            )
            content_weight = weights['content_weight']
            collaborative_weight = weights['collaborative_weight']
        else:
            content_weight = self.default_content_weight
            collaborative_weight = self.default_collaborative_weight
        
        # Get content-based recommendations
        if liked_movies and len(liked_movies) > 0:
            content_recs = self.content_filter.get_user_profile_recommendations(
                liked_movies, top_n=top_n*2
            )
            for rec in content_recs:
                movie_id = rec['movie_id']
                if movie_id not in all_recommendations:
                    all_recommendations[movie_id] = {
                        'movie_id': movie_id,
                        'title': rec['title'],
                        'content_score': 0.0,
                        'collaborative_score': 0.0,
                        'reasons': []
                    }
                all_recommendations[movie_id]['content_score'] = rec['score']
                all_recommendations[movie_id]['reasons'].append(rec['reason'])
        
        # Get collaborative filtering recommendations
        if user_id and user_ratings_count > 0:
            try:
                collab_recs = self.collaborative_filter.get_recommendations(
                    user_id, top_n=top_n*2, movies_df=self.movies_df
                )
                for rec in collab_recs:
                    movie_id = rec['movie_id']
                    if movie_id not in all_recommendations:
                        all_recommendations[movie_id] = {
                            'movie_id': movie_id,
                            'title': rec['title'],
                            'content_score': 0.0,
                            'collaborative_score': 0.0,
                            'reasons': []
                        }
                    all_recommendations[movie_id]['collaborative_score'] = rec['score']
                    all_recommendations[movie_id]['reasons'].append(rec['reason'])
            except (KeyError, IndexError):
                # User not in collaborative filtering matrix
                pass
        
        # If no recommendations from either method, try item-based or cold-start
        if len(all_recommendations) == 0:
            if liked_movies and len(liked_movies) > 0:
                for movie_id in liked_movies[:1]:
                    item_recs = self.collaborative_filter.get_item_based_recommendations(
                        movie_id, top_n=top_n, movies_df=self.movies_df
                    )
                    for rec in item_recs:
                        if rec['movie_id'] not in liked_movies:
                            if rec['movie_id'] not in all_recommendations:
                                all_recommendations[rec['movie_id']] = {
                                    'movie_id': rec['movie_id'],
                                    'title': rec['title'],
                                    'content_score': 0.0,
                                    'collaborative_score': rec['score'],
                                    'reasons': []
                                }
                            all_recommendations[rec['movie_id']]['reasons'].append(rec['reason'])
            elif self.cold_start_handler:
                # Fall back to cold-start
                return self.cold_start_handler.recommend_for_new_user(
                    genre_preferences=genre_preferences,
                    top_n=top_n
                )
        
        # Combine scores with adaptive weights
        for movie_id in all_recommendations:
            content_score = all_recommendations[movie_id]['content_score']
            collab_score = all_recommendations[movie_id]['collaborative_score']
            
            # Normalize scores to 0-1 range
            if content_score > 0:
                content_score = min(1.0, content_score)
            if collab_score > 0:
                collab_score = min(1.0, collab_score / 5.0)  # Ratings are 1-5
            
            # Weighted combination
            hybrid_score = (content_weight * content_score + 
                          collaborative_weight * collab_score)
            
            all_recommendations[movie_id]['hybrid_score'] = hybrid_score
        
        # Sort by hybrid score
        sorted_recs = sorted(
            all_recommendations.values(),
            key=lambda x: x['hybrid_score'],
            reverse=True
        )
        
        # Format final recommendations with enhanced explanations
        final_recs = []
        for rec in sorted_recs[:top_n]:
            # Generate detailed explanation
            if self.explanation_generator:
                main_reason = self.explanation_generator.generate_explanation(
                    movie_id=rec['movie_id'],
                    user_id=user_id,
                    liked_movies=liked_movies,
                    similarity_score=rec.get('hybrid_score'),
                    content_features={
                        'genres': rec.get('content_score', 0),
                        'director': rec.get('content_score', 0) * 0.8,
                        'cast': rec.get('content_score', 0) * 0.6
                    }
                )
            else:
                main_reason = self._generate_explanation(
                    rec['movie_id'],
                    liked_movies if liked_movies else [],
                    rec['reasons']
                )
            
            final_recs.append({
                'movie_id': rec['movie_id'],
                'title': rec['title'],
                'score': rec['hybrid_score'],
                'reason': main_reason
            })
        
        return final_recs
    
    def _generate_explanation(self, movie_id: str, liked_movies: List[str], 
                            reasons: List[str]) -> str:
        """Generate personalized explanation for recommendation"""
        if not liked_movies:
            return reasons[0] if reasons else "Recommended for you"
        
        # Find which liked movie this is most similar to
        movie_title = self.movies_df[
            self.movies_df['movie_id'] == movie_id
        ]['title'].values
        
        if len(movie_title) == 0:
            return reasons[0] if reasons else "Recommended for you"
        
        movie_title = movie_title[0]
        
        # Try to find the source movie
        if liked_movies:
            source_movie_info = self.movies_df[
                self.movies_df['movie_id'] == liked_movies[0]
            ]
            if not source_movie_info.empty:
                source_title = source_movie_info.iloc[0]['title']
                return f"Because you liked {source_title}, try {movie_title}"
        
        return reasons[0] if reasons else f"Recommended: {movie_title}"

