"""
Example usage of the CinemaCompass Hybrid Recommendation System
"""

from recommendation_system.hybrid_model import HybridRecommender
from recommendation_system.data_loader import load_sample_data
from recommendation_system.evaluation import precision_at_k, ndcg_at_k


def main():
    print("🎬 CinemaCompass - Hybrid Recommendation System Example\n")
    
    # Load sample data
    print("Loading data...")
    movies_df, ratings_df = load_sample_data()
    
    print(f"Loaded {len(movies_df)} movies and {len(ratings_df)} ratings\n")
    
    # Initialize recommender
    print("Initializing hybrid recommender...")
    recommender = HybridRecommender(content_weight=0.6, collaborative_weight=0.4)
    recommender.fit(movies_df, ratings_df)
    
    print("✓ Model trained successfully\n")
    
    # Example 1: Recommendations based on liked movies
    print("=" * 60)
    print("Example 1: Recommendations based on liked movies")
    print("=" * 60)
    
    liked_movies = ['m1', 'm2']  # Inception and Interstellar
    print(f"\nUser liked: {', '.join(movies_df[movies_df['movie_id'].isin(liked_movies)]['title'].tolist())}")
    
    recommendations = recommender.get_recommendations(
        liked_movies=liked_movies,
        top_n=5
    )
    
    print("\nTop 5 Recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['title']}")
        print(f"   Score: {rec['score']:.3f}")
        print(f"   Reason: {rec['reason']}\n")
    
    # Example 2: User-based collaborative filtering
    print("=" * 60)
    print("Example 2: User-based recommendations")
    print("=" * 60)
    
    user_id = 'u1'
    print(f"\nGetting recommendations for user: {user_id}")
    
    recommendations = recommender.get_recommendations(
        user_id=user_id,
        top_n=5
    )
    
    print("\nTop 5 Recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['title']}")
        print(f"   Score: {rec['score']:.3f}")
        print(f"   Reason: {rec['reason']}\n")
    
    # Example 3: Evaluation metrics
    print("=" * 60)
    print("Example 3: Evaluation Metrics")
    print("=" * 60)
    
    # Simulate recommendations and relevant items
    recommended = [r['movie_id'] for r in recommendations[:10]]
    relevant = ratings_df[
        (ratings_df['user_id'] == user_id) & 
        (ratings_df['rating'] >= 4.0)
    ]['movie_id'].tolist()
    
    prec_at_5 = precision_at_k(recommended, relevant, k=5)
    prec_at_10 = precision_at_k(recommended, relevant, k=10)
    ndcg_5 = ndcg_at_k(recommended, relevant, k=5)
    ndcg_10 = ndcg_at_k(recommended, relevant, k=10)
    
    print(f"\nPrecision@5: {prec_at_5:.3f}")
    print(f"Precision@10: {prec_at_10:.3f}")
    print(f"NDCG@5: {ndcg_5:.3f}")
    print(f"NDCG@10: {ndcg_10:.3f}")
    
    print("\n✓ Example completed successfully!")


if __name__ == "__main__":
    main()

