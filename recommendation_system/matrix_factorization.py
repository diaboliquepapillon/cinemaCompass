"""
Matrix Factorization methods for collaborative filtering
Implements SVD (Singular Value Decomposition) and ALS (Alternating Least Squares)
"""

import numpy as np
import pandas as pd
from typing import Tuple, Optional, Dict
import logging
from scipy.sparse import csr_matrix
import warnings
warnings.filterwarnings('ignore')

try:
    from surprise import SVD as SurpriseSVD, Dataset, Reader
    from surprise.model_selection import train_test_split
    SURPRISE_AVAILABLE = True
except ImportError:
    SURPRISE_AVAILABLE = False
    logging.warning("surprise not available. Install with: pip install surprise")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MatrixFactorization:
    """Matrix factorization for collaborative filtering"""
    
    def __init__(self, n_factors: int = 50, use_surprise: bool = True):
        """
        Initialize matrix factorization model
        
        Args:
            n_factors: Number of latent factors
            use_surprise: Whether to use Surprise library (more robust)
        """
        self.n_factors = n_factors
        self.use_surprise = use_surprise and SURPRISE_AVAILABLE
        self.model = None
        self.user_factors = None
        self.item_factors = None
        self.user_bias = None
        self.item_bias = None
        self.global_mean = 0.0
        self.user_to_idx = {}
        self.item_to_idx = {}
        self.idx_to_user = {}
        self.idx_to_item = {}
    
    def fit(self, ratings_df: pd.DataFrame):
        """
        Fit matrix factorization model
        
        Args:
            ratings_df: DataFrame with columns: user_id, movie_id, rating
        """
        if self.use_surprise:
            self._fit_surprise(ratings_df)
        else:
            self._fit_custom(ratings_df)
    
    def _fit_surprise(self, ratings_df: pd.DataFrame):
        """Fit using Surprise library"""
        logger.info("Fitting SVD model using Surprise library...")
        
        # Prepare data for Surprise
        reader = Reader(rating_scale=(0.5, 5.0))
        data = Dataset.load_from_df(
            ratings_df[['user_id', 'movie_id', 'rating']],
            reader
        )
        
        # Train on full dataset
        trainset = data.build_full_trainset()
        
        # Initialize and train SVD
        self.model = SurpriseSVD(n_factors=self.n_factors, verbose=False)
        self.model.fit(trainset)
        
        # Extract factors
        self.global_mean = trainset.global_mean
        self.user_factors = self.model.pu
        self.item_factors = self.model.qi
        
        # Build mappings
        for inner_id in range(trainset.n_users):
            raw_id = trainset.to_raw_uid(inner_id)
            self.user_to_idx[str(raw_id)] = inner_id
            self.idx_to_user[inner_id] = str(raw_id)
        
        for inner_id in range(trainset.n_items):
            raw_id = trainset.to_raw_iid(inner_id)
            self.item_to_idx[str(raw_id)] = inner_id
            self.idx_to_item[inner_id] = str(raw_id)
        
        logger.info(f"Fitted SVD: {trainset.n_users} users, {trainset.n_items} items")
    
    def _fit_custom(self, ratings_df: pd.DataFrame):
        """Custom implementation using ALS"""
        logger.info("Fitting matrix factorization using custom ALS...")
        
        # Create user and item mappings
        users = ratings_df['user_id'].unique()
        items = ratings_df['movie_id'].unique()
        
        self.user_to_idx = {str(u): idx for idx, u in enumerate(users)}
        self.item_to_idx = {str(i): idx for idx, i in enumerate(items)}
        self.idx_to_user = {idx: u for u, idx in self.user_to_idx.items()}
        self.idx_to_item = {idx: i for i, idx in self.item_to_idx.items()}
        
        n_users = len(users)
        n_items = len(items)
        self.global_mean = ratings_df['rating'].mean()
        
        # Initialize factors
        self.user_factors = np.random.normal(0, 0.1, (n_users, self.n_factors))
        self.item_factors = np.random.normal(0, 0.1, (n_items, self.n_factors))
        self.user_bias = np.zeros(n_users)
        self.item_bias = np.zeros(n_items)
        
        # Create sparse matrix
        user_indices = [self.user_to_idx[str(u)] for u in ratings_df['user_id']]
        item_indices = [self.item_to_idx[str(i)] for i in ratings_df['movie_id']]
        ratings = ratings_df['rating'].values
        
        R = csr_matrix((ratings, (user_indices, item_indices)), 
                       shape=(n_users, n_items))
        
        # ALS training
        n_iterations = 20
        reg = 0.01
        learning_rate = 0.01
        
        for iteration in range(n_iterations):
            # Update user factors
            for u in range(n_users):
                items_rated = R[u].indices
                if len(items_rated) > 0:
                    ratings_u = R[u].data
                    items_u = self.item_factors[items_rated]
                    
                    # Update user factors
                    self.user_factors[u] = np.linalg.solve(
                        items_u.T @ items_u + reg * np.eye(self.n_factors),
                        items_u.T @ ratings_u
                    )
                    
                    # Update user bias
                    self.user_bias[u] = np.mean(ratings_u - 
                                               self.item_factors[items_rated] @ self.user_factors[u])
            
            # Update item factors
            for i in range(n_items):
                users_rated = R[:, i].indices
                if len(users_rated) > 0:
                    ratings_i = R[:, i].data
                    users_i = self.user_factors[users_rated]
                    
                    # Update item factors
                    self.item_factors[i] = np.linalg.solve(
                        users_i.T @ users_i + reg * np.eye(self.n_factors),
                        users_i.T @ ratings_i
                    )
                    
                    # Update item bias
                    self.item_bias[i] = np.mean(ratings_i - 
                                               self.user_factors[users_rated] @ self.item_factors[i])
            
            if (iteration + 1) % 5 == 0:
                logger.info(f"ALS iteration {iteration + 1}/{n_iterations}")
        
        logger.info(f"Fitted ALS: {n_users} users, {n_items} items")
    
    def predict(self, user_id: str, movie_id: str) -> float:
        """
        Predict rating for user-movie pair
        
        Args:
            user_id: User identifier
            movie_id: Movie identifier
        
        Returns:
            Predicted rating
        """
        if self.use_surprise and self.model:
            try:
                prediction = self.model.predict(user_id, movie_id)
                return prediction.est
            except:
                return self.global_mean
        
        # Custom prediction
        user_id = str(user_id)
        movie_id = str(movie_id)
        
        if user_id not in self.user_to_idx or movie_id not in self.item_to_idx:
            return self.global_mean
        
        u_idx = self.user_to_idx[user_id]
        i_idx = self.item_to_idx[movie_id]
        
        prediction = (self.global_mean + 
                     self.user_bias[u_idx] + 
                     self.item_bias[i_idx] + 
                     self.user_factors[u_idx] @ self.item_factors[i_idx])
        
        return np.clip(prediction, 0.5, 5.0)
    
    def get_user_representations(self) -> np.ndarray:
        """Get all user latent factor representations"""
        if self.user_factors is not None:
            return self.user_factors
        return np.array([])
    
    def get_item_representations(self) -> np.ndarray:
        """Get all item latent factor representations"""
        if self.item_factors is not None:
            return self.item_factors
        return np.array([])

