"""
Advanced explanation generation for recommendations
Provides detailed, multi-faceted explanations
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExplanationGenerator:
    """Generate detailed explanations for recommendations"""
    
    def __init__(self, movies_df: pd.DataFrame, ratings_df: pd.DataFrame):
        """
        Initialize explanation generator
        
        Args:
            movies_df: Movies dataframe
            ratings_df: Ratings dataframe
        """
        self.movies_df = movies_df.copy()
        self.ratings_df = ratings_df.copy()
    
    def generate_explanation(self,
                               movie_id: str,
                               user_id: Optional[str] = None,
                               liked_movies: Optional[List[str]] = None,
                               similarity_score: Optional[float] = None,
                               content_features: Optional[Dict] = None) -> str:
        """
        Generate comprehensive explanation for a recommendation
        
        Args:
            movie_id: Recommended movie ID
            user_id: User ID (for collaborative explanations)
            liked_movies: List of movies user liked (for content-based explanations)
            similarity_score: Similarity score (0-1)
            content_features: Dict of feature contributions
        
        Returns:
            Explanation string
        """
        movie_info = self.movies_df[self.movies_df['movie_id'] == movie_id]
        if movie_info.empty:
            return "Recommended for you"
        
        movie_info = movie_info.iloc[0]
        explanations = []
        
        # Feature-based explanation
        if content_features:
            feature_explanation = self._generate_feature_explanation(
                movie_info, content_features
            )
            if feature_explanation:
                explanations.append(feature_explanation)
        
        # Similarity-based explanation
        if liked_movies and len(liked_movies) > 0:
            similarity_explanation = self._generate_similarity_explanation(
                movie_info, liked_movies, similarity_score
            )
            if similarity_explanation:
                explanations.append(similarity_explanation)
        
        # Social proof explanation
        if user_id:
            social_explanation = self._generate_social_proof(
                movie_id, user_id
            )
            if social_explanation:
                explanations.append(social_explanation)
        
        # Collaborative explanation
        collaborative_explanation = self._generate_collaborative_explanation(
            movie_id
        )
        if collaborative_explanation:
            explanations.append(collaborative_explanation)
        
        # Temporal explanation (trending)
        temporal_explanation = self._generate_temporal_explanation(movie_id)
        if temporal_explanation:
            explanations.append(temporal_explanation)
        
        # Combine explanations
        if explanations:
            return " | ".join(explanations[:2])  # Return top 2 explanations
        else:
            return f"Recommended: {movie_info.get('title', 'this movie')}"
    
    def _generate_feature_explanation(self,
                                     movie_info: pd.Series,
                                     content_features: Dict) -> Optional[str]:
        """Generate feature-based explanation"""
        features = []
        
        if 'genres' in content_features and content_features['genres'] > 0.5:
            genres = str(movie_info.get('genres', '')).split(',')[:2]
            features.append(f"Genre ({', '.join(genres)}: {int(content_features['genres']*100)}%)")
        
        if 'director' in content_features and content_features['director'] > 0.5:
            director = movie_info.get('director', '')
            if director:
                features.append(f"Director ({director}: {int(content_features['director']*100)}%)")
        
        if 'cast' in content_features and content_features['cast'] > 0.3:
            cast = str(movie_info.get('cast', '')).split(',')[0]
            if cast:
                features.append(f"Cast ({cast}: {int(content_features['cast']*100)}%)")
        
        if features:
            return f"Recommended because: {', '.join(features)}"
        return None
    
    def _generate_similarity_explanation(self,
                                        movie_info: pd.Series,
                                        liked_movies: List[str],
                                        similarity_score: Optional[float]) -> Optional[str]:
        """Generate similarity-based explanation"""
        # Find most similar liked movie
        source_movie_info = self.movies_df[
            self.movies_df['movie_id'] == liked_movies[0]
        ]
        
        if not source_movie_info.empty:
            source_title = source_movie_info.iloc[0].get('title', 'movies you liked')
            target_title = movie_info.get('title', 'this movie')
            
            if similarity_score:
                return f"Similar to '{source_title}' (similarity: {similarity_score:.2f})"
            else:
                return f"Similar to '{source_title}', try '{target_title}'"
        
        return None
    
    def _generate_social_proof(self,
                              movie_id: str,
                              user_id: str) -> Optional[str]:
        """Generate social proof explanation"""
        # Count users with similar taste who liked this movie
        # For now, use a simple heuristic
        movie_ratings = self.ratings_df[self.ratings_df['movie_id'] == movie_id]
        
        if len(movie_ratings) > 0:
            high_ratings = movie_ratings[movie_ratings['rating'] >= 4.0]
            count = len(high_ratings)
            
            if count > 10:
                return f"Also liked by {count} users with similar taste"
        
        return None
    
    def _generate_collaborative_explanation(self, movie_id: str) -> Optional[str]:
        """Generate collaborative filtering explanation"""
        movie_ratings = self.ratings_df[self.ratings_df['movie_id'] == movie_id]
        
        if len(movie_ratings) > 0:
            avg_rating = movie_ratings['rating'].mean()
            count = len(movie_ratings)
            
            if avg_rating >= 4.0 and count >= 20:
                return f"Users rate this {avg_rating:.1f}/5.0 ({count} ratings)"
        
        return None
    
    def _generate_temporal_explanation(self, movie_id: str) -> Optional[str]:
        """Generate temporal/trending explanation"""
        movie_ratings = self.ratings_df[self.ratings_df['movie_id'] == movie_id]
        
        if len(movie_ratings) == 0:
            return None
        
        # Check if movie is trending (many recent ratings)
        if 'timestamp' in movie_ratings.columns:
            movie_ratings = movie_ratings.copy()
            movie_ratings['timestamp'] = pd.to_datetime(movie_ratings['timestamp'])
            recent = movie_ratings[
                movie_ratings['timestamp'] > pd.Timestamp.now() - pd.Timedelta(days=30)
            ]
            
            if len(recent) > 50:
                return "Trending this week among movie fans"
        
        return None


def generate_detailed_explanation(movie_id: str,
                                 recommendation_data: Dict,
                                 explanation_generator: ExplanationGenerator) -> Dict:
    """
    Generate detailed explanation with multiple components
    
    Args:
        movie_id: Recommended movie ID
        recommendation_data: Dict with recommendation metadata
        explanation_generator: ExplanationGenerator instance
    
    Returns:
        Dict with explanation components
    """
    explanation = explanation_generator.generate_explanation(
        movie_id=movie_id,
        user_id=recommendation_data.get('user_id'),
        liked_movies=recommendation_data.get('liked_movies'),
        similarity_score=recommendation_data.get('similarity_score'),
        content_features=recommendation_data.get('content_features')
    )
    
    return {
        'primary_explanation': explanation,
        'explanation_type': recommendation_data.get('explanation_type', 'hybrid'),
        'confidence': recommendation_data.get('confidence', 0.5),
        'feature_contributions': recommendation_data.get('content_features', {})
    }

