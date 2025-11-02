"""
Collaborative filtering using matrix factorization (SVD)
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from surprise import SVD, Dataset, Reader
from surprise.model_selection import train_test_split
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CollaborativeFilter:
    """Collaborative filtering using SVD matrix factorization"""
    
    def __init__(self, n_factors: int = 50, n_epochs: int = 20):
        self.n_factors = n_factors
        self.n_epochs = n_epochs
        self.algo = None
        self.trainset = None
        self.ratings_df = None
        self.user_item_matrix = None
        
    def fit(self, ratings_df: pd.DataFrame):
        """Fit the collaborative filtering model"""
        self.ratings_df = ratings_df.copy()
        
        # Check required columns
        required_cols = ['user_id', 'movie_id', 'rating']
        missing_cols = [col for col in required_cols if col not in ratings_df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Prepare data for Surprise
        reader = Reader(rating_scale=(0.5, 5.0))
        
        # Map user_id and movie_id to integers if they're not already
        if not pd.api.types.is_integer_dtype(ratings_df['user_id']):
            self.user_id_map = {uid: idx for idx, uid in enumerate(ratings_df['user_id'].unique())}
            ratings_df_mapped = ratings_df.copy()
            ratings_df_mapped['user_id'] = ratings_df_mapped['user_id'].map(self.user_id_map)
            self.user_id_reverse_map = {v: k for k, v in self.user_id_map.items()}
        else:
            self.user_id_map = None
            self.user_id_reverse_map = None
        
        if not pd.api.types.is_integer_dtype(ratings_df['movie_id']):
            self.movie_id_map = {mid: idx for idx, mid in enumerate(ratings_df['movie_id'].unique())}
            ratings_df_mapped['movie_id'] = ratings_df_mapped['movie_id'].map(self.movie_id_map)
            self.movie_id_reverse_map = {v: k for k, v in self.movie_id_map.items()}
        else:
            self.movie_id_map = None
            self.movie_id_reverse_map = None
        
        # Load data
        data = Dataset.load_from_df(
            ratings_df_mapped[['user_id', 'movie_id', 'rating']],
            reader
        )
        
        # Split and train
        self.trainset, _ = train_test_split(data, test_size=0.2, random_state=42)
        
        logger.info("Training SVD model...")
        self.algo = SVD(n_factors=n_factors, n_epochs=n_epochs, random_state=42)
        self.algo.fit(self.trainset)
        
        logger.info("Collaborative filtering model fitted successfully.")
        return self
    
    def predict_rating(self, user_id: str, movie_id: str) -> float:
        """Predict rating for a user-movie pair"""
        if self.algo is None:
            raise ValueError("Model must be fitted first. Call fit() before predict_rating()")
        
        # Map IDs if necessary
        uid = self.user_id_map.get(user_id, user_id) if self.user_id_map else user_id
        mid = self.movie_id_map.get(movie_id, movie_id) if self.movie_id_map else movie_id
        
        # Check if user or item is in trainset
        if uid not in self.trainset.all_users() or mid not in self.trainset.all_items():
            # Return average rating as fallback
            return 3.0
        
        try:
            prediction = self.algo.predict(uid, mid)
            return max(0.5, min(5.0, prediction.est))
        except:
            return 3.0  # Default rating
    
    def get_recommendations(
        self,
        user_id: str,
        all_movie_ids: List[str],
        top_n: int = 10
    ) -> List[Dict]:
        """Get top N recommendations for a user"""
        if self.algo is None:
            raise ValueError("Model must be fitted first. Call fit() before get_recommendations()")
        
        # Get predictions for all movies
        predictions = []
        for movie_id in all_movie_ids:
            rating = self.predict_rating(user_id, movie_id)
            predictions.append({
                'movie_id': movie_id,
                'predicted_rating': rating
            })
        
        # Sort by predicted rating
        predictions.sort(key=lambda x: x['predicted_rating'], reverse=True)
        
        # Format results
        recommendations = []
        for pred in predictions[:top_n]:
            recommendations.append({
                'movie_id': pred['movie_id'],
                'predicted_rating': pred['predicted_rating'],
                'reason': f"Users with similar taste rated this highly"
            })
        
        return recommendations
    
    def get_user_similar_movies(
        self,
        user_id: str,
        liked_movie_ids: List[str],
        all_movie_ids: List[str],
        top_n: int = 10
    ) -> List[Dict]:
        """Get recommendations based on movies liked by similar users"""
        # Find users who liked the same movies
        similar_users = set()
        
        for movie_id in liked_movie_ids:
            movie_ratings = self.ratings_df[self.ratings_df['movie_id'] == movie_id]
            # Get users who rated this movie highly (>= 4.0)
            high_raters = movie_ratings[movie_ratings['rating'] >= 4.0]['user_id'].unique()
            similar_users.update(high_raters)
        
        # Remove the current user if present
        if user_id in similar_users:
            similar_users.remove(user_id)
        
        if not similar_users:
            # Fallback to general recommendations
            return self.get_recommendations(user_id, all_movie_ids, top_n)
        
        # Get movies that similar users liked (that current user hasn't seen)
        similar_users_list = list(similar_users)
        similar_users_ratings = self.ratings_df[
            (self.ratings_df['user_id'].isin(similar_users_list)) &
            (~self.ratings_df['movie_id'].isin(liked_movie_ids))
        ]
        
        # Aggregate by movie
        movie_scores = similar_users_ratings.groupby('movie_id').agg({
            'rating': ['mean', 'count']
        }).reset_index()
        movie_scores.columns = ['movie_id', 'avg_rating', 'num_ratings']
        
        # Sort by weighted score (average rating * log of number of ratings)
        movie_scores['weighted_score'] = (
            movie_scores['avg_rating'] * 
            np.log1p(movie_scores['num_ratings'])
        )
        movie_scores = movie_scores.sort_values('weighted_score', ascending=False)
        
        # Format results
        recommendations = []
        for _, row in movie_scores.head(top_n).iterrows():
            recommendations.append({
                'movie_id': row['movie_id'],
                'predicted_rating': float(row['avg_rating']),
                'reason': f"Users with similar taste to you loved this movie"
            })
        
        return recommendations

