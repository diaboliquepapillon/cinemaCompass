"""
Advanced feature engineering: embeddings for genres, directors, cast, and text
Uses Word2Vec, FastText, and sentence transformers for rich representations
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple
import logging
from pathlib import Path
import pickle
import warnings
warnings.filterwarnings('ignore')

try:
    from gensim.models import Word2Vec, FastText
    from gensim.models.keyedvectors import KeyedVectors
    GENSIM_AVAILABLE = True
except ImportError:
    GENSIM_AVAILABLE = False
    logging.warning("gensim not available. Install with: pip install gensim")

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logging.warning("sentence-transformers not available. Install with: pip install sentence-transformers")

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GenreEmbedder:
    """Generate embeddings for movie genres"""
    
    def __init__(self, embedding_dim: int = 50):
        self.embedding_dim = embedding_dim
        self.genre_to_idx = {}
        self.idx_to_genre = {}
        self.embeddings = None
        
    def fit(self, genres_list: List[str]):
        """
        Fit genre embeddings from list of genre strings
        
        Args:
            genres_list: List of comma-separated genre strings
        """
        # Extract all unique genres
        all_genres = set()
        for genres_str in genres_list:
            if pd.notna(genres_str) and genres_str:
                for genre in str(genres_str).split(','):
                    all_genres.add(genre.strip())
        
        all_genres = sorted(list(all_genres))
        self.genre_to_idx = {genre: idx for idx, genre in enumerate(all_genres)}
        self.idx_to_genre = {idx: genre for genre, idx in self.genre_to_idx.items()}
        
        # Create one-hot encoding then reduce dimensions
        num_genres = len(all_genres)
        one_hot = np.eye(num_genres)
        
        # Use PCA-like reduction (or could train embeddings)
        from sklearn.decomposition import PCA
        pca = PCA(n_components=self.embedding_dim)
        self.embeddings = pca.fit_transform(one_hot)
        
        logger.info(f"Fitted genre embeddings: {num_genres} genres → {self.embedding_dim} dims")
        
    def transform(self, genres_str: str) -> np.ndarray:
        """
        Transform genre string to embedding vector
        
        Args:
            genres_str: Comma-separated genre string
        
        Returns:
            Embedding vector (embedding_dim,)
        """
        if not genres_str or pd.isna(genres_str):
            return np.zeros(self.embedding_dim)
        
        genres = [g.strip() for g in str(genres_str).split(',')]
        genre_vectors = []
        
        for genre in genres:
            if genre in self.genre_to_idx:
                idx = self.genre_to_idx[genre]
                genre_vectors.append(self.embeddings[idx])
        
        if genre_vectors:
            # Average pooling for multi-genre movies
            return np.mean(genre_vectors, axis=0)
        else:
            return np.zeros(self.embedding_dim)
    
    def save(self, filepath: str):
        """Save embeddings to disk"""
        data = {
            'genre_to_idx': self.genre_to_idx,
            'idx_to_genre': self.idx_to_genre,
            'embeddings': self.embeddings,
            'embedding_dim': self.embedding_dim
        }
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
        logger.info(f"Saved genre embeddings to {filepath}")
    
    def load(self, filepath: str):
        """Load embeddings from disk"""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        self.genre_to_idx = data['genre_to_idx']
        self.idx_to_genre = data['idx_to_genre']
        self.embeddings = data['embeddings']
        self.embedding_dim = data['embedding_dim']
        logger.info(f"Loaded genre embeddings from {filepath}")


class DirectorCastEmbedder:
    """Generate embeddings for directors and cast using Word2Vec"""
    
    def __init__(self, embedding_dim: int = 100, use_fasttext: bool = False):
        self.embedding_dim = embedding_dim
        self.use_fasttext = use_fasttext and GENSIM_AVAILABLE
        self.model = None
        
    def fit(self, directors: List[str], cast_lists: List[str]):
        """
        Train Word2Vec model on directors and cast
        
        Args:
            directors: List of director names
            cast_lists: List of comma-separated cast strings
        """
        if not GENSIM_AVAILABLE:
            logger.warning("gensim not available. Using simple encoding instead.")
            self._fit_simple(directors, cast_lists)
            return
        
        # Prepare sentences (each person is a word)
        sentences = []
        
        # Add directors as single-word sentences
        for director in directors:
            if pd.notna(director) and director:
                # Split compound names, treat as one token
                sentences.append([director.lower().replace(' ', '_')])
        
        # Add cast members
        for cast_str in cast_lists:
            if pd.notna(cast_str) and cast_str:
                cast_members = [c.strip().lower().replace(' ', '_') 
                               for c in str(cast_str).split(',')[:10]]
                if cast_members:
                    sentences.append(cast_members)
        
        if not sentences:
            self._fit_simple(directors, cast_lists)
            return
        
        # Train Word2Vec or FastText
        if self.use_fasttext:
            self.model = FastText(sentences=sentences, vector_size=self.embedding_dim,
                                window=5, min_count=1, workers=4, sg=1)
        else:
            self.model = Word2Vec(sentences=sentences, vector_size=self.embedding_dim,
                                 window=5, min_count=1, workers=4, sg=1)
        
        logger.info(f"Trained Word2Vec model: {len(self.model.wv)} unique people")
    
    def _fit_simple(self, directors: List[str], cast_lists: List[str]):
        """Fallback simple encoding"""
        all_people = set()
        for director in directors:
            if pd.notna(director):
                all_people.add(director.lower().strip())
        for cast_str in cast_lists:
            if pd.notna(cast_str):
                for person in str(cast_str).split(','):
                    all_people.add(person.strip().lower())
        
        # Simple label encoding fallback
        self.people_to_idx = {p: idx for idx, p in enumerate(sorted(all_people))}
        logger.info(f"Using simple encoding: {len(self.people_to_idx)} unique people")
    
    def get_director_embedding(self, director: str) -> np.ndarray:
        """Get embedding for a director"""
        if not director or pd.isna(director):
            return np.zeros(self.embedding_dim)
        
        if self.model:
            key = director.lower().replace(' ', '_')
            if key in self.model.wv:
                return self.model.wv[key]
        
        # Fallback
        return np.zeros(self.embedding_dim)
    
    def get_cast_embedding(self, cast_str: str) -> np.ndarray:
        """Get embedding for cast (average pooling)"""
        if not cast_str or pd.isna(cast_str):
            return np.zeros(self.embedding_dim)
        
        cast_members = [c.strip().lower().replace(' ', '_') 
                       for c in str(cast_str).split(',')[:10]]
        
        if self.model and cast_members:
            embeddings = []
            for person in cast_members:
                if person in self.model.wv:
                    embeddings.append(self.model.wv[person])
            
            if embeddings:
                return np.mean(embeddings, axis=0)
        
        return np.zeros(self.embedding_dim)
    
    def save(self, filepath: str):
        """Save model to disk"""
        if self.model:
            self.model.save(str(filepath))
            logger.info(f"Saved Word2Vec model to {filepath}")
    
    def load(self, filepath: str):
        """Load model from disk"""
        if GENSIM_AVAILABLE:
            if self.use_fasttext:
                self.model = FastText.load(str(filepath))
            else:
                self.model = Word2Vec.load(str(filepath))
            logger.info(f"Loaded Word2Vec model from {filepath}")


class TextEmbedder:
    """Generate embeddings for movie descriptions using TF-IDF and sentence transformers"""
    
    def __init__(self, use_transformer: bool = True, tfidf_max_features: int = 300):
        self.use_transformer = use_transformer and SENTENCE_TRANSFORMERS_AVAILABLE
        self.tfidf_max_features = tfidf_max_features
        self.tfidf = TfidfVectorizer(max_features=tfidf_max_features, stop_words='english')
        self.transformer_model = None
        
        if self.use_transformer:
            try:
                # Use a lightweight model for faster inference
                self.transformer_model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Loaded sentence transformer model")
            except Exception as e:
                logger.warning(f"Could not load transformer model: {e}")
                self.use_transformer = False
    
    def fit(self, texts: List[str]):
        """
        Fit TF-IDF vectorizer
        
        Args:
            texts: List of text descriptions
        """
        # Clean texts
        clean_texts = [str(text) if pd.notna(text) else '' for text in texts]
        self.tfidf.fit(clean_texts)
        logger.info(f"Fitted TF-IDF vectorizer: {len(self.tfidf.vocabulary_)} features")
    
    def transform(self, text: str) -> np.ndarray:
        """
        Transform text to embedding vector
        
        Args:
            text: Text description
        
        Returns:
            Embedding vector
        """
        if not text or pd.isna(text):
            text = ''
        
        # Use transformer if available (better quality)
        if self.use_transformer and self.transformer_model:
            embedding = self.transformer_model.encode(str(text))
            return embedding
        
        # Fallback to TF-IDF
        tfidf_vec = self.tfidf.transform([str(text)]).toarray()[0]
        return tfidf_vec
    
    def save(self, filepath: str):
        """Save vectorizer to disk"""
        import joblib
        joblib.dump(self.tfidf, filepath)
        logger.info(f"Saved TF-IDF vectorizer to {filepath}")
    
    def load(self, filepath: str):
        """Load vectorizer from disk"""
        import joblib
        self.tfidf = joblib.load(filepath)
        logger.info(f"Loaded TF-IDF vectorizer from {filepath}")


class FeatureExtractor:
    """Main feature extraction pipeline combining all embeddings"""
    
    def __init__(self):
        self.genre_embedder = GenreEmbedder(embedding_dim=50)
        self.director_cast_embedder = DirectorCastEmbedder(embedding_dim=100)
        self.text_embedder = TextEmbedder()
        
    def fit(self, movies_df: pd.DataFrame):
        """
        Fit all embedding models on movie data
        
        Args:
            movies_df: DataFrame with columns: genres, director, cast, overview
        """
        logger.info("Fitting feature extractors...")
        
        # Fit genre embeddings
        if 'genres' in movies_df.columns:
            self.genre_embedder.fit(movies_df['genres'].fillna('').tolist())
        
        # Fit director/cast embeddings
        directors = movies_df.get('director', pd.Series()).fillna('').tolist()
        cast_lists = movies_df.get('cast', pd.Series()).fillna('').tolist()
        self.director_cast_embedder.fit(directors, cast_lists)
        
        # Fit text embeddings
        texts = movies_df.get('overview', pd.Series()).fillna('').tolist()
        if not texts or all(not t for t in texts):
            # Fallback to title + genres if no overview
            texts = (movies_df.get('title', '') + ' ' + 
                    movies_df.get('genres', '').fillna('')).tolist()
        self.text_embedder.fit(texts)
        
        logger.info("Feature extractors fitted successfully")
    
    def extract_features(self, movie_row: pd.Series) -> np.ndarray:
        """
        Extract combined feature vector for a movie
        
        Args:
            movie_row: Series with movie data
        
        Returns:
            Concatenated feature vector
        """
        features = []
        
        # Genre embedding
        genres_str = movie_row.get('genres', '')
        genre_vec = self.genre_embedder.transform(genres_str)
        features.append(genre_vec)
        
        # Director embedding
        director = movie_row.get('director', '')
        director_vec = self.director_cast_embedder.get_director_embedding(director)
        features.append(director_vec)
        
        # Cast embedding
        cast_str = movie_row.get('cast', '')
        cast_vec = self.director_cast_embedder.get_cast_embedding(cast_str)
        features.append(cast_vec)
        
        # Text embedding
        text = movie_row.get('overview', '')
        if not text:
            text = str(movie_row.get('title', '')) + ' ' + str(genres_str)
        text_vec = self.text_embedder.transform(text)
        features.append(text_vec)
        
        # Concatenate all features
        combined = np.concatenate(features)
        return combined
    
    def extract_all_features(self, movies_df: pd.DataFrame) -> np.ndarray:
        """
        Extract features for all movies
        
        Args:
            movies_df: DataFrame of movies
        
        Returns:
            Feature matrix (n_movies, n_features)
        """
        logger.info(f"Extracting features for {len(movies_df)} movies...")
        feature_matrix = []
        
        for _, row in movies_df.iterrows():
            features = self.extract_features(row)
            feature_matrix.append(features)
        
        feature_matrix = np.array(feature_matrix)
        logger.info(f"Feature matrix shape: {feature_matrix.shape}")
        return feature_matrix
    
    def save(self, directory: str):
        """Save all models to directory"""
        dir_path = Path(directory)
        dir_path.mkdir(parents=True, exist_ok=True)
        
        self.genre_embedder.save(str(dir_path / 'genre_embeddings.pkl'))
        self.director_cast_embedder.save(str(dir_path / 'director_cast_model.bin'))
        self.text_embedder.save(str(dir_path / 'text_vectorizer.pkl'))
        
        logger.info(f"Saved all feature extractors to {directory}")
    
    def load(self, directory: str):
        """Load all models from directory"""
        dir_path = Path(directory)
        
        self.genre_embedder.load(str(dir_path / 'genre_embeddings.pkl'))
        self.director_cast_embedder.load(str(dir_path / 'director_cast_model.bin'))
        self.text_embedder.load(str(dir_path / 'text_vectorizer.pkl'))
        
        logger.info(f"Loaded all feature extractors from {directory}")

