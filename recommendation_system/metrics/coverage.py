"""
Coverage metrics for recommendation evaluation
Measures what percentage of catalog/users are covered by recommendations
"""

import pandas as pd
from typing import Dict, List


def calculate_coverage(recommendations_dict: Dict[str, List[str]],
                      movies_df: pd.DataFrame,
                      ratings_df: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate catalog and user coverage
    
    Args:
        recommendations_dict: Dict mapping user_id to list of recommended movie_ids
        movies_df: Movies dataframe
        ratings_df: Ratings dataframe
    
    Returns:
        Dict with 'catalog_coverage', 'user_coverage'
    """
    # Catalog coverage: unique movies recommended / total catalog
    all_recommended_movies = set()
    for user_id, recommendations in recommendations_dict.items():
        all_recommended_movies.update(recommendations)
    
    total_catalog_size = len(movies_df)
    catalog_coverage = len(all_recommended_movies) / total_catalog_size if total_catalog_size > 0 else 0.0
    
    # User coverage: users with recommendations / total users
    users_with_recs = len(recommendations_dict)
    total_users = ratings_df['user_id'].nunique()
    user_coverage = users_with_recs / total_users if total_users > 0 else 0.0
    
    return {
        'catalog_coverage': catalog_coverage,
        'user_coverage': user_coverage,
        'unique_items_recommended': len(all_recommended_movies),
        'total_catalog_size': total_catalog_size,
        'users_with_recommendations': users_with_recs,
        'total_users': total_users
    }

