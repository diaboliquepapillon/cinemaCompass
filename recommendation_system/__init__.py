"""
CinemaCompass Hybrid Recommendation System
Combines content-based and collaborative filtering with rich metadata
"""

from .hybrid_recommender import HybridRecommender
from .evaluation import evaluate_model, precision_at_k, recall_at_k, ndcg_at_k

__all__ = ['HybridRecommender', 'evaluate_model', 'precision_at_k', 'recall_at_k', 'ndcg_at_k']

