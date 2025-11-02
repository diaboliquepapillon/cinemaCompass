"""
Streamlit app for CinemaCompass Hybrid Recommendation System
NETFLIX-STYLE UI
"""

import streamlit as st
import pandas as pd
import numpy as np
from recommendation_system.hybrid_model import HybridRecommender
from recommendation_system.data_loader import load_sample_data
from recommendation_system.evaluation import (
    precision_at_k, recall_at_k, ndcg_at_k, map_at_k, evaluate_recommender
)
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

# Add src to path for utilities
sys.path.insert(0, str(Path(__file__).parent / "src"))
try:
    from utils import format_user_id, format_id_for_display, get_poster
except ImportError:
    # Fallback if utils not available
    def format_user_id(uid): return f"User #{hash(uid) % 99999 + 1}" if uid else "Guest"
    def format_id_for_display(uid, _): return format_user_id(uid)
    def get_poster(*args): return None


# Page configuration
st.set_page_config(
    page_title="CinemaCompass - Hybrid Movie Recommendations",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# CINEMATIC CUSTOM CSS - Portfolio Ready Design
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;700;900&family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', 'Montserrat', 'Helvetica Neue', Arial, sans-serif;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Netflix-style navigation */
    .netflix-nav {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background: linear-gradient(180deg, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.7) 50%, transparent 100%);
        padding: 1rem 3rem;
        z-index: 1000;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .nav-logo {
        font-size: 2rem;
        font-weight: 700;
        color: #E50914;
        text-decoration: none;
    }
    
    .nav-links {
        display: flex;
        gap: 2rem;
        align-items: center;
    }
    
    .nav-link {
        color: #FFFFFF;
        text-decoration: none;
        font-size: 0.95rem;
        transition: color 0.3s;
        position: relative;
    }
    
    .nav-link.active {
        color: #FFFFFF;
    }
    
    .nav-link.active::after {
        content: '';
        position: absolute;
        bottom: -5px;
        left: 0;
        right: 0;
        height: 2px;
        background: #E50914;
    }
    
    .nav-icons {
        display: flex;
        gap: 1.5rem;
        align-items: center;
    }
    
    /* Hero Section */
    .hero-section {
        position: relative;
        height: 80vh;
        min-height: 600px;
        background-size: cover;
        background-position: center;
        display: flex;
        align-items: center;
        margin-top: -100px;
        padding-top: 100px;
    }
    
    .hero-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(90deg, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.7) 50%, rgba(0,0,0,0.3) 100%);
    }
    
    .hero-content {
        position: relative;
        z-index: 2;
        padding: 2rem 3rem;
        max-width: 600px;
        color: white;
    }
    
    .hero-duration {
        font-size: 0.9rem;
        color: #B8B8B8;
        margin-bottom: 0.5rem;
    }
    
    .hero-rating {
        font-size: 1rem;
        color: #FFFFFF;
        margin-bottom: 0.5rem;
    }
    
    .hero-title {
        font-size: 4rem;
        font-weight: 700;
        color: #FFFFFF;
        margin: 1rem 0;
        line-height: 1.1;
    }
    
    .hero-description {
        font-size: 1.1rem;
        color: #E5E5E5;
        line-height: 1.6;
        margin: 1.5rem 0;
    }
    
    .hero-buttons {
        display: flex;
        gap: 1rem;
        margin-top: 2rem;
    }
    
    .btn-watch {
        background: #E50914;
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        border-radius: 4px;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        transition: all 0.3s;
    }
    
    .btn-watch:hover {
        background: #F40612;
        transform: scale(1.05);
    }
    
    .btn-add {
        background: rgba(42, 42, 42, 0.6);
        color: white;
        border: 2px solid white;
        padding: 0.75rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        border-radius: 4px;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        transition: all 0.3s;
    }
    
    .btn-add:hover {
        background: rgba(255, 255, 255, 0.2);
    }
    
    /* Section Headers */
    .section-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 2rem 0 1rem 0;
        padding: 0 3rem;
    }
    
    .section-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #FFFFFF;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .section-tabs {
        display: flex;
        gap: 1.5rem;
        align-items: center;
    }
    
    .section-tab {
        color: #B8B8B8;
        cursor: pointer;
        font-size: 0.95rem;
        transition: color 0.3s;
        position: relative;
    }
    
    .section-tab.active {
        color: #FFFFFF;
    }
    
    .section-tab.active::after {
        content: '';
        position: absolute;
        bottom: -5px;
        left: 0;
        right: 0;
        height: 2px;
        background: #E50914;
    }
    
    /* Category Filters */
    .category-filters {
        display: flex;
        gap: 1rem;
        padding: 0 3rem;
        margin-bottom: 1.5rem;
        overflow-x: auto;
        scrollbar-width: none;
    }
    
    .category-filters::-webkit-scrollbar {
        display: none;
    }
    
    .category-btn {
        background: transparent;
        border: 2px solid #E50914;
        color: #FFFFFF;
        padding: 0.5rem 1.5rem;
        border-radius: 20px;
        font-size: 0.9rem;
        cursor: pointer;
        white-space: nowrap;
        transition: all 0.3s;
    }
    
    .category-btn.active {
        background: #E50914;
        color: #FFFFFF;
    }
    
    .category-btn:hover {
        background: #E50914;
        transform: scale(1.05);
    }
    
    /* Movie Row */
    .movie-row {
        display: flex;
        gap: 0.5rem;
        padding: 0 3rem;
        overflow-x: auto;
        scrollbar-width: thin;
        scrollbar-color: #E50914 #141414;
        margin-bottom: 2rem;
    }
    
    .movie-row::-webkit-scrollbar {
        height: 8px;
    }
    
    .movie-row::-webkit-scrollbar-track {
        background: #0C0C0C;
    }
    
    .movie-row::-webkit-scrollbar-thumb {
        background: #E50914;
        border-radius: 4px;
    }
    
    .movie-poster {
        min-width: 200px;
        width: 200px;
        height: 300px;
        border-radius: 4px;
        overflow: hidden;
        cursor: pointer;
        transition: transform 0.3s, box-shadow 0.3s;
        position: relative;
    }
    
    .movie-poster:hover {
        transform: scale(1.1);
        z-index: 10;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8);
    }
    
    .movie-poster img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    
    .movie-info-overlay {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(180deg, transparent 0%, rgba(0,0,0,0.9) 100%);
        padding: 1rem;
        color: white;
        transform: translateY(100%);
        transition: transform 0.3s;
    }
    
    .movie-poster:hover .movie-info-overlay {
        transform: translateY(0);
    }
    
    .movie-title-small {
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 0.25rem;
    }
    
    .movie-rating-small {
        font-size: 0.8rem;
        color: #FFD700;
    }
    
    /* Main container styling */
    .stApp {
        background: #0C0C0C;
    }
    
    /* Custom scrollbar for main content */
    ::-webkit-scrollbar {
        width: 12px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0C0C0C;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #E50914;
        border-radius: 6px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #F40612;
    }
    
    /* Remove default Streamlit styling */
    .main .block-container {
        padding-top: 0;
        max-width: 100%;
    }
    
    /* Hero carousel dots */
    .carousel-dots {
        display: flex;
        gap: 0.5rem;
        justify-content: center;
        padding: 1rem;
        position: absolute;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 3;
    }
    
    .carousel-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.5);
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .carousel-dot.active {
        width: 24px;
        border-radius: 4px;
        background: #E50914;
    }
    
    /* Movie detail card */
    .movie-detail-card {
        background: #0C0C0C;
        border-radius: 8px;
        overflow: hidden;
        margin: 2rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'recommender' not in st.session_state:
    st.session_state.recommender = None
if 'movies_df' not in st.session_state:
    st.session_state.movies_df = None
if 'ratings_df' not in st.session_state:
    st.session_state.ratings_df = None
if 'user_liked_movies' not in st.session_state:
    st.session_state.user_liked_movies = []
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = []
if 'selected_category' not in st.session_state:
    st.session_state.selected_category = 'All'
if 'hero_movie_index' not in st.session_state:
    st.session_state.hero_movie_index = 0


@st.cache_data
def load_data():
    """Load and cache data"""
    movies_df, ratings_df = load_sample_data()
    return movies_df, ratings_df


def initialize_recommender():
    """Initialize the hybrid recommender"""
    if st.session_state.movies_df is None or st.session_state.ratings_df is None:
        st.session_state.movies_df, st.session_state.ratings_df = load_data()
    
    content_weight = st.session_state.get('content_weight', 0.5)
    collab_weight = 1.0 - content_weight
    
    recommender = HybridRecommender(
        content_weight=content_weight,
        collaborative_weight=collab_weight
    )
    recommender.fit(st.session_state.movies_df, st.session_state.ratings_df)
    
    return recommender


def get_all_genres(movies_df):
    """Extract all unique genres"""
    all_genres = set()
    for genres_str in movies_df['genres'].dropna():
        for genre in genres_str.split(','):
            all_genres.add(genre.strip())
    return sorted(list(all_genres))


def filter_movies_by_category(movies_df, category):
    """Filter movies by category/genre"""
    if category == 'All':
        return movies_df
    return movies_df[movies_df['genres'].str.contains(category, case=False, na=False)]


# Load data and initialize recommender
if st.session_state.movies_df is None or st.session_state.ratings_df is None:
    with st.spinner("Loading..."):
        st.session_state.movies_df, st.session_state.ratings_df = load_data()
        st.session_state.recommender = initialize_recommender()

# NETFLIX-STYLE NAVIGATION BAR
st.markdown("""
    <div class="netflix-nav">
        <div class="nav-logo">CINEMACOMPASS</div>
        <div class="nav-links">
            <a href="#" class="nav-link active">Home</a>
            <a href="#" class="nav-link">Movies</a>
            <a href="#" class="nav-link">Series</a>
            <a href="#" class="nav-link">My List</a>
        </div>
        <div class="nav-icons">
            <span style="color: white; cursor: pointer;">🔍</span>
            <span style="color: white; cursor: pointer;">🔔</span>
            <span style="color: white; cursor: pointer;">👤</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# HERO SECTION
if st.session_state.movies_df is not None and len(st.session_state.movies_df) > 0:
    hero_movies = st.session_state.movies_df.head(3)
    current_hero = hero_movies.iloc[st.session_state.hero_movie_index]
    
    hero_poster = current_hero.get('poster_url', '')
    hero_bg = f"url('{hero_poster}')" if hero_poster else "linear-gradient(135deg, #1E2330, #141414)"
    
    # Generate carousel dots
    dots_html = ""
    for i in range(len(hero_movies)):
        active_class = "active" if i == st.session_state.hero_movie_index else ""
        dots_html += f'<span class="carousel-dot {active_class}"></span>'
    
    st.markdown(f"""
        <div class="hero-section" style="background-image: {hero_bg};">
            <div class="hero-overlay"></div>
            <div class="hero-content">
                <div class="hero-duration">Duration: 2h 10m</div>
                <div class="hero-rating">★ {np.random.choice([7.5, 8.0, 8.5, 9.0])} {current_hero.get('genres', 'Action').split(',')[0]} | {current_hero.get('director', 'Director')}</div>
                <div class="hero-title">{current_hero['title']}</div>
                <div class="hero-description">
                    Experience the ultimate movie recommendation system powered by AI. 
                    Discover movies tailored to your taste with our hybrid filtering technology.
                </div>
                <div class="hero-buttons">
                    <button class="btn-watch">► WATCH</button>
                    <button class="btn-add">+ ADD LIST</button>
                </div>
            </div>
            <div class="carousel-dots">
                {dots_html}
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Hero carousel navigation
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        hero_cols = st.columns(len(hero_movies))
        for i, col in enumerate(hero_cols):
            with col:
                if st.button(f"{i+1}", key=f"hero_{i}"):
                    st.session_state.hero_movie_index = i
                    st.rerun()

# MAIN CONTENT AREA
st.markdown('<div style="background: #141414; min-height: 100vh; padding-top: 2rem;">', unsafe_allow_html=True)

# TRENDS NOW SECTION
st.markdown("""
    <div class="section-header">
        <div class="section-title">
            📈 Trends Now
        </div>
        <div class="section-tabs">
            <span class="section-tab active">Popular</span>
            <span class="section-tab">Premieres</span>
            <span class="section-tab">Recently Added</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# Category filters
genres = get_all_genres(st.session_state.movies_df)
genre_cols = st.columns(min(len(genres) + 1, 10))
with genre_cols[0]:
    if st.button("All", key="cat_all", use_container_width=True):
        st.session_state.selected_category = 'All'
        st.rerun()

for idx, genre in enumerate(genres[:9]):
    with genre_cols[min(idx + 1, 9)]:
        is_active = st.session_state.selected_category == genre
        if st.button(genre, key=f"cat_{genre}", use_container_width=True, type="primary" if is_active else "secondary"):
            st.session_state.selected_category = genre
            st.rerun()

# Filtered movies for trends
filtered_movies = filter_movies_by_category(st.session_state.movies_df, st.session_state.selected_category)
trending_movies = filtered_movies.head(10)

# Movie row using Streamlit columns
cols = st.columns(min(len(trending_movies), 10))
for idx, (_, movie) in enumerate(trending_movies.iterrows()):
    if idx >= len(cols):
        break
    with cols[idx]:
        poster_url = movie.get('poster_url', '')
        rating = np.random.choice([7.5, 8.0, 8.5, 9.0])
        try:
            if poster_url:
                st.image(poster_url, use_container_width=True)
            else:
                st.markdown('<div style="height: 300px; background: #141414; display: flex; align-items: center; justify-content: center; font-size: 3rem; border-radius: 4px; transition: transform 0.3s ease;">🎬</div>', unsafe_allow_html=True)
        except:
            st.markdown('<div style="height: 300px; background: #141414; display: flex; align-items: center; justify-content: center; font-size: 3rem; border-radius: 4px; transition: transform 0.3s ease;">🎬</div>', unsafe_allow_html=True)
        st.caption(f"**{movie['title']}**")
        st.caption(f"★ {rating}")

# RECOMMENDATIONS SECTION
st.markdown("""
    <div class="section-header">
        <div class="section-title">
            🎯 Your Recommendations
        </div>
        <div class="section-tabs">
            <span class="section-tab active">For You</span>
            <span class="section-tab">Trending</span>
            <span class="section-tab">Top Rated</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# Sidebar for recommendation settings
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    st.markdown('<p style="color: #F5F5F5; font-size: 0.9rem; margin-bottom: 1rem;">Adjust recommendation preferences</p>', unsafe_allow_html=True)
    content_weight = st.slider(
        "Content-Based Weight",
        0.0, 1.0, 0.5, 0.1,
        help="Adjust the balance between content-based and collaborative filtering"
    )
    st.session_state.content_weight = content_weight
    
    # Display formatted user info if available (hide ugly UUIDs)
    if 'user_id' in st.session_state and st.session_state.get('user_id'):
        formatted_id = format_id_for_display(st.session_state['user_id'], 'user')
        st.markdown(f'<p style="color: #B8B8B8; font-size: 0.85rem; margin-top: 1rem;">👤 {formatted_id}</p>', unsafe_allow_html=True)
    
    if st.session_state.recommender is None or st.session_state.get('content_weight') != content_weight:
        with st.spinner("Training model..."):
            st.session_state.recommender = initialize_recommender()
    
    st.markdown("---")
    st.markdown("### 🎭 Select Movies")
    
    movie_options = st.session_state.movies_df['title'].tolist()
    selected_movies = st.multiselect(
        "Choose movies you like:",
        movie_options,
        default=st.session_state.user_liked_movies,
        label_visibility="collapsed"
    )
    st.session_state.user_liked_movies = selected_movies
    
    if st.button("🚀 Get Recommendations", type="primary", use_container_width=True) and selected_movies:
        movie_dict = dict(zip(st.session_state.movies_df['title'], st.session_state.movies_df['movie_id']))
        liked_ids = [movie_dict[movie] for movie in selected_movies]
        
        with st.spinner("Generating recommendations..."):
            recommendations = st.session_state.recommender.get_recommendations(
                liked_movies=liked_ids,
                top_n=10
            )
            st.session_state.recommendations = recommendations

# Display recommendations using Streamlit columns
if st.session_state.recommendations:
    rec_cols = st.columns(min(len(st.session_state.recommendations), 10))
    for idx, rec in enumerate(st.session_state.recommendations[:10]):
        if idx >= len(rec_cols):
            break
        movie_info = st.session_state.movies_df[
            st.session_state.movies_df['movie_id'] == rec['movie_id']
        ].iloc[0]
        poster_url = movie_info.get('poster_url', '')
        score_rating = int(rec['score'] * 10) / 2 + 7  # Convert to 7-9.5 range
        
        with rec_cols[idx]:
            try:
                if poster_url:
                    st.image(poster_url, use_container_width=True)
                else:
                    st.markdown('<div style="height: 300px; background: #141414; display: flex; align-items: center; justify-content: center; font-size: 3rem; border-radius: 4px; transition: transform 0.3s ease;">🎬</div>', unsafe_allow_html=True)
            except:
                st.markdown('<div style="height: 300px; background: #141414; display: flex; align-items: center; justify-content: center; font-size: 3rem; border-radius: 4px; transition: transform 0.3s ease;">🎬</div>', unsafe_allow_html=True)
            st.caption(f"**{movie_info['title']}**")
            st.caption(f"★ {score_rating:.1f}")
            with st.expander("ℹ️"):
                st.write(rec['reason'])
else:
    # Show popular movies if no recommendations
    popular_movies = st.session_state.movies_df.head(10)
    pop_cols = st.columns(min(len(popular_movies), 10))
    for idx, (_, movie) in enumerate(popular_movies.iterrows()):
        if idx >= len(pop_cols):
            break
        poster_url = movie.get('poster_url', '')
        rating = np.random.choice([7.5, 8.0, 8.5, 9.0])
        
        with pop_cols[idx]:
            try:
                if poster_url:
                    st.image(poster_url, use_container_width=True)
                else:
                    st.markdown('<div style="height: 300px; background: #141414; display: flex; align-items: center; justify-content: center; font-size: 3rem; border-radius: 4px; transition: transform 0.3s ease;">🎬</div>', unsafe_allow_html=True)
            except:
                st.markdown('<div style="height: 300px; background: #141414; display: flex; align-items: center; justify-content: center; font-size: 3rem; border-radius: 4px; transition: transform 0.3s ease;">🎬</div>', unsafe_allow_html=True)
            st.caption(f"**{movie['title']}**")
            st.caption(f"★ {rating}")

# MOVIES SECTION
st.markdown("""
    <div class="section-header">
        <div class="section-title">
            🎬 Movies
        </div>
        <div class="section-tabs">
            <span class="section-tab active">All Movies</span>
            <span class="section-tab">New Releases</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# All movies row using Streamlit columns
all_movies = st.session_state.movies_df.head(20)  # Limit to 20 for display
all_cols = st.columns(min(len(all_movies), 10))
for idx, (_, movie) in enumerate(all_movies.iterrows()):
    if idx >= len(all_cols):
        # Create new row if needed
        if idx % 10 == 0 and idx > 0:
            all_cols = st.columns(min(len(all_movies) - idx, 10))
            idx = idx % 10
        else:
            continue
    
    poster_url = movie.get('poster_url', '')
    rating = np.random.choice([7.0, 7.5, 8.0, 8.5])
    
    with all_cols[idx % 10]:
        try:
            if poster_url:
                st.image(poster_url, use_container_width=True)
            else:
                st.markdown('<div style="height: 300px; background: #141414; display: flex; align-items: center; justify-content: center; font-size: 3rem; border-radius: 4px; transition: transform 0.3s ease;">🎬</div>', unsafe_allow_html=True)
        except:
            st.markdown('<div style="height: 300px; background: #141414; display: flex; align-items: center; justify-content: center; font-size: 3rem; border-radius: 4px; transition: transform 0.3s ease;">🎬</div>', unsafe_allow_html=True)
        st.caption(f"**{movie['title']}**")
        st.caption(f"★ {rating}")
        with st.expander("ℹ️"):
            st.write(f"**Genre:** {movie.get('genres', 'N/A')}")
            st.write(f"**Director:** {movie.get('director', 'N/A')}")

st.markdown('</div>', unsafe_allow_html=True)
