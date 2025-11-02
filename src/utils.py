"""
Utility functions for CinemaCompass
Includes ID formatting, poster fetching, and helper functions
"""

import re
import hashlib
from typing import Optional
import requests
import os


def format_user_id(user_id: str) -> str:
    """
    Convert UUID to friendly format (e.g., 'User #12345')
    Uses hash to create consistent short IDs
    """
    if not user_id:
        return "Guest"
    
    # Create a consistent short ID from UUID
    hash_obj = hashlib.md5(user_id.encode())
    hash_int = int(hash_obj.hexdigest()[:8], 16)
    short_id = (hash_int % 99999) + 1  # 1-99999 range
    
    return f"User #{short_id}"


def format_movie_id_slug(title: str, year: Optional[int] = None) -> str:
    """
    Convert movie title to URL-friendly slug
    e.g., 'The Matrix (1999)' -> 'the-matrix-1999'
    """
    # Remove year from title if present
    title_clean = re.sub(r'\s*\(\d{4}\)\s*$', '', title)
    
    # Convert to lowercase and replace spaces/special chars
    slug = re.sub(r'[^\w\s-]', '', title_clean.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    slug = slug.strip('-')
    
    # Add year if provided
    if year:
        slug = f"{slug}-{year}"
    
    return slug


def parse_movie_id_from_slug(slug: str) -> tuple[str, Optional[int]]:
    """
    Extract title and year from slug
    Returns: (title, year)
    """
    # Extract year if present
    year_match = re.search(r'-(\d{4})$', slug)
    year = int(year_match.group(1)) if year_match else None
    
    # Remove year from slug
    title_slug = re.sub(r'-\d{4}$', '', slug)
    
    # Convert back to title format
    title = title_slug.replace('-', ' ').title()
    
    return title, year


def get_poster(title: str, year: Optional[int] = None, tmdb_api_key: Optional[str] = None) -> Optional[str]:
    """
    Fetch movie poster from TMDb API
    
    Args:
        title: Movie title
        year: Release year (optional)
        tmdb_api_key: TMDb API key (optional, can use env var TMDB_API_KEY)
    
    Returns:
        Poster URL or None
    """
    api_key = tmdb_api_key or os.getenv('TMDB_API_KEY')
    if not api_key:
        return None
    
    try:
        # Search for movie
        search_url = "https://api.themoviedb.org/3/search/movie"
        params = {
            'api_key': api_key,
            'query': title,
            'year': year
        }
        
        response = requests.get(search_url, params=params, timeout=5)
        response.raise_for_status()
        
        results = response.json().get('results', [])
        if results:
            poster_path = results[0].get('poster_path')
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500{poster_path}"
        
        return None
    except Exception:
        return None


def format_id_for_display(id_value: str, id_type: str = "user") -> str:
    """
    Format any ID for user-friendly display
    
    Args:
        id_value: The ID to format
        id_type: Type of ID ('user', 'movie', or 'generic')
    
    Returns:
        Formatted ID string
    """
    if not id_value:
        return "N/A"
    
    if id_type == "user":
        return format_user_id(id_value)
    elif id_type == "movie":
        # For movies, return the ID as-is if it's not a UUID
        # Otherwise try to decode if it's a slug
        if len(id_value) > 36:  # Likely not a UUID
            return id_value
        return id_value
    else:
        # Generic: shorten UUIDs
        if len(id_value) > 20:
            hash_obj = hashlib.md5(id_value.encode())
            return f"#{hash_obj.hexdigest()[:8]}"
        return id_value


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def safe_filename(text: str) -> str:
    """Convert text to safe filename"""
    # Remove special characters
    filename = re.sub(r'[^\w\s-]', '', text)
    # Replace spaces with underscores
    filename = re.sub(r'[-\s]+', '_', filename)
    return filename.strip('_')

