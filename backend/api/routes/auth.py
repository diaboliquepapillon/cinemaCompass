"""
Authentication routes
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
import hashlib
import secrets
from datetime import datetime, timedelta
import jwt
import os
import uuid

from ..database import get_db
from ..models import User

router = APIRouter()

# JWT secret key (in production, use environment variable)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "cinemacompass-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str


def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    return hash_password(plain_password) == hashed_password


def create_access_token(user_id: str) -> str:
    """Create JWT access token"""
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    payload = {
        "sub": user_id,
        "exp": expire
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserRegister, db=Depends(get_db)):
    """Register a new user"""
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = hash_password(user_data.password)
    new_user = User(
        user_id=str(uuid.uuid4()),
        email=user_data.email,
        password_hash=hashed_password,
        name=user_data.name or user_data.email.split("@")[0]
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create access token
    access_token = create_access_token(str(new_user.user_id))
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=str(new_user.user_id)
    )


@router.post("/login", response_model=TokenResponse)
async def login(login_data: UserLogin, db=Depends(get_db)):
    """Login user"""
    user = db.query(User).filter(User.email == login_data.email).first()
    
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create access token
    access_token = create_access_token(str(user.user_id))
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=str(user.user_id)
    )
