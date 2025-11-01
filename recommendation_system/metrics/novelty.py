"""
Novelty metrics for recommendation evaluation
Measures how surprising/unexpected recommendations are
"""

import numpy as np
import pandas as pd
from typing import List, Dict
import math


def calculate_novelty(recommendations: List[str],
                     movies_df: pd.DataFrame,
                     ratings_df: pd.DataFrame,
                     catalog_size: int = None) -> float:
    """
    Calculate novelty using self-information: -log2(popularity)
    
    Args:
        recommendations: List of recommended movie IDs
        movies_df: Movies dataframe
        ratings_df: Ratings dataframe
        catalog_size: Total catalog size (for popularity calculation)
    
    Returns:
        Average novelty score (higher = more novel)
    """
    if not recommendations:
        return 0.0
    
    if catalog_size is None:
        catalog_size = len(movies_df)
    
    novelty_scores = []
    
    for movie_id in recommendations:
        # Calculate popularity (number of ratings / catalog_size)
        movie_ratings = ratings_df[ratings_df['movie_id'] == movie_id]
        popularity = len(movie_ratings) / catalog_size if catalog_size > 0 else 0.5
        
        # Avoid log(0)
        popularity = max(popularity, 1e-10)
        
        # Self-information: -log2(popularity)
        self_info = -math.log2(popularity)
        novelty_scores.append(self_info)
    
    return np.mean(novelty_scores) if novelty_scores else 0.0


def calculate_unexpectedness(recommendations: List[str],
                            user_liked_movies: List[str],
                            movies_df: pd.DataFrame,
                            similarity_threshold: float = 0.7) -> float:
    """
    Calculate unexpectedness (how different from user's preferences)
    
    Args:
        recommendations: List of recommended movie IDs
        user_liked_movies: List of movies user liked
        movies_df: Movies dataframe
        similarity_threshold: Threshold for considering movies similar
    
    Returns:
        Unexpectedness score (0-1, higher = more unexpected)
    """
    if not recommendations or not user_liked_movies:
        return 0.5  # Neutral
    
    # For each recommendation, check similarity to liked movies
    unexpected_scores = []
    
    for rec_id in recommendations:
        rec_genres = set()
        rec_info = movies_df[movies_df['movie_id'] == rec_id]
        if not rec_info.empty:
            genres = str(rec_info.iloc[0].get('genres', '')).split(',')
            rec_genres = set([g.strip().lower() for g in genres])
        
        # Check similarity to any liked movie
        max_similarity = 0.0
        for liked_id in user_liked_movies:
            liked_info = movies_df[movies_df['movie_id'] == liked_id]
            if not liked_info.empty:
                genres = str(liked_info.iloc[0].get('genres', '')).split(',')
                liked_genres = set([g.strip().lower() for g in genres])
                
                # Jaccard similarity
                intersection = len(rec_genres & liked_genres)
                union = len(rec_genres | liked_genres)
                if union > 0:
                    similarity = intersection / union
                    max_similarity = max(max_similarity, similarity)
        
        # Unexpectedness = 1 - similarity
        unexpectedness = 1.0 - max_similarity
        unexpected_scores.append(unexpectedness)
    
    return np.mean(unexpected_scores) if unexpected_scores else 0.0

