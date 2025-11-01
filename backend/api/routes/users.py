"""
User management routes
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
import jwt
import uuid

from ..database import get_db
from ..models import User, Watchlist, Rating

router = APIRouter()

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "cinemacompass-secret-key-change-in-production")
ALGORITHM = "HS256"


def get_current_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> str:
    """Extract user ID from JWT token"""
    from ..auth import get_current_user
    try:
        if credentials:
            return get_current_user(credentials)
    except Exception:
        pass
    # Fallback for development
    user_id = os.getenv("DEFAULT_USER_ID", "1")
    return user_id


class UserPreferences(BaseModel):
    favorite_genres: Optional[List[str]] = []
    explicit_content: Optional[bool] = True
    recommendation_style: Optional[str] = "balanced"  # popular, niche, balanced


class UserProfileResponse(BaseModel):
    user_id: str
    email: str
    name: Optional[str]
    preferences: Optional[Dict]


@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(user_id: str = Depends(get_current_user_id), db=Depends(get_db)):
    """Get user profile"""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserProfileResponse(
        user_id=str(user.user_id),
        email=user.email,
        name=user.name,
        preferences=user.preferences or {}
    )


@router.put("/preferences")
async def update_preferences(
    preferences: UserPreferences,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """Update user preferences"""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.preferences = preferences.dict()
    db.commit()
    
    return {"message": "Preferences updated", "preferences": preferences.dict()}


@router.get("/watchlist")
async def get_watchlist(
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """Get user watchlist"""
    watchlist = db.query(Watchlist).filter(Watchlist.user_id == user_id).all()
    
    return {
        "watchlist": [
            {
                "movie_id": item.movie_id,
                "status": item.status,
                "added_at": item.added_at.isoformat() if item.added_at else None
            }
            for item in watchlist
        ]
    }


@router.post("/watchlist/add")
async def add_to_watchlist(
    movie_id: str,
    status: str = "want_to_watch",
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """Add movie to watchlist"""
    # Check if already in watchlist
    existing = db.query(Watchlist).filter(
        Watchlist.user_id == user_id,
        Watchlist.movie_id == movie_id
    ).first()
    
    if existing:
        existing.status = status
    else:
        new_item = Watchlist(
            watchlist_id=str(uuid.uuid4()),
            user_id=user_id,
            movie_id=movie_id,
            status=status
        )
        db.add(new_item)
    
    db.commit()
    return {"message": "Added to watchlist"}


@router.delete("/watchlist/remove")
async def remove_from_watchlist(
    movie_id: str,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_db)
):
    """Remove movie from watchlist"""
    item = db.query(Watchlist).filter(
        Watchlist.user_id == user_id,
        Watchlist.movie_id == movie_id
    ).first()
    
    if item:
        db.delete(item)
        db.commit()
    
    return {"message": "Removed from watchlist"}
