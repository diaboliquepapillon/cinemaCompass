"""
Watchlist model
"""

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base
import uuid


class Watchlist(Base):
    __tablename__ = "watchlists"
    
    watchlist_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False, index=True)
    movie_id = Column(String, ForeignKey("movies.movie_id"), nullable=False, index=True)
    status = Column(String, default="want_to_watch")  # want_to_watch, watching, watched
    added_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user = relationship("User", backref="watchlists")
    movie = relationship("Movie", backref="watchlists")

