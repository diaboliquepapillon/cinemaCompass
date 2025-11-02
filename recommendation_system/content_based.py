"""
Content-based filtering using rich metadata (genre, director, cast, tags)
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentBasedRecommender:
    """Content-based filtering using TF-IDF on rich movie metadata"""
    
    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=5000,
            ngram_range=(1, 2)
        )
        self.similarity_matrix = None
        self.movies_df = None
        
    def _prepare_features(self, movies_df: pd.DataFrame) -> pd.Series:
        """
        Combine rich metadata into a single feature string:
        - Genres
        - Director
        - Cast (top 5)
        - Tags/keywords
        - Overview
        """
        features = []
        
        for _, movie in movies_df.iterrows():
            feature_parts = []
            
            # Genres
            if pd.notna(movie.get('genres')):
                if isinstance(movie['genres'], str):
                    feature_parts.append(movie['genres'])
                elif isinstance(movie['genres'], list):
                    feature_parts.append(' '.join(movie['genres']))
            
            # Director
            if pd.notna(movie.get('director')):
                feature_parts.append(str(movie['director']))
            
            # Cast (top 5)
            if pd.notna(movie.get('cast')):
                cast_list = movie['cast']
                if isinstance(cast_list, str):
                    # Parse comma-separated string
                    cast = [c.strip() for c in cast_list.split(',')][:5]
                elif isinstance(cast_list, list):
                    cast = cast_list[:5]
                else:
                    cast = []
                feature_parts.append(' '.join(cast))
            
            # Tags/Keywords
            if pd.notna(movie.get('tags')) or pd.notna(movie.get('keywords')):
                tags = movie.get('tags') or movie.get('keywords') or ''
                if isinstance(tags, list):
                    tags = ' '.join(tags)
                feature_parts.append(str(tags))
            
            # Overview/Description
            if pd.notna(movie.get('overview')):
                feature_parts.append(str(movie['overview']))
            
            # Combine all features
            combined = ' '.join(filter(None, feature_parts))
            features.append(combined if combined else '')
        
        return pd.Series(features)
    
    def fit(self, movies_df: pd.DataFrame):
        """Fit the content-based model on movie metadata"""
        self.movies_df = movies_df.copy()
        
        # Prepare feature strings
        logger.info("Preparing rich metadata features...")
        features = self._prepare_features(movies_df)
        
        # Fit TF-IDF vectorizer
        logger.info("Fitting TF-IDF vectorizer...")
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(features)
        
        # Compute cosine similarity matrix
        logger.info("Computing similarity matrix...")
        self.similarity_matrix = cosine_similarity(tfidf_matrix)
        
        logger.info("Content-based model fitted successfully.")
        return self
    
    def get_similar_movies(
        self, 
        movie_id: str, 
        top_n: int = 10,
        exclude_self: bool = True
    ) -> List[Dict]:
        """Get similar movies based on content"""
        if self.similarity_matrix is None:
            raise ValueError("Model must be fitted first. Call fit() before get_similar_movies()")
        
        # Find movie index
        movie_idx = self.movies_df[self.movies_df['id'] == movie_id].index
        if len(movie_idx) == 0:
            logger.warning(f"Movie ID {movie_id} not found")
            return []
        
        movie_idx = movie_idx[0]
        
        # Get similarity scores
        sim_scores = list(enumerate(self.similarity_matrix[movie_idx]))
        
        # Sort by similarity
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        # Exclude self and get top N
        start_idx = 1 if exclude_self else 0
        sim_scores = sim_scores[start_idx:start_idx + top_n]
        
        # Prepare results
        recommendations = []
        for idx, score in sim_scores:
            movie = self.movies_df.iloc[idx]
            recommendations.append({
                'movie_id': movie.get('id'),
                'title': movie.get('title'),
                'similarity_score': float(score),
                'genres': movie.get('genres'),
                'poster_path': movie.get('poster_path'),
                'vote_average': movie.get('vote_average', 0),
                'reason': f"Similar in genres, cast, and storyline"
            })
        
        return recommendations
    
    def get_recommendations_from_multiple(
        self,
        movie_ids: List[str],
        top_n: int = 10
    ) -> List[Dict]:
        """Get recommendations based on multiple liked movies"""
        all_recommendations = {}
        
        for movie_id in movie_ids:
            similar = self.get_similar_movies(movie_id, top_n=top_n * 2, exclude_self=True)
            
            for rec in similar:
                rec_id = rec['movie_id']
                if rec_id not in all_recommendations:
                    all_recommendations[rec_id] = {
                        'movie_id': rec_id,
                        'title': rec['title'],
                        'similarity_score': rec['similarity_score'],
                        'count': 1,
                        'genres': rec['genres'],
                        'poster_path': rec['poster_path'],
                        'vote_average': rec['vote_average']
                    }
                else:
                    # Aggregate scores from multiple movies
                    all_recommendations[rec_id]['similarity_score'] += rec['similarity_score']
                    all_recommendations[rec_id]['count'] += 1
        
        # Normalize scores and sort
        for rec_id in all_recommendations:
            all_recommendations[rec_id]['similarity_score'] /= all_recommendations[rec_id]['count']
        
        # Sort by aggregated similarity score
        sorted_recs = sorted(
            all_recommendations.values(),
            key=lambda x: x['similarity_score'],
            reverse=True
        )
        
        return sorted_recs[:top_n]

