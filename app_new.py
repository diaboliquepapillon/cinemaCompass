"""
CinemaCompass - Modern User-Friendly UI
Clean, intuitive design focused on ease of use
"""

import streamlit as st
import pandas as pd
import numpy as np
from recommendation_system.hybrid_model import HybridRecommender
from recommendation_system.data_loader import load_sample_data
from recommendation_system.evaluation import (
    precision_at_k, recall_at_k, ndcg_at_k, map_at_k, evaluate_recommender
)
import sys
from pathlib import Path

# Add src to path for utilities
sys.path.insert(0, str(Path(__file__).parent / "src"))
try:
    from utils import format_user_id, format_id_for_display, get_poster
except ImportError:
    def format_user_id(uid): return f"User #{hash(uid) % 99999 + 1}" if uid else "Guest"
    def format_id_for_display(uid, _): return format_user_id(uid)
    def get_poster(*args): return None

# Page configuration
st.set_page_config(
    page_title="CinemaCompass - Find Your Next Favorite Movie",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# MODERN, USER-FRIENDLY CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Poppins', 'Inter', sans-serif;
    }
    
    /* Hide Streamlit defaults */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container */
    .main {
        padding: 2rem 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    /* Clean card design */
    .movie-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s, box-shadow 0.2s;
        cursor: pointer;
        border: 2px solid transparent;
    }
    
    .movie-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
        border-color: #667eea;
    }
    
    .movie-card.selected {
        border-color: #667eea;
        background: #f0f4ff;
    }
    
    /* Step indicator */
    .step-indicator {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 2rem 0;
        gap: 1rem;
    }
    
    .step {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        background: #e0e0e0;
        color: #666;
        transition: all 0.3s;
    }
    
    .step.active {
        background: #667eea;
        color: white;
        transform: scale(1.1);
    }
    
    .step.completed {
        background: #4caf50;
        color: white;
    }
    
    .step-connector {
        width: 60px;
        height: 3px;
        background: #e0e0e0;
    }
    
    .step-connector.completed {
        background: #4caf50;
    }
    
    /* Search box */
    .search-container {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Welcome section */
    .welcome-box {
        background: white;
        border-radius: 20px;
        padding: 3rem;
        margin: 2rem 0;
        text-align: center;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    }
    
    .welcome-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a1a1a;
        margin-bottom: 1rem;
    }
    
    .welcome-subtitle {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    
    /* Button styles */
    .btn-primary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 1rem 2rem;
        border-radius: 12px;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        transition: transform 0.2s;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    .btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(102, 126, 234, 0.5);
    }
    
    .btn-secondary {
        background: white;
        color: #667eea;
        border: 2px solid #667eea;
        padding: 1rem 2rem;
        border-radius: 12px;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .btn-secondary:hover {
        background: #f0f4ff;
    }
    
    /* Recommendation cards */
    .rec-card {
        background: white;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s;
        margin: 0.5rem;
    }
    
    .rec-card:hover {
        transform: scale(1.02);
    }
    
    .rec-poster {
        width: 100%;
        height: 300px;
        object-fit: cover;
    }
    
    .rec-info {
        padding: 1rem;
    }
    
    .rec-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 0.5rem;
    }
    
    .rec-genres {
        font-size: 0.85rem;
        color: #666;
        margin-bottom: 0.5rem;
    }
    
    .rec-score {
        display: inline-block;
        background: #667eea;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    /* Info boxes */
    .info-box {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .info-box-title {
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 0.5rem;
    }
    
    .info-box-text {
        color: #666;
        font-size: 0.9rem;
        line-height: 1.6;
    }
    
    /* Stats badges */
    .stat-badge {
        display: inline-block;
        background: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        margin: 0.25rem;
        font-size: 0.85rem;
        font-weight: 500;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 1  # 1: Welcome, 2: Select Movies, 3: Get Recommendations

if 'movies_df' not in st.session_state:
    with st.spinner("Loading movies..."):
        st.session_state.movies_df, st.session_state.ratings_df = load_sample_data()

if 'selected_movies' not in st.session_state:
    st.session_state.selected_movies = []

if 'recommendations' not in st.session_state:
    st.session_state.recommendations = []

if 'recommender' not in st.session_state:
    st.session_state.recommender = None

def initialize_recommender():
    """Initialize the recommendation model"""
    try:
        content_weight = st.session_state.get('content_weight', 0.5)
        recommender = HybridRecommender(
            content_weight=content_weight,
            collaborative_weight=1.0 - content_weight
        )
        # Load sample data for training
        recommender.fit(
            st.session_state.movies_df,
            st.session_state.ratings_df
        )
        return recommender
    except Exception as e:
        st.error(f"Error initializing recommender: {e}")
        return None

# STEP 1: WELCOME SCREEN
if st.session_state.step == 1:
    st.markdown("""
        <div class="welcome-box">
            <div class="welcome-title">🎬 Welcome to CinemaCompass</div>
            <div class="welcome-subtitle">
                Discover your next favorite movie with AI-powered recommendations
            </div>
            <p style="color: #666; font-size: 1rem; max-width: 600px; margin: 0 auto 2rem;">
                Our smart recommendation system learns from your preferences to suggest movies 
                you'll love. It only takes a few clicks to get started!
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Get Started", type="primary", use_container_width=True):
            st.session_state.step = 2
            st.rerun()
    
    st.markdown("---")
    
    # Show how it works
    st.markdown("### ✨ How It Works")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div style="text-align: center; padding: 1.5rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">1️⃣</div>
                <h3 style="color: #1a1a1a; margin-bottom: 0.5rem;">Select Movies</h3>
                <p style="color: #666;">Choose movies you've watched and loved</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div style="text-align: center; padding: 1.5rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">2️⃣</div>
                <h3 style="color: #1a1a1a; margin-bottom: 0.5rem;">AI Analysis</h3>
                <p style="color: #666;">Our algorithm analyzes your preferences</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div style="text-align: center; padding: 1.5rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">3️⃣</div>
                <h3 style="color: #1a1a1a; margin-bottom: 0.5rem;">Get Results</h3>
                <p style="color: #666;">Receive personalized recommendations</p>
            </div>
        """, unsafe_allow_html=True)

# STEP 2: SELECT MOVIES
elif st.session_state.step == 2:
    # Step indicator
    st.markdown("""
        <div class="step-indicator">
            <div class="step completed">✓</div>
            <div class="step-connector completed"></div>
            <div class="step active">2</div>
            <div class="step-connector"></div>
            <div class="step">3</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 style="color: white; font-size: 2rem; margin-bottom: 0.5rem;">What Movies Do You Like?</h1>
            <p style="color: rgba(255, 255, 255, 0.9); font-size: 1.1rem;">
                Select at least 3 movies you've enjoyed. This helps us understand your taste!
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Search box
    search_term = st.text_input(
        "🔍 Search for movies",
        placeholder="Type to search...",
        help="Start typing to find movies quickly"
    )
    
    # Filter movies based on search
    movies_to_show = st.session_state.movies_df
    if search_term:
        movies_to_show = movies_to_show[
            movies_to_show['title'].str.contains(search_term, case=False, na=False)
        ]
    
    # Limit to 50 for performance
    movies_to_show = movies_to_show.head(100)
    
    # Show selected count
    selected_count = len(st.session_state.selected_movies)
    st.markdown(f"""
        <div style="background: white; padding: 1rem; border-radius: 12px; margin-bottom: 1rem;">
            <strong>Selected:</strong> {selected_count} movie{'s' if selected_count != 1 else ''}
            {'✓' if selected_count >= 3 else ' (Need at least 3)'}
        </div>
    """, unsafe_allow_html=True)
    
    # Display movies in grid
    cols = st.columns(4)
    for idx, (_, movie) in enumerate(movies_to_show.iterrows()):
        col_idx = idx % 4
        with cols[col_idx]:
            movie_id = movie.get('movie_id', '')
            movie_title = movie.get('title', 'Unknown')
            genres = movie.get('genres', 'N/A')
            poster_url = movie.get('poster_url', '')
            
            is_selected = movie_title in st.session_state.selected_movies
            
            card_class = "movie-card selected" if is_selected else "movie-card"
            
            with st.container():
                st.markdown(f"""
                    <div class="{card_class}" onclick="selectMovie_{idx}()">
                """, unsafe_allow_html=True)
                
                # Poster or placeholder
                if poster_url:
                    try:
                        st.image(poster_url, use_container_width=True)
                    except:
                        st.markdown('<div style="height: 200px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; border-radius: 8px;">🎬</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div style="height: 200px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; border-radius: 8px;">🎬</div>', unsafe_allow_html=True)
                
                st.markdown(f"**{movie_title}**")
                st.caption(genres)
                
                # Selection button
                if st.button(f"{'✓ Selected' if is_selected else 'Select'}", 
                            key=f"select_{idx}", 
                            use_container_width=True,
                            type="primary" if is_selected else "secondary"):
                    if movie_title not in st.session_state.selected_movies:
                        st.session_state.selected_movies.append(movie_title)
                    else:
                        st.session_state.selected_movies.remove(movie_title)
                    st.rerun()
                
                st.markdown("</div>", unsafe_allow_html=True)
        
        # Create new row every 4 movies
        if (idx + 1) % 4 == 0 and idx < len(movies_to_show) - 1:
            cols = st.columns(4)
    
    st.markdown("---")
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.step = 1
            st.rerun()
    
    with col3:
        if st.button("Get Recommendations →", 
                    type="primary", 
                    use_container_width=True,
                    disabled=selected_count < 3):
            if selected_count >= 3:
                st.session_state.step = 3
                st.rerun()
            else:
                st.warning("Please select at least 3 movies")

# STEP 3: RECOMMENDATIONS
elif st.session_state.step == 3:
    # Step indicator
    st.markdown("""
        <div class="step-indicator">
            <div class="step completed">✓</div>
            <div class="step-connector completed"></div>
            <div class="step completed">✓</div>
            <div class="step-connector completed"></div>
            <div class="step active">3</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 style="color: white; font-size: 2rem; margin-bottom: 0.5rem;">🎯 Your Recommendations</h1>
            <p style="color: rgba(255, 255, 255, 0.9); font-size: 1.1rem;">
                Based on your selections, here are movies we think you'll love
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Generate recommendations
    if not st.session_state.recommendations:
        with st.spinner("🔮 Analyzing your preferences and generating recommendations..."):
            # Initialize recommender if needed
            if st.session_state.recommender is None:
                st.session_state.recommender = initialize_recommender()
            
            # Get movie IDs for selected movies
            movie_dict = dict(zip(st.session_state.movies_df['title'], 
                                 st.session_state.movies_df['movie_id']))
            liked_ids = [movie_dict.get(title, '') for title in st.session_state.selected_movies]
            liked_ids = [mid for mid in liked_ids if mid]
            
            if st.session_state.recommender and liked_ids:
                try:
                    # Get recommendations from the hybrid model
                    recommendations = st.session_state.recommender.get_recommendations(
                        liked_movies=liked_ids,
                        top_n=12
                    )
                    
                    # Format recommendations
                    formatted_recs = []
                    for rec in recommendations:
                        movie_id = rec.get('movie_id', '')
                        movie_info = st.session_state.movies_df[
                            st.session_state.movies_df['movie_id'] == movie_id
                        ]
                        if len(movie_info) > 0:
                            movie = movie_info.iloc[0]
                            formatted_recs.append({
                                'movie_id': movie_id,
                                'title': movie.get('title', 'Unknown'),
                                'genres': movie.get('genres', 'N/A'),
                                'score': rec.get('score', 0.0),
                                'reason': rec.get('reason', 'Recommended for you')
                            })
                    st.session_state.recommendations = formatted_recs
                except Exception as e:
                    st.error(f"Error generating recommendations: {e}")
                    st.session_state.recommendations = []
    
    # Display recommendations
    if st.session_state.recommendations:
        st.markdown(f"""
            <div class="info-box">
                <div class="info-box-title">💡 Found {len(st.session_state.recommendations)} recommendations</div>
                <div class="info-box-text">
                    These movies were selected based on similarities to your preferences. 
                    Click on any movie to see more details!
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Display in grid
        cols = st.columns(4)
        for idx, rec in enumerate(st.session_state.recommendations[:12]):
            col_idx = idx % 4
            
            if idx > 0 and idx % 4 == 0:
                cols = st.columns(4)
            
            with cols[col_idx]:
                movie_id = rec.get('movie_id', '')
                movie_title = rec.get('title', 'Unknown')
                genres = rec.get('genres', 'N/A')
                score = rec.get('score', 0)
                
                # Find movie poster
                movie_info = st.session_state.movies_df[
                    st.session_state.movies_df['movie_id'] == movie_id
                ]
                poster_url = ''
                if len(movie_info) > 0:
                    poster_url = movie_info.iloc[0].get('poster_url', '')
                
                st.markdown("""
                    <div class="rec-card">
                """, unsafe_allow_html=True)
                
                # Poster
                if poster_url:
                    try:
                        st.image(poster_url, use_container_width=True)
                    except:
                        st.markdown('<div style="height: 300px; background: #f0f0f0; display: flex; align-items: center; justify-content: center;">🎬</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div style="height: 300px; background: #f0f0f0; display: flex; align-items: center; justify-content: center;">🎬</div>', unsafe_allow_html=True)
                
                # Info
                st.markdown(f"""
                    <div class="rec-info">
                        <div class="rec-title">{movie_title}</div>
                        <div class="rec-genres">{genres}</div>
                        <div class="rec-score">Match: {score:.1%}</div>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No recommendations available. Please go back and select more movies.")
    
    st.markdown("---")
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("← Start Over", use_container_width=True):
            st.session_state.step = 1
            st.session_state.selected_movies = []
            st.session_state.recommendations = []
            st.rerun()
    
    with col2:
        if st.button("🔄 Get New Recommendations", use_container_width=True):
            st.session_state.recommendations = []
            st.rerun()
    
    with col3:
        if st.button("📝 Change Selections", use_container_width=True):
            st.session_state.step = 2
            st.rerun()

