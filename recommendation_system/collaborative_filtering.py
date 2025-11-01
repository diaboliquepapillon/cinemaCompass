"""
Collaborative filtering recommendation system
Enhanced with matrix factorization
"""

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple, Optional
from .matrix_factorization import MatrixFactorization
import logging
import warnings
warnings.filterwarnings('ignore')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CollaborativeFilter:
    """Collaborative filtering using user-item matrix and matrix factorization"""
    
    def __init__(self, use_matrix_factorization: bool = True, n_factors: int = 50):
        """
        Initialize collaborative filter
        
        Args:
            use_matrix_factorization: Whether to use matrix factorization (recommended)
            n_factors: Number of latent factors for matrix factorization
        """
        self.use_matrix_factorization = use_matrix_factorization
        self.mf_model = None
        self.ratings_df = None
        self.user_item_matrix = None
        self.user_similarity = None
        self.item_similarity = None
        
        if use_matrix_factorization:
            self.mf_model = MatrixFactorization(n_factors=n_factors)
        
    def prepare_data(self, ratings_df: pd.DataFrame):
        """Prepare ratings data and compute similarity matrices"""
        self.ratings_df = ratings_df.copy()
        
        # Create user-item matrix
        self.user_item_matrix = ratings_df.pivot_table(
            index='user_id',
            columns='movie_id',
            values='rating',
            fill_value=0
        )
        
        # Fit matrix factorization if enabled
        if self.use_matrix_factorization and self.mf_model:
            logger.info("Fitting matrix factorization model...")
            self.mf_model.fit(ratings_df)
        
        # Compute user-user similarity (fallback for cold-start)
        self.user_similarity = cosine_similarity(self.user_item_matrix)
        self.user_similarity = pd.DataFrame(
            self.user_similarity,
            index=self.user_item_matrix.index,
            columns=self.user_item_matrix.index
        )
        
        # Compute item-item similarity
        item_item_matrix = self.user_item_matrix.T
        item_sim_matrix = cosine_similarity(item_item_matrix)
        self.item_similarity = pd.DataFrame(
            item_sim_matrix,
            index=item_item_matrix.index,
            columns=item_item_matrix.index
        )
        
        return self
    
    def predict_rating(self, user_id: str, movie_id: str) -> float:
        """Predict rating for a user-movie pair"""
        # Use matrix factorization if available and user/movie are known
        if self.mf_model:
            try:
                prediction = self.mf_model.predict(user_id, movie_id)
                if prediction > 0:
                    return float(prediction)
            except:
                pass  # Fall back to similarity-based
        
        # Fallback to similarity-based prediction
        if user_id not in self.user_item_matrix.index:
            return 0.0
        
        if movie_id not in self.user_item_matrix.columns:
            return 0.0
        
        # Get user's mean rating
        user_ratings = self.user_item_matrix.loc[user_id]
        user_mean = user_ratings[user_ratings > 0].mean()
        if pd.isna(user_mean):
            user_mean = 0.0
        
        # Find similar users who rated this movie
        user_idx = self.user_item_matrix.index.get_loc(user_id)
        similar_users = self.user_similarity.iloc[user_idx].sort_values(ascending=False)
        
        # Get top similar users who rated this movie
        prediction = 0.0
        similarity_sum = 0.0
        
        for similar_user_id, similarity in similar_users.items():
            if similar_user_id == user_id:
                continue
            
            rating = self.user_item_matrix.loc[similar_user_id, movie_id]
            if rating > 0:
                similar_user_ratings = self.user_item_matrix.loc[similar_user_id]
                similar_user_mean = similar_user_ratings[similar_user_ratings > 0].mean()
                if pd.isna(similar_user_mean):
                    similar_user_mean = 0.0
                
                prediction += similarity * (rating - similar_user_mean)
                similarity_sum += abs(similarity)
        
        if similarity_sum > 0:
            prediction = user_mean + (prediction / similarity_sum)
        else:
            prediction = user_mean
        
        return max(0.0, min(5.0, prediction))
    
    def get_recommendations(self, user_id: str, top_n: int = 10, movies_df: pd.DataFrame = None) -> List[Dict]:
        """Get collaborative filtering recommendations for a user"""
        if user_id not in self.user_item_matrix.index:
            return []
        
        # Get movies user hasn't rated
        user_ratings = self.user_item_matrix.loc[user_id]
        unrated_movies = user_ratings[user_ratings == 0].index.tolist()
        
        # Predict ratings for unrated movies
        predictions = []
        for movie_id in unrated_movies:
            predicted_rating = self.predict_rating(user_id, movie_id)
            if predicted_rating > 0:
                predictions.append({
                    'movie_id': movie_id,
                    'predicted_rating': predicted_rating
                })
        
        # Sort by predicted rating
        predictions.sort(key=lambda x: x['predicted_rating'], reverse=True)
        
        # Get top N
        recommendations = []
        for pred in predictions[:top_n]:
            movie_data = {'movie_id': pred['movie_id']}
            if movies_df is not None:
                movie_info = movies_df[movies_df['movie_id'] == pred['movie_id']]
                if not movie_info.empty:
                    movie_data['title'] = movie_info.iloc[0].get('title', '')
            
            recommendations.append({
                'movie_id': pred['movie_id'],
                'title': movie_data.get('title', pred['movie_id']),
                'score': pred['predicted_rating'],
                'reason': "Liked by users with similar taste"
            })
        
        return recommendations
    
    def get_item_based_recommendations(self, movie_id: str, top_n: int = 10, movies_df: pd.DataFrame = None) -> List[Dict]:
        """Get recommendations based on item similarity"""
        if movie_id not in self.item_similarity.index:
            return []
        
        # Get similar movies
        similar_movies = self.item_similarity[movie_id].sort_values(ascending=False)
        
        recommendations = []
        count = 0
        for similar_movie_id, similarity in similar_movies.items():
            if similar_movie_id == movie_id or similarity <= 0:
                continue
            
            movie_data = {'movie_id': similar_movie_id}
            if movies_df is not None:
                movie_info = movies_df[movies_df['movie_id'] == similar_movie_id]
                if not movie_info.empty:
                    movie_data['title'] = movie_info.iloc[0].get('title', '')
            
            recommendations.append({
                'movie_id': similar_movie_id,
                'title': movie_data.get('title', similar_movie_id),
                'score': float(similarity),
                'reason': "Users who liked this also liked that"
            })
            
            count += 1
            if count >= top_n:
                break
        
        return recommendations

