-- CinemaCompass PostgreSQL Database Schema
-- This schema supports the hybrid recommendation system

-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL,
    name VARCHAR,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);

-- Movies table
CREATE TABLE IF NOT EXISTS movies (
    movie_id VARCHAR PRIMARY KEY,
    title VARCHAR NOT NULL,
    genres VARCHAR,
    director VARCHAR,
    cast TEXT,
    overview TEXT,
    poster_url VARCHAR,
    backdrop_url VARCHAR,
    year INTEGER,
    runtime INTEGER,  -- minutes
    vote_average FLOAT,
    vote_count INTEGER,
    tags TEXT,
    tmdb_id VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX idx_movies_title ON movies(title);
CREATE INDEX idx_movies_tmdb_id ON movies(tmdb_id);
CREATE INDEX idx_movies_year ON movies(year);

-- Ratings table
CREATE TABLE IF NOT EXISTS ratings (
    rating_id VARCHAR PRIMARY KEY,
    user_id VARCHAR NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    movie_id VARCHAR NOT NULL REFERENCES movies(movie_id) ON DELETE CASCADE,
    rating FLOAT NOT NULL CHECK (rating >= 0.5 AND rating <= 5.0),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, movie_id)
);

CREATE INDEX idx_ratings_user_id ON ratings(user_id);
CREATE INDEX idx_ratings_movie_id ON ratings(movie_id);
CREATE INDEX idx_ratings_rating ON ratings(rating);

-- Watchlists table
CREATE TABLE IF NOT EXISTS watchlists (
    watchlist_id VARCHAR PRIMARY KEY,
    user_id VARCHAR NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    movie_id VARCHAR NOT NULL REFERENCES movies(movie_id) ON DELETE CASCADE,
    status VARCHAR DEFAULT 'want_to_watch',  -- want_to_watch, watching, watched
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, movie_id)
);

CREATE INDEX idx_watchlists_user_id ON watchlists(user_id);
CREATE INDEX idx_watchlists_movie_id ON watchlists(movie_id);
CREATE INDEX idx_watchlists_status ON watchlists(status);

-- Recommendations table (for logging)
CREATE TABLE IF NOT EXISTS recommendations (
    recommendation_id VARCHAR PRIMARY KEY,
    user_id VARCHAR NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    movie_id VARCHAR NOT NULL REFERENCES movies(movie_id) ON DELETE CASCADE,
    score FLOAT NOT NULL,
    explanation TEXT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_recommendations_user_id ON recommendations(user_id);
CREATE INDEX idx_recommendations_movie_id ON recommendations(movie_id);
CREATE INDEX idx_recommendations_generated_at ON recommendations(generated_at);

-- Feedback table (for recommendation feedback)
CREATE TABLE IF NOT EXISTS feedback (
    feedback_id VARCHAR PRIMARY KEY,
    user_id VARCHAR NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    movie_id VARCHAR NOT NULL REFERENCES movies(movie_id) ON DELETE CASCADE,
    feedback_type VARCHAR NOT NULL,  -- 'like', 'dislike', 'dismiss'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_feedback_user_id ON feedback(user_id);
CREATE INDEX idx_feedback_movie_id ON feedback(movie_id);

-- User sessions table (for Redis fallback)
CREATE TABLE IF NOT EXISTS user_sessions (
    session_id VARCHAR PRIMARY KEY,
    user_id VARCHAR NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    token VARCHAR NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_sessions_token ON user_sessions(token);
CREATE INDEX idx_sessions_expires_at ON user_sessions(expires_at);

