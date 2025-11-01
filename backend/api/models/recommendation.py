"""
Recommendation model (for logging recommendations)
"""

from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base


class Recommendation(Base):
    __tablename__ = "recommendations"
    
    recommendation_id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False, index=True)
    movie_id = Column(String, ForeignKey("movies.movie_id"), nullable=False, index=True)
    score = Column(Float, nullable=False)
    explanation = Column(Text)
    generated_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user = relationship("User", backref="recommendations")
    movie = relationship("Movie", backref="recommendations")

