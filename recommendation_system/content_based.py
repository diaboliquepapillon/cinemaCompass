"""
Content-based filtering using movie metadata
"""

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple
import warnings
warnings.filterwarnings('ignore')


class ContentBasedFilter:
    """Content-based recommendation system using metadata"""
    
    def __init__(self):
        self.movies_df = None
        self.content_matrix = None
        self.tfidf = TfidfVectorizer(max_features=5000, stop_words='english')
        self.similarity_matrix = None
        
    def prepare_data(self, movies_df: pd.DataFrame):
        """Prepare movie data and create content features"""
        self.movies_df = movies_df.copy()
        
        # Combine metadata into a single text feature
        self.movies_df['combined_features'] = (
            self.movies_df['genres'].fillna('') + ' ' +
            self.movies_df['director'].fillna('') + ' ' +
            self.movies_df['cast'].fillna('') + ' ' +
            self.movies_df['tags'].fillna('')
        ).str.lower()
        
        # Create TF-IDF matrix
        self.content_matrix = self.tfidf.fit_transform(self.movies_df['combined_features'])
        
        # Calculate similarity matrix
        self.similarity_matrix = cosine_similarity(self.content_matrix)
        
        return self
    
    def get_recommendations(self, movie_id: str, top_n: int = 10) -> List[Dict]:
        """Get content-based recommendations for a movie"""
        if self.movies_df is None or self.similarity_matrix is None:
            raise ValueError("Model not fitted. Call prepare_data() first.")
        
        # Find movie index
        movie_idx = self.movies_df[self.movies_df['movie_id'] == movie_id].index
        if len(movie_idx) == 0:
            return []
        
        movie_idx = movie_idx[0]
        
        # Get similarity scores
        similarity_scores = list(enumerate(self.similarity_matrix[movie_idx]))
        
        # Sort by similarity
        similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
        
        # Get top N recommendations (excluding the movie itself)
        recommendations = []
        for idx, score in similarity_scores[1:top_n+1]:
            movie_data = self.movies_df.iloc[idx].to_dict()
            recommendations.append({
                'movie_id': movie_data['movie_id'],
                'title': movie_data.get('title', ''),
                'score': float(score),
                'reason': self._generate_reason(movie_idx, idx)
            })
        
        return recommendations
    
    def _generate_reason(self, source_idx: int, target_idx: int) -> str:
        """Generate explanation for why this movie is recommended"""
        source_movie = self.movies_df.iloc[source_idx]
        target_movie = self.movies_df.iloc[target_idx]
        
        reasons = []
        
        # Check genre similarity
        source_genres = set(str(source_movie.get('genres', '')).lower().split(','))
        target_genres = set(str(target_movie.get('genres', '')).lower().split(','))
        common_genres = source_genres.intersection(target_genres)
        if common_genres:
            reasons.append(f"Similar genres: {', '.join(list(common_genres)[:2])}")
        
        # Check director
        if (source_movie.get('director') and target_movie.get('director') and
            str(source_movie.get('director')).lower() == str(target_movie.get('director')).lower()):
            reasons.append(f"Same director: {target_movie.get('director')}")
        
        # Check cast overlap
        source_cast = set(str(source_movie.get('cast', '')).lower().split(','))
        target_cast = set(str(target_movie.get('cast', '')).lower().split(','))
        common_cast = source_cast.intersection(target_cast)
        if common_cast:
            reasons.append(f"Shared cast: {', '.join(list(common_cast)[:2])}")
        
        if not reasons:
            reasons.append("Similar themes and style")
        
        return "; ".join(reasons)
    
    def get_user_profile_recommendations(self, liked_movies: List[str], top_n: int = 10) -> List[Dict]:
        """Get recommendations based on user's liked movies"""
        if len(liked_movies) == 0:
            return []
        
        # Get recommendations for each liked movie
        all_recommendations = {}
        for movie_id in liked_movies:
            recs = self.get_recommendations(movie_id, top_n=top_n*2)
            for rec in recs:
                if rec['movie_id'] not in liked_movies:
                    if rec['movie_id'] not in all_recommendations:
                        all_recommendations[rec['movie_id']] = {
                            'movie_id': rec['movie_id'],
                            'title': rec['title'],
                            'score': 0.0,
                            'reasons': []
                        }
                    all_recommendations[rec['movie_id']]['score'] += rec['score']
                    all_recommendations[rec['movie_id']]['reasons'].append(rec['reason'])
        
        # Normalize scores by number of liked movies
        for movie_id in all_recommendations:
            all_recommendations[movie_id]['score'] /= len(liked_movies)
        
        # Sort by score and return top N
        sorted_recs = sorted(all_recommendations.values(), key=lambda x: x['score'], reverse=True)
        
        # Format final recommendations
        final_recs = []
        for rec in sorted_recs[:top_n]:
            # Get the most relevant reason
            main_reason = rec['reasons'][0] if rec['reasons'] else "Similar to your preferences"
            final_recs.append({
                'movie_id': rec['movie_id'],
                'title': rec['title'],
                'score': rec['score'],
                'reason': main_reason
            })
        
        return final_recs

