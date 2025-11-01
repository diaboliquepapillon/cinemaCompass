"""
Database models
"""

from .database import Base, init_db
from .user import User
from .movie import Movie
from .rating import Rating
from .watchlist import Watchlist
from .recommendation import Recommendation

__all__ = ['Base', 'init_db', 'User', 'Movie', 'Rating', 'Watchlist', 'Recommendation']

