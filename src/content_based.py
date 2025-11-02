"""
Content-Based Filtering Module
Uses TF-IDF and cosine similarity for movie recommendations
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Optional
import joblib
import os


class ContentBasedRecommender:
    """Content-based movie recommender using TF-IDF"""
    
    def __init__(self, max_features: int = 5000, ngram_range: tuple = (1, 2)):
        """
        Initialize content-based recommender
        
        Args:
            max_features: Maximum number of features for TF-IDF
            ngram_range: Range of n-grams to use
        """
        self.tfidf = TfidfVectorizer(
            max_features=max_features,
            stop_words='english',
            ngram_range=ngram_range,
            min_df=2
        )
        self.similarity_matrix = None
        self.movies_df = None
    
    def build_model(self, movies_df: pd.DataFrame, features_column: str = 'features') -> np.ndarray:
        """
        Build similarity matrix from movie features
        
        Args:
            movies_df: DataFrame with movie data
            features_column: Column name containing combined features (genres, tags, etc.)
        
        Returns:
            Similarity matrix
        """
        self.movies_df = movies_df.copy()
        
        # Ensure features column exists
        if features_column not in movies_df.columns:
            # Create features from available columns
            features = []
            for _, row in movies_df.iterrows():
                feature_parts = []
                if pd.notna(row.get('genres')):
                    feature_parts.append(str(row['genres']))
                if pd.notna(row.get('tags')):
                    feature_parts.append(str(row['tags']))
                if pd.notna(row.get('director')):
                    feature_parts.append(str(row['director']))
                if pd.notna(row.get('cast')):
                    feature_parts.append(str(row['cast']))
                features.append(' '.join(feature_parts))
            
            movies_df[features_column] = features
        
        # Fill NaN values
        movies_df[features_column] = movies_df[features_column].fillna('')
        
        # Build TF-IDF matrix
        tfidf_matrix = self.tfidf.fit_transform(movies_df[features_column])
        
        # Compute cosine similarity
        self.similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
        
        return self.similarity_matrix
    
    def get_recommendations(
        self,
        movie_title: str,
        top_n: int = 10,
        similarity_threshold: float = 0.0
    ) -> List[Dict]:
        """
        Get content-based recommendations for a movie
        
        Args:
            movie_title: Title of the movie
            top_n: Number of recommendations
            similarity_threshold: Minimum similarity score
        
        Returns:
            List of recommended movies with scores
        """
        if self.similarity_matrix is None or self.movies_df is None:
            raise ValueError("Model not built. Call build_model() first.")
        
        # Find movie index
        movie_idx = self.movies_df[
            self.movies_df['title'].str.lower() == movie_title.lower()
        ].index
        
        if len(movie_idx) == 0:
            # Try partial match
            movie_idx = self.movies_df[
                self.movies_df['title'].str.lower().str.contains(movie_title.lower(), na=False)
            ].index
        
        if len(movie_idx) == 0:
            return []
        
        movie_idx = movie_idx[0]
        
        # Get similarity scores
        sim_scores = list(enumerate(self.similarity_matrix[movie_idx]))
        
        # Sort by similarity
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        # Get top N (excluding the movie itself)
        sim_scores = [
            (idx, score) for idx, score in sim_scores[1:top_n+1]
            if score >= similarity_threshold
        ]
        
        # Build recommendations
        recommendations = []
        for idx, score in sim_scores:
            movie = self.movies_df.iloc[idx]
            recommendations.append({
                'movie_id': movie.get('movie_id', ''),
                'title': movie.get('title', ''),
                'score': float(score),
                'genres': movie.get('genres', ''),
                'reason': f"Similar content: {movie.get('genres', 'N/A')}"
            })
        
        return recommendations
    
    def get_recommendations_from_ids(
        self,
        movie_ids: List[str],
        top_n: int = 10
    ) -> List[Dict]:
        """
        Get recommendations for multiple movies
        
        Args:
            movie_ids: List of movie IDs
            top_n: Number of recommendations per movie
        
        Returns:
            Aggregated list of recommendations
        """
        if self.similarity_matrix is None or self.movies_df is None:
            raise ValueError("Model not built. Call build_model() first.")
        
        all_scores = {}
        
        for movie_id in movie_ids:
            movie_idx = self.movies_df[
                self.movies_df['movie_id'] == movie_id
            ].index
            
            if len(movie_idx) == 0:
                continue
            
            movie_idx = movie_idx[0]
            sim_scores = list(enumerate(self.similarity_matrix[movie_idx]))
            
            for idx, score in sim_scores:
                other_movie_id = self.movies_df.iloc[idx]['movie_id']
                
                # Skip if it's one of the input movies
                if other_movie_id in movie_ids:
                    continue
                
                # Aggregate scores (max)
                if other_movie_id not in all_scores:
                    all_scores[other_movie_id] = score
                else:
                    all_scores[other_movie_id] = max(all_scores[other_movie_id], score)
        
        # Sort and get top N
        sorted_movies = sorted(all_scores.items(), key=lambda x: x[1], reverse=True)
        
        recommendations = []
        for movie_id, score in sorted_movies[:top_n]:
            movie = self.movies_df[self.movies_df['movie_id'] == movie_id].iloc[0]
            recommendations.append({
                'movie_id': movie_id,
                'title': movie.get('title', ''),
                'score': float(score),
                'genres': movie.get('genres', ''),
                'reason': f"Similar to movies you liked"
            })
        
        return recommendations
    
    def save_model(self, filepath: str):
        """Save model to disk"""
        if self.similarity_matrix is None:
            raise ValueError("No model to save")
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump({
            'similarity_matrix': self.similarity_matrix,
            'tfidf': self.tfidf,
            'movies_df': self.movies_df
        }, filepath)
    
    def load_model(self, filepath: str):
        """Load model from disk"""
        data = joblib.load(filepath)
        self.similarity_matrix = data['similarity_matrix']
        self.tfidf = data['tfidf']
        self.movies_df = data['movies_df']


def build_content_model(movies_df: pd.DataFrame, features_column: str = 'features') -> tuple:
    """
    Convenience function to build content-based model
    
    Returns:
        (ContentBasedRecommender, similarity_matrix)
    """
    recommender = ContentBasedRecommender()
    similarity_matrix = recommender.build_model(movies_df, features_column)
    return recommender, similarity_matrix


def get_content_recommendations(
    title: str,
    movies: pd.DataFrame,
    similarity: np.ndarray,
    n: int = 10
) -> pd.DataFrame:
    """
    Get content-based recommendations (legacy function for compatibility)
    
    Args:
        title: Movie title
        movies: Movies dataframe
        similarity: Pre-computed similarity matrix
        n: Number of recommendations
    
    Returns:
        DataFrame with recommendations
    """
    # Find movie index
    movie_idx = movies[movies['title'].str.lower() == title.lower()].index
    
    if len(movie_idx) == 0:
        return pd.DataFrame()
    
    movie_idx = movie_idx[0]
    
    # Get similarity scores
    sim_scores = list(enumerate(similarity[movie_idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:n+1]
    
    # Get recommended movies
    rec_indices = [i[0] for i in sim_scores]
    return movies.iloc[rec_indices][['movie_id', 'title', 'genres']]

