"""
Streamlit Admin Dashboard for CinemaCompass
Model performance monitoring, user analytics, and system metrics
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from recommendation_system.data_loader import load_from_csv, load_cleaned_datasets
from recommendation_system.evaluation import evaluate_recommender
from recommendation_system.metrics.diversity import calculate_diversity, calculate_genre_diversity
from recommendation_system.metrics.novelty import calculate_novelty
from recommendation_system.metrics.coverage import calculate_coverage
import numpy as np

# Page config
st.set_page_config(
    page_title="CinemaCompass Admin Dashboard",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 CinemaCompass Admin Dashboard")
st.markdown("---")

# Initialize session state
if 'movies_df' not in st.session_state:
    try:
        st.session_state.movies_df, st.session_state.ratings_df = load_cleaned_datasets()
    except FileNotFoundError:
        st.session_state.movies_df, st.session_state.ratings_df = load_from_csv()

if 'metrics' not in st.session_state:
    st.session_state.metrics = {}

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox(
    "Select Page",
    ["Overview", "Model Performance", "User Analytics", "System Metrics", "Data Quality"]
)

# Overview Page
if page == "Overview":
    st.header("System Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Movies", len(st.session_state.movies_df))
    
    with col2:
        st.metric("Total Users", st.session_state.ratings_df['user_id'].nunique())
    
    with col3:
        st.metric("Total Ratings", len(st.session_state.ratings_df))
    
    with col4:
        avg_rating = st.session_state.ratings_df['rating'].mean()
        st.metric("Average Rating", f"{avg_rating:.2f}")
    
    st.markdown("---")
    
    # Recent activity
    st.subheader("Recent Activity")
    
    if 'timestamp' in st.session_state.ratings_df.columns:
        st.session_state.ratings_df['timestamp'] = pd.to_datetime(st.session_state.ratings_df['timestamp'])
        recent_ratings = st.session_state.ratings_df.sort_values('timestamp', ascending=False).head(10)
        st.dataframe(recent_ratings[['user_id', 'movie_id', 'rating', 'timestamp']])
    else:
        st.info("Timestamp data not available")

# Model Performance Page
elif page == "Model Performance":
    st.header("Model Performance Metrics")
    
    # Run evaluation
    if st.button("Run Evaluation"):
        with st.spinner("Evaluating model..."):
            # Sample users for evaluation
            sample_users = st.session_state.ratings_df['user_id'].unique()[:10]
            
            # Create recommendations dict (simplified)
            recommendations_dict = {}
            for user_id in sample_users:
                # This would normally call the recommender
                user_movies = st.session_state.ratings_df[
                    st.session_state.ratings_df['user_id'] == user_id
                ]['movie_id'].tolist()[:10]
                recommendations_dict[user_id] = user_movies
            
            # Split data for evaluation
            test_size = int(len(st.session_state.ratings_df) * 0.2)
            test_ratings = st.session_state.ratings_df.tail(test_size)
            train_ratings = st.session_state.ratings_df.head(len(st.session_state.ratings_df) - test_size)
            
            # Evaluate
            results = evaluate_recommender(
                recommendations_dict,
                test_ratings,
                movies_df=st.session_state.movies_df,
                k_values=[5, 10, 20]
            )
            
            st.session_state.metrics = results
    
    # Display metrics
    if st.session_state.metrics:
        st.subheader("Evaluation Results")
        
        for k in [5, 10, 20]:
            if f'metric_{k}' in st.session_state.metrics:
                st.write(f"### Metrics @ K={k}")
                metric_data = st.session_state.metrics[f'metric_{k}']
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Precision@K", f"{metric_data.get('Precision@K', 0):.3f}")
                with col2:
                    st.metric("Recall@K", f"{metric_data.get('Recall@K', 0):.3f}")
                with col3:
                    st.metric("NDCG@K", f"{metric_data.get('NDCG@K', 0):.3f}")
                with col4:
                    st.metric("MAP@K", f"{metric_data.get('MAP@K', 0):.3f}")
        
        # Coverage metrics
        if 'coverage' in st.session_state.metrics:
            st.write("### Coverage Metrics")
            coverage = st.session_state.metrics['coverage']
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Catalog Coverage", f"{coverage.get('catalog_coverage', 0):.2%}")
            with col2:
                st.metric("User Coverage", f"{coverage.get('user_coverage', 0):.2%}")

# User Analytics Page
elif page == "User Analytics":
    st.header("User Analytics")
    
    # User distribution
    st.subheader("User Rating Distribution")
    user_rating_counts = st.session_state.ratings_df.groupby('user_id').size()
    
    fig = px.histogram(
        x=user_rating_counts.values,
        nbins=20,
        labels={'x': 'Number of Ratings per User', 'y': 'Number of Users'},
        title="Distribution of Ratings per User"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Top users
    st.subheader("Most Active Users")
    top_users = user_rating_counts.sort_values(ascending=False).head(10)
    st.dataframe(pd.DataFrame({
        'User ID': top_users.index,
        'Number of Ratings': top_users.values
    }))
    
    # Rating trends
    st.subheader("Rating Distribution")
    rating_counts = st.session_state.ratings_df['rating'].value_counts().sort_index()
    fig = px.bar(
        x=rating_counts.index,
        y=rating_counts.values,
        labels={'x': 'Rating', 'y': 'Count'},
        title="Distribution of Ratings"
    )
    st.plotly_chart(fig, use_container_width=True)

# System Metrics Page
elif page == "System Metrics":
    st.header("System Metrics")
    
    # Diversity metrics
    st.subheader("Recommendation Diversity")
    
    # Sample recommendations
    sample_movies = st.session_state.movies_df['movie_id'].head(20).tolist()
    diversity_score = calculate_diversity(sample_movies, st.session_state.movies_df)
    st.metric("Sample Diversity Score", f"{diversity_score:.3f}")
    
    # Genre diversity
    genre_diversity = calculate_genre_diversity(sample_movies, st.session_state.movies_df)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Unique Genres", genre_diversity['unique_genres'])
    with col2:
        st.metric("Genre Count", genre_diversity['genre_count'])
    with col3:
        st.metric("Diversity Score", f"{genre_diversity['diversity_score']:.3f}")
    
    # Novelty
    st.subheader("Recommendation Novelty")
    novelty_score = calculate_novelty(
        sample_movies,
        st.session_state.movies_df,
        st.session_state.ratings_df,
        catalog_size=len(st.session_state.movies_df)
    )
    st.metric("Sample Novelty Score", f"{novelty_score:.3f}")
    
    # Genre distribution
    st.subheader("Genre Distribution")
    all_genres = []
    for genres_str in st.session_state.movies_df['genres'].fillna(''):
        if genres_str:
            all_genres.extend([g.strip() for g in str(genres_str).split(',')])
    
    genre_counts = pd.Series(all_genres).value_counts().head(10)
    fig = px.bar(
        x=genre_counts.index,
        y=genre_counts.values,
        labels={'x': 'Genre', 'y': 'Count'},
        title="Top 10 Genres"
    )
    st.plotly_chart(fig, use_container_width=True)

# Data Quality Page
elif page == "Data Quality":
    st.header("Data Quality Metrics")
    
    # Missing data
    st.subheader("Missing Data Analysis")
    missing_data = st.session_state.movies_df.isnull().sum()
    missing_percent = (missing_data / len(st.session_state.movies_df)) * 100
    
    missing_df = pd.DataFrame({
        'Column': missing_data.index,
        'Missing Count': missing_data.values,
        'Missing %': missing_percent.values
    }).sort_values('Missing %', ascending=False)
    
    st.dataframe(missing_df[missing_df['Missing Count'] > 0])
    
    # Data completeness
    st.subheader("Data Completeness")
    completeness = {
        'Movies': len(st.session_state.movies_df),
        'Ratings': len(st.session_state.ratings_df),
        'Users': st.session_state.ratings_df['user_id'].nunique(),
        'Movies with Posters': st.session_state.movies_df['poster_url'].notna().sum(),
        'Movies with Overview': st.session_state.movies_df['overview'].notna().sum()
    }
    
    for key, value in completeness.items():
        st.metric(key, value)

