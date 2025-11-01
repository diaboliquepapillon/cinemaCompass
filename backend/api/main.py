"""
FastAPI main application
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from typing import Optional

from .routes import recommendations, movies, users, auth
from .database import get_db
from .models import init_db

app = FastAPI(
    title="CinemaCompass API",
    description="Hybrid movie recommendation system API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api/user", tags=["users"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["recommendations"])
app.include_router(movies.router, prefix="/api/movies", tags=["movies"])

# Security
security = HTTPBearer()

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    print("CinemaCompass API started")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "CinemaCompass API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/api/health")
async def health_check():
    """Health check"""
    return {"status": "healthy"}

