"""
Evaluation metrics for recommendation systems
Enhanced with diversity, novelty, and coverage metrics
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple
from .metrics.diversity import calculate_diversity, calculate_genre_diversity
from .metrics.novelty import calculate_novelty, calculate_unexpectedness
from .metrics.coverage import calculate_coverage
import warnings
warnings.filterwarnings('ignore')


def precision_at_k(recommended_items: List[str], relevant_items: List[str], k: int) -> float:
    """
    Calculate Precision@K
    
    Args:
        recommended_items: List of recommended item IDs
        relevant_items: List of relevant item IDs (ground truth)
        k: Number of top recommendations to consider
    
    Returns:
        Precision@K score
    """
    if k == 0 or len(recommended_items) == 0:
        return 0.0
    
    top_k_recommended = recommended_items[:k]
    relevant_recommended = [item for item in top_k_recommended if item in relevant_items]
    
    return len(relevant_recommended) / min(k, len(recommended_items))


def recall_at_k(recommended_items: List[str], relevant_items: List[str], k: int) -> float:
    """
    Calculate Recall@K
    
    Args:
        recommended_items: List of recommended item IDs
        relevant_items: List of relevant item IDs (ground truth)
        k: Number of top recommendations to consider
    
    Returns:
        Recall@K score
    """
    if len(relevant_items) == 0:
        return 0.0
    
    top_k_recommended = recommended_items[:k]
    relevant_recommended = [item for item in top_k_recommended if item in relevant_items]
    
    return len(relevant_recommended) / len(relevant_items)


def ndcg_at_k(recommended_items: List[str], relevant_items: List[str], 
              k: int, scores: List[float] = None) -> float:
    """
    Calculate Normalized Discounted Cumulative Gain (NDCG)@K
    
    Args:
        recommended_items: List of recommended item IDs
        relevant_items: List of relevant item IDs (ground truth)
        k: Number of top recommendations to consider
        scores: Optional relevance scores for recommended items
    
    Returns:
        NDCG@K score
    """
    if k == 0 or len(recommended_items) == 0 or len(relevant_items) == 0:
        return 0.0
    
    top_k_recommended = recommended_items[:k]
    
    # Calculate DCG
    dcg = 0.0
    for i, item in enumerate(top_k_recommended):
        if item in relevant_items:
            relevance = scores[i] if scores and i < len(scores) else 1.0
            position = i + 1
            dcg += relevance / np.log2(position + 1)
    
    # Calculate ideal DCG (IDCG)
    ideal_relevance = [scores[i] if scores and i < len(scores) else 1.0 
                      for i in range(min(k, len(relevant_items)))]
    ideal_relevance.sort(reverse=True)
    
    idcg = 0.0
    for i, rel in enumerate(ideal_relevance):
        idcg += rel / np.log2(i + 2)
    
    if idcg == 0:
        return 0.0
    
    return dcg / idcg


def map_at_k(recommended_items: List[str], relevant_items: List[str], k: int) -> float:
    """
    Calculate Mean Average Precision (MAP)@K
    
    Args:
        recommended_items: List of recommended item IDs
        relevant_items: List of relevant item IDs
        k: Number of top recommendations to consider
    
    Returns:
        MAP@K score
    """
    if k == 0 or len(relevant_items) == 0:
        return 0.0
    
    top_k_recommended = recommended_items[:k]
    relevant_found = []
    precision_scores = []
    
    for i, item in enumerate(top_k_recommended):
        if item in relevant_items:
            relevant_found.append(item)
            precision_scores.append(len(relevant_found) / (i + 1))
    
    if len(precision_scores) == 0:
        return 0.0
    
    return sum(precision_scores) / len(relevant_items)


def evaluate_recommender(recommendations_dict: Dict[str, List[str]],
                        test_ratings: pd.DataFrame,
                        movies_df: pd.DataFrame = None,
                        k_values: List[int] = [5, 10, 20],
                        min_rating: float = 4.0) -> Dict[str, Dict[str, float]]:
    """
    Evaluate recommender system on test data
    
    Args:
        recommendations_dict: Dictionary mapping user_id to list of recommended movie_ids
        test_ratings: DataFrame with columns: user_id, movie_id, rating
        movies_df: Movies dataframe (for diversity/novelty metrics)
        k_values: List of K values to evaluate at
        min_rating: Minimum rating to consider as relevant
    
    Returns:
        Dictionary with evaluation metrics
    """
    results = {f'metric_{k}': {} for k in k_values}
    
    for k in k_values:
        precisions = []
        recalls = []
        ndcgs = []
        maps = []
        diversities = []
        novelties = []
        
        for user_id, recommended_items in recommendations_dict.items():
            # Get relevant items for this user (movies rated >= min_rating)
            user_test = test_ratings[test_ratings['user_id'] == user_id]
            relevant_items = user_test[
                user_test['rating'] >= min_rating
            ]['movie_id'].tolist()
            
            # Get top-K recommendations
            top_k_items = recommended_items[:k]
            
            if len(top_k_items) == 0:
                continue
            
            # Calculate accuracy metrics
            if len(relevant_items) > 0:
                prec = precision_at_k(top_k_items, relevant_items, k)
                rec = recall_at_k(top_k_items, relevant_items, k)
                ndcg = ndcg_at_k(top_k_items, relevant_items, k)
                map_score = map_at_k(top_k_items, relevant_items, k)
                
                precisions.append(prec)
                recalls.append(rec)
                ndcgs.append(ndcg)
                maps.append(map_score)
            
            # Calculate diversity
            if movies_df is not None and len(top_k_items) > 1:
                diversity = calculate_diversity(top_k_items, movies_df)
                diversities.append(diversity)
            
            # Calculate novelty
            if movies_df is not None and len(test_ratings) > 0:
                novelty = calculate_novelty(
                    top_k_items,
                    movies_df,
                    test_ratings,
                    catalog_size=len(movies_df)
                )
                novelties.append(novelty)
        
        result_dict = {}
        
        if len(precisions) > 0:
            result_dict['Precision@K'] = np.mean(precisions)
            result_dict['Recall@K'] = np.mean(recalls)
            result_dict['NDCG@K'] = np.mean(ndcgs)
            result_dict['MAP@K'] = np.mean(maps)
        else:
            result_dict['Precision@K'] = 0.0
            result_dict['Recall@K'] = 0.0
            result_dict['NDCG@K'] = 0.0
            result_dict['MAP@K'] = 0.0
        
        # Add diversity and novelty
        if diversities:
            result_dict['Diversity@K'] = np.mean(diversities)
        if novelties:
            result_dict['Novelty@K'] = np.mean(novelties)
        
        results[f'metric_{k}'] = result_dict
    
    # Add coverage metrics
    if movies_df is not None:
        coverage_metrics = calculate_coverage(recommendations_dict, movies_df, test_ratings)
        results['coverage'] = coverage_metrics
    
    return results

