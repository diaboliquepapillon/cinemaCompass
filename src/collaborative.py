"""
Collaborative Filtering Module
Uses SVD (Singular Value Decomposition) for collaborative recommendations
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import warnings

# Try to import Surprise, fallback to simple implementation
try:
    from surprise import SVD, Dataset, Reader
    from surprise.model_selection import train_test_split
    from surprise import accuracy
    SURPRISE_AVAILABLE = True
except ImportError:
    SURPRISE_AVAILABLE = False
    warnings.warn("Surprise library not available. Using simplified collaborative filtering.")


class CollaborativeFilter:
    """Collaborative filtering recommender using SVD"""
    
    def __init__(self, n_factors: int = 100, n_epochs: int = 20):
        """
        Initialize collaborative filter
        
        Args:
            n_factors: Number of factors for SVD
            n_epochs: Number of training epochs
        """
        self.n_factors = n_factors
        self.n_epochs = n_epochs
        self.algo = None
        self.trainset = None
        self.user_mapping = {}
        self.item_mapping = {}
        self.inverse_user_mapping = {}
        self.inverse_item_mapping = {}
    
    def train(self, ratings_df: pd.DataFrame) -> 'CollaborativeFilter':
        """
        Train collaborative filtering model
        
        Args:
            ratings_df: DataFrame with columns ['userId', 'movieId', 'rating']
        
        Returns:
            Self for chaining
        """
        if not SURPRISE_AVAILABLE:
            raise ImportError("Surprise library required. Install with: pip install surprise")
        
        # Create mappings for user and item IDs
        unique_users = ratings_df['userId'].unique()
        unique_items = ratings_df['movieId'].unique()
        
        self.user_mapping = {uid: idx for idx, uid in enumerate(unique_users)}
        self.item_mapping = {mid: idx for idx, mid in enumerate(unique_items)}
        self.inverse_user_mapping = {idx: uid for uid, idx in self.user_mapping.items()}
        self.inverse_item_mapping = {idx: mid for mid, idx in self.item_mapping.items()}
        
        # Map IDs
        mapped_ratings = ratings_df.copy()
        mapped_ratings['userId'] = mapped_ratings['userId'].map(self.user_mapping)
        mapped_ratings['movieId'] = mapped_ratings['movieId'].map(self.item_mapping)
        
        # Remove NaN values (items/users not in mapping)
        mapped_ratings = mapped_ratings.dropna()
        
        # Prepare data for Surprise
        reader = Reader(rating_scale=(0.5, 5.0))
        data = Dataset.load_from_df(
            mapped_ratings[['userId', 'movieId', 'rating']],
            reader
        )
        
        # Split data
        trainset, testset = train_test_split(data, test_size=0.2, random_state=42)
        self.trainset = trainset
        
        # Train model
        self.algo = SVD(n_factors=self.n_factors, n_epochs=self.n_epochs, random_state=42)
        self.algo.fit(trainset)
        
        return self
    
    def predict(self, user_id: str, movie_id: str) -> float:
        """
        Predict rating for user-movie pair
        
        Args:
            user_id: User ID
            movie_id: Movie ID
        
        Returns:
            Predicted rating
        """
        if self.algo is None:
            raise ValueError("Model not trained. Call train() first.")
        
        # Map to internal IDs
        internal_user = self.user_mapping.get(user_id)
        internal_movie = self.item_mapping.get(movie_id)
        
        if internal_user is None or internal_movie is None:
            # Return average rating for unknown user/movie
            return 3.0
        
        # Predict
        prediction = self.algo.predict(internal_user, internal_movie)
        return prediction.est
    
    def get_recommendations(
        self,
        user_id: str,
        movie_ids: List[str],
        top_n: int = 10
    ) -> List[Dict]:
        """
        Get recommendations for a user
        
        Args:
            user_id: User ID
            movie_ids: List of all movie IDs to consider
            top_n: Number of recommendations
        
        Returns:
            List of recommendations with predicted ratings
        """
        if self.algo is None:
            raise ValueError("Model not trained. Call train() first.")
        
        predictions = []
        
        for movie_id in movie_ids:
            try:
                pred_rating = self.predict(user_id, movie_id)
                predictions.append({
                    'movie_id': movie_id,
                    'score': float(pred_rating),
                    'predicted_rating': float(pred_rating)
                })
            except Exception:
                continue
        
        # Sort by predicted rating
        predictions.sort(key=lambda x: x['score'], reverse=True)
        
        return predictions[:top_n]
    
    def evaluate(self, ratings_df: pd.DataFrame, test_size: float = 0.2) -> Dict:
        """
        Evaluate model performance
        
        Args:
            ratings_df: Ratings DataFrame
            test_size: Test set proportion
        
        Returns:
            Dictionary with RMSE, MAE metrics
        """
        if not SURPRISE_AVAILABLE:
            return {'rmse': None, 'mae': None}
        
        reader = Reader(rating_scale=(0.5, 5.0))
        
        # Map IDs
        mapped_ratings = ratings_df.copy()
        mapped_ratings['userId'] = mapped_ratings['userId'].map(self.user_mapping)
        mapped_ratings['movieId'] = mapped_ratings['movieId'].map(self.item_mapping)
        mapped_ratings = mapped_ratings.dropna()
        
        data = Dataset.load_from_df(
            mapped_ratings[['userId', 'movieId', 'rating']],
            reader
        )
        
        trainset, testset = train_test_split(data, test_size=test_size, random_state=42)
        
        # Train
        algo = SVD(n_factors=self.n_factors, n_epochs=self.n_epochs, random_state=42)
        algo.fit(trainset)
        
        # Test
        predictions = algo.test(testset)
        
        rmse = accuracy.rmse(predictions, verbose=False)
        mae = accuracy.mae(predictions, verbose=False)
        
        return {'rmse': rmse, 'mae': mae}


def train_collaborative_model(ratings_df: pd.DataFrame, n_factors: int = 100) -> CollaborativeFilter:
    """
    Convenience function to train collaborative model
    
    Args:
        ratings_df: DataFrame with ['userId', 'movieId', 'rating']
        n_factors: Number of SVD factors
    
    Returns:
        Trained CollaborativeFilter
    """
    cf = CollaborativeFilter(n_factors=n_factors)
    cf.train(ratings_df)
    return cf

