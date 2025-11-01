"""
Cold-start problem handlers for new users and new movies
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ColdStartHandler:
    """Handle cold-start problems for new users and new movies"""
    
    def __init__(self, movies_df: pd.DataFrame, ratings_df: pd.DataFrame):
        """
        Initialize cold-start handler
        
        Args:
            movies_df: Movies dataframe
            ratings_df: Ratings dataframe
        """
        self.movies_df = movies_df.copy()
        self.ratings_df = ratings_df.copy()
        
        # Pre-compute popular movies
        self._compute_popular_movies()
        
        # Pre-compute genre preferences
        self._compute_genre_popularity()
    
    def _compute_popular_movies(self):
        """Pre-compute popular movies for fallback recommendations"""
        movie_ratings = self.ratings_df.groupby('movie_id').agg({
            'rating': ['mean', 'count']
        }).reset_index()
        movie_ratings.columns = ['movie_id', 'avg_rating', 'rating_count']
        
        # Score = weighted average rating with popularity
        movie_ratings['popularity_score'] = (
            movie_ratings['avg_rating'] * movie_ratings['rating_count'] / 
            (movie_ratings['rating_count'] + 10)  # Bayesian average
        )
        
        self.popular_movies = movie_ratings.sort_values(
            'popularity_score', ascending=False
        )['movie_id'].tolist()
        
        logger.info(f"Pre-computed {len(self.popular_movies)} popular movies")
    
    def _compute_genre_popularity(self):
        """Pre-compute genre-based popularity"""
        # Expand genres
        genre_scores = {}
        
        for _, movie in self.movies_df.iterrows():
            genres = str(movie.get('genres', '')).split(',')
            movie_id = movie['movie_id']
            
            # Get movie rating info
            movie_ratings = self.ratings_df[self.ratings_df['movie_id'] == movie_id]
            if len(movie_ratings) > 0:
                avg_rating = movie_ratings['rating'].mean()
                rating_count = len(movie_ratings)
                
                for genre in genres:
                    genre = genre.strip()
                    if genre:
                        if genre not in genre_scores:
                            genre_scores[genre] = []
                        genre_scores[genre].append((avg_rating, rating_count))
        
        # Calculate average scores per genre
        self.genre_popularity = {}
        for genre, scores in genre_scores.items():
            if scores:
                avg_rating = np.mean([s[0] for s in scores])
                total_ratings = sum([s[1] for s in scores])
                self.genre_popularity[genre] = {
                    'avg_rating': avg_rating,
                    'total_ratings': total_ratings
                }
        
        logger.info(f"Pre-computed popularity for {len(self.genre_popularity)} genres")
    
    def recommend_for_new_user(self,
                               genre_preferences: Optional[List[str]] = None,
                               top_n: int = 10) -> List[Dict]:
        """
        Get recommendations for a new user (no rating history)
        
        Args:
            genre_preferences: List of preferred genres (optional)
            top_n: Number of recommendations
        
        Returns:
            List of recommendation dicts
        """
        if genre_preferences and len(genre_preferences) > 0:
            # Filter by genre preferences
            genre_movies = self.movies_df[
                self.movies_df['genres'].str.contains(
                    '|'.join(genre_preferences), case=False, na=False
                )
            ]['movie_id'].tolist()
            
            # Score by popularity within genre
            genre_scored = []
            for movie_id in genre_movies:
                movie_ratings = self.ratings_df[self.ratings_df['movie_id'] == movie_id]
                if len(movie_ratings) > 0:
                    avg_rating = movie_ratings['rating'].mean()
                    count = len(movie_ratings)
                    score = avg_rating * count / (count + 10)
                    genre_scored.append((movie_id, score))
            
            # Sort and get top N
            genre_scored.sort(key=lambda x: x[1], reverse=True)
            recommended_ids = [m[0] for m in genre_scored[:top_n]]
        else:
            # Fall back to popular movies
            recommended_ids = self.popular_movies[:top_n]
        
        # Format recommendations
        recommendations = []
        for movie_id in recommended_ids:
            movie_info = self.movies_df[self.movies_df['movie_id'] == movie_id]
            if not movie_info.empty:
                movie_info = movie_info.iloc[0]
                recommendations.append({
                    'movie_id': movie_id,
                    'title': movie_info.get('title', ''),
                    'score': 0.5,  # Neutral score for cold-start
                    'reason': self._generate_cold_start_reason(movie_info, genre_preferences)
                })
        
        return recommendations
    
    def recommend_new_movie(self,
                           movie_id: str,
                           content_filter,
                           top_n: int = 10) -> List[Dict]:
        """
        Get users to recommend a new movie to
        
        Args:
            movie_id: New movie ID
            content_filter: ContentBasedFilter instance for finding similar movies
            top_n: Number of user recommendations
        
        Returns:
            List of user recommendations (or movie recommendations if content-based approach)
        """
        # Find similar movies using content-based filtering
        similar_movies = content_filter.get_recommendations(movie_id, top_n=20)
        
        # Get users who liked similar movies
        user_scores = {}
        
        for similar_movie in similar_movies:
            similar_id = similar_movie['movie_id']
            similarity = similar_movie['score']
            
            # Get users who rated this similar movie highly
            high_ratings = self.ratings_df[
                (self.ratings_df['movie_id'] == similar_id) & 
                (self.ratings_df['rating'] >= 4.0)
            ]
            
            for _, rating in high_ratings.iterrows():
                user_id = rating['user_id']
                if user_id not in user_scores:
                    user_scores[user_id] = 0.0
                user_scores[user_id] += similarity * rating['rating']
        
        # Sort users by score
        sorted_users = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Return top users (or convert to movie recommendations)
        recommendations = []
        for user_id, score in sorted_users[:top_n]:
            recommendations.append({
                'user_id': user_id,
                'score': float(score),
                'reason': f"Liked similar movies to {movie_id}"
            })
        
        return recommendations
    
    def _generate_cold_start_reason(self,
                                    movie_info: pd.Series,
                                    genre_preferences: Optional[List[str]]) -> str:
        """Generate explanation for cold-start recommendation"""
        if genre_preferences:
            movie_genres = str(movie_info.get('genres', '')).split(',')
            matching_genres = [g.strip() for g in movie_genres 
                             if g.strip().lower() in [p.lower() for p in genre_preferences]]
            if matching_genres:
                return f"Matches your preferred genres: {', '.join(matching_genres[:2])}"
        
        return "Popular and highly-rated movie"

