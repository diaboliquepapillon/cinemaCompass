"""
Rating model
"""

from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base


class Rating(Base):
    __tablename__ = "ratings"
    
    rating_id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False, index=True)
    movie_id = Column(String, ForeignKey("movies.movie_id"), nullable=False, index=True)
    rating = Column(Float, nullable=False)  # 0.5 to 5.0
    timestamp = Column(DateTime, server_default=func.now())
    
    # Relationships
    user = relationship("User", backref="ratings")
    movie = relationship("Movie", backref="ratings")

