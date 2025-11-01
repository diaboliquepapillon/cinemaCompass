"""
Database module (re-export for convenience)
"""

from .models.database import get_db, init_db

__all__ = ['get_db', 'init_db']

