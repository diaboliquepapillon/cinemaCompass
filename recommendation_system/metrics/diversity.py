"""
Diversity metrics for recommendation evaluation
"""

import numpy as np
import pandas as pd
from typing import List, Dict
from sklearn.metrics.pairwise import cosine_similarity


def calculate_diversity(recommendations: List[str],
                       movies_df: pd.DataFrame,
                       feature_matrix: np.ndarray = None) -> float:
    """
    Calculate intra-list diversity (average distance between recommendations)
    
    Args:
        recommendations: List of recommended movie IDs
        movies_df: Movies dataframe
        feature_matrix: Pre-computed feature matrix (optional)
    
    Returns:
        Diversity score (0-1, higher = more diverse)
    """
    if len(recommendations) < 2:
        return 0.0
    
    # If feature matrix not provided, create simple one from genres
    if feature_matrix is None:
        # Simple genre-based diversity
        genres_list = []
        for movie_id in recommendations:
            movie_info = movies_df[movies_df['movie_id'] == movie_id]
            if not movie_info.empty:
                genres = str(movie_info.iloc[0].get('genres', '')).split(',')
                genres_list.append(set([g.strip().lower() for g in genres]))
        
        # Calculate Jaccard diversity
        if len(genres_list) < 2:
            return 0.0
        
        total_similarity = 0.0
        pairs = 0
        
        for i in range(len(genres_list)):
            for j in range(i + 1, len(genres_list)):
                intersection = len(genres_list[i] & genres_list[j])
                union = len(genres_list[i] | genres_list[j])
                if union > 0:
                    similarity = intersection / union
                    total_similarity += similarity
                    pairs += 1
        
        if pairs > 0:
            avg_similarity = total_similarity / pairs
            diversity = 1.0 - avg_similarity
            return max(0.0, min(1.0, diversity))
        return 0.0
    
    # Use feature matrix for diversity calculation
    movie_indices = []
    for movie_id in recommendations:
        movie_idx = movies_df[movies_df['movie_id'] == movie_id].index
        if len(movie_idx) > 0:
            movie_indices.append(movie_idx[0])
    
    if len(movie_indices) < 2:
        return 0.0
    
    # Get feature vectors for recommended movies
    rec_features = feature_matrix[movie_indices]
    
    # Calculate pairwise cosine similarities
    similarities = cosine_similarity(rec_features)
    
    # Average similarity (excluding diagonal)
    mask = ~np.eye(len(similarities), dtype=bool)
    avg_similarity = similarities[mask].mean()
    
    diversity = 1.0 - avg_similarity
    return max(0.0, min(1.0, diversity))


def calculate_genre_diversity(recommendations: List[str],
                              movies_df: pd.DataFrame) -> Dict:
    """
    Calculate genre diversity metrics
    
    Returns:
        Dict with 'unique_genres', 'genre_count', 'diversity_score'
    """
    all_genres = set()
    
    for movie_id in recommendations:
        movie_info = movies_df[movies_df['movie_id'] == movie_id]
        if not movie_info.empty:
            genres = str(movie_info.iloc[0].get('genres', '')).split(',')
            for genre in genres:
                all_genres.add(genre.strip())
    
    unique_genres = len(all_genres)
    genre_count = len(recommendations)
    
    # Diversity score: unique genres / total recommendations
    diversity_score = unique_genres / genre_count if genre_count > 0 else 0.0
    
    return {
        'unique_genres': unique_genres,
        'genre_count': genre_count,
        'diversity_score': diversity_score
    }

