"""
Movie model
"""

from sqlalchemy import Column, String, Integer, Float, Text, DateTime
from sqlalchemy.sql import func
from .database import Base


class Movie(Base):
    __tablename__ = "movies"
    
    movie_id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    genres = Column(String)
    director = Column(String)
    cast = Column(Text)
    overview = Column(Text)
    poster_url = Column(String)
    backdrop_url = Column(String)
    year = Column(Integer)
    runtime = Column(Integer)  # minutes
    vote_average = Column(Float)
    vote_count = Column(Integer)
    tags = Column(Text)
    tmdb_id = Column(String, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

