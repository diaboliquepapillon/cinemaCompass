"""
Evaluation metrics for recommendation systems
Precision@K, Recall@K, NDCG@K
"""

import numpy as np
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def precision_at_k(
    recommended_items: List[str],
    relevant_items: List[str],
    k: int
) -> float:
    """
    Calculate Precision@K
    
    Args:
        recommended_items: List of recommended item IDs
        relevant_items: List of relevant (ground truth) item IDs
        k: Top K items to consider
    
    Returns:
        Precision@K score (0-1)
    """
    if k == 0 or len(recommended_items) == 0:
        return 0.0
    
    # Take top K recommendations
    top_k = recommended_items[:k]
    
    # Count how many are relevant
    relevant_count = sum(1 for item in top_k if item in relevant_items)
    
    return relevant_count / min(k, len(top_k))


def recall_at_k(
    recommended_items: List[str],
    relevant_items: List[str],
    k: int
) -> float:
    """
    Calculate Recall@K
    
    Args:
        recommended_items: List of recommended item IDs
        relevant_items: List of relevant (ground truth) item IDs
        k: Top K items to consider
    
    Returns:
        Recall@K score (0-1)
    """
    if len(relevant_items) == 0:
        return 0.0
    
    # Take top K recommendations
    top_k = recommended_items[:k]
    
    # Count how many relevant items were retrieved
    retrieved_relevant = sum(1 for item in top_k if item in relevant_items)
    
    return retrieved_relevant / len(relevant_items)


def dcg_at_k(scores: List[float], k: int) -> float:
    """
    Calculate Discounted Cumulative Gain at K
    
    Args:
        scores: List of relevance scores (1 if relevant, 0 if not)
        k: Top K items to consider
    
    Returns:
        DCG@K score
    """
    scores = scores[:k]
    dcg = 0.0
    for i, score in enumerate(scores):
        dcg += score / np.log2(i + 2)  # i+2 because log2(1) = 0
    return dcg


def ndcg_at_k(
    recommended_items: List[str],
    relevant_items: List[str],
    k: int
) -> float:
    """
    Calculate Normalized Discounted Cumulative Gain at K
    
    Args:
        recommended_items: List of recommended item IDs
        relevant_items: List of relevant (ground truth) item IDs
        k: Top K items to consider
    
    Returns:
        NDCG@K score (0-1)
    """
    if len(relevant_items) == 0:
        return 0.0
    
    # Create relevance scores (1 if relevant, 0 if not)
    scores = [1.0 if item in relevant_items else 0.0 for item in recommended_items[:k]]
    
    # Calculate DCG
    dcg = dcg_at_k(scores, k)
    
    # Calculate Ideal DCG (perfect ranking)
    ideal_scores = [1.0] * min(len(relevant_items), k) + [0.0] * max(0, k - len(relevant_items))
    ideal_dcg = dcg_at_k(ideal_scores, k)
    
    if ideal_dcg == 0:
        return 0.0
    
    return dcg / ideal_dcg


def mean_average_precision(
    all_recommendations: List[List[str]],
    all_relevant_items: List[List[str]],
    k: int
) -> float:
    """
    Calculate Mean Average Precision (MAP@K)
    
    Args:
        all_recommendations: List of recommendation lists (one per user)
        all_relevant_items: List of relevant items lists (one per user)
        k: Top K items to consider
    
    Returns:
        MAP@K score
    """
    if len(all_recommendations) != len(all_relevant_items):
        raise ValueError("Number of recommendation lists must match number of relevant items lists")
    
    if len(all_recommendations) == 0:
        return 0.0
    
    aps = []
    for recommended_items, relevant_items in zip(all_recommendations, all_relevant_items):
        if len(relevant_items) == 0:
            continue
        
        top_k = recommended_items[:k]
        precisions = []
        
        for i, item in enumerate(top_k):
            if item in relevant_items:
                # Precision at this position
                prec = sum(1 for rec_item in top_k[:i+1] if rec_item in relevant_items) / (i + 1)
                precisions.append(prec)
        
        if precisions:
            ap = np.mean(precisions)
            aps.append(ap)
        else:
            aps.append(0.0)
    
    return np.mean(aps) if aps else 0.0


def evaluate_model(
    model,
    test_data: List[Dict],
    k_values: List[int] = [5, 10, 20]
) -> Dict:
    """
    Comprehensive evaluation of a recommendation model
    
    Args:
        model: Recommendation model with get_recommendations method
        test_data: List of test cases, each with:
            - user_id: User ID
            - liked_movies: List of liked movie IDs
            - relevant_movies: List of relevant movie IDs (ground truth)
        k_values: List of K values to evaluate at
    
    Returns:
        Dictionary with evaluation metrics
    """
    results = {}
    
    all_precision = {k: [] for k in k_values}
    all_recall = {k: [] for k in k_values}
    all_ndcg = {k: [] for k in k_values}
    
    for test_case in test_data:
        user_id = test_case.get('user_id')
        liked_movies = test_case.get('liked_movies', [])
        relevant_movies = test_case.get('relevant_movies', [])
        
        # Get recommendations
        recommendations = model.get_recommendations(
            user_id=user_id,
            liked_movie_ids=liked_movies,
            top_n=max(k_values),
            explain=False
        )
        
        recommended_ids = [rec['movie_id'] for rec in recommendations]
        
        # Calculate metrics for each K
        for k in k_values:
            prec = precision_at_k(recommended_ids, relevant_movies, k)
            rec = recall_at_k(recommended_ids, relevant_movies, k)
            ndcg = ndcg_at_k(recommended_ids, relevant_movies, k)
            
            all_precision[k].append(prec)
            all_recall[k].append(rec)
            all_ndcg[k].append(ndcg)
    
    # Aggregate results
    for k in k_values:
        results[f'precision@{k}'] = np.mean(all_precision[k]) if all_precision[k] else 0.0
        results[f'recall@{k}'] = np.mean(all_recall[k]) if all_recall[k] else 0.0
        results[f'ndcg@{k}'] = np.mean(all_ndcg[k]) if all_ndcg[k] else 0.0
    
    return results

