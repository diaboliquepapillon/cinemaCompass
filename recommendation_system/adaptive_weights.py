"""
Adaptive weight calculation for hybrid recommendation model
Dynamically adjusts content vs collaborative weights based on user/item characteristics
"""

import numpy as np
import pandas as pd
from typing import Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AdaptiveWeightCalculator:
    """Calculate adaptive weights for hybrid recommendation"""
    
    def __init__(self, 
                 default_content_weight: float = 0.5,
                 default_collaborative_weight: float = 0.5):
        """
        Initialize adaptive weight calculator
        
        Args:
            default_content_weight: Default weight for content-based filtering
            default_collaborative_weight: Default weight for collaborative filtering
        """
        self.default_content_weight = default_content_weight
        self.default_collaborative_weight = default_collaborative_weight
    
    def calculate_weights(self,
                          user_id: Optional[str] = None,
                          movie_id: Optional[str] = None,
                          user_ratings_count: Optional[int] = None,
                          movie_ratings_count: Optional[int] = None,
                          data_sparsity: Optional[float] = None) -> Dict[str, float]:
        """
        Calculate adaptive weights based on context
        
        Args:
            user_id: User identifier
            movie_id: Movie identifier
            user_ratings_count: Number of ratings by user
            movie_ratings_count: Number of ratings for movie
            data_sparsity: Overall sparsity of rating matrix
        
        Returns:
            Dict with 'content_weight' and 'collaborative_weight'
        """
        content_weight = self.default_content_weight
        collaborative_weight = self.default_collaborative_weight
        
        # Adjust based on user interaction history
        if user_ratings_count is not None:
            if user_ratings_count < 5:
                # New user: favor content-based (more reliable)
                content_weight = 0.7
                collaborative_weight = 0.3
            elif user_ratings_count < 20:
                # Moderate user: balanced
                content_weight = 0.5
                collaborative_weight = 0.5
            else:
                # Established user: favor collaborative (more personalized)
                content_weight = 0.3
                collaborative_weight = 0.7
        
        # Adjust based on item popularity
        if movie_ratings_count is not None:
            if movie_ratings_count < 10:
                # Long-tail item: favor content-based
                content_weight = max(content_weight, 0.6)
                collaborative_weight = min(collaborative_weight, 0.4)
            elif movie_ratings_count > 100:
                # Popular item: collaborative is reliable
                collaborative_weight = max(collaborative_weight, 0.6)
                content_weight = min(content_weight, 0.4)
        
        # Adjust based on data sparsity
        if data_sparsity is not None:
            if data_sparsity > 0.95:  # Very sparse
                # Favor content-based when data is sparse
                content_weight = max(content_weight, 0.6)
                collaborative_weight = min(collaborative_weight, 0.4)
            elif data_sparsity < 0.8:  # Dense
                # Collaborative works well with dense data
                collaborative_weight = max(collaborative_weight, 0.6)
                content_weight = min(content_weight, 0.4)
        
        # Normalize to sum to 1.0
        total = content_weight + collaborative_weight
        if total > 0:
            content_weight /= total
            collaborative_weight /= total
        
        return {
            'content_weight': content_weight,
            'collaborative_weight': collaborative_weight
        }
    
    def calculate_time_decay_weights(self,
                                     user_id: str,
                                     ratings_df: pd.DataFrame,
                                     decay_factor: float = 0.95) -> Dict[str, float]:
        """
        Calculate weights with time decay (recent interactions weighted higher)
        
        Args:
            user_id: User identifier
            ratings_df: Ratings dataframe with timestamp column
            decay_factor: Decay factor per time period
        
        Returns:
            Dict with adjusted weights
        """
        base_weights = self.calculate_weights(user_id=user_id)
        
        # Check if user has recent ratings
        user_ratings = ratings_df[ratings_df['user_id'] == user_id]
        
        if len(user_ratings) == 0 or 'timestamp' not in user_ratings.columns:
            return base_weights
        
        # Calculate time decay
        if pd.api.types.is_datetime64_any_dtype(user_ratings['timestamp']):
            now = pd.Timestamp.now()
            user_ratings = user_ratings.copy()
            user_ratings['days_ago'] = (now - user_ratings['timestamp']).dt.days
            
            # Recent ratings (last 30 days) get higher weight for collaborative
            recent_ratings = user_ratings[user_ratings['days_ago'] <= 30]
            recent_ratio = len(recent_ratings) / len(user_ratings) if len(user_ratings) > 0 else 0
            
            if recent_ratio > 0.5:
                # User has been active recently: collaborative filtering works well
                collaborative_weight = base_weights['collaborative_weight'] * (1 + recent_ratio * 0.3)
                content_weight = base_weights['content_weight'] * (1 - recent_ratio * 0.3)
                
                # Normalize
                total = content_weight + collaborative_weight
                return {
                    'content_weight': content_weight / total,
                    'collaborative_weight': collaborative_weight / total
                }
        
        return base_weights

