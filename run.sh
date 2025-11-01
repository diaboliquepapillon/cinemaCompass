#!/bin/bash

# CinemaCompass - Hybrid Movie Recommendation System
# Run script for Streamlit app

echo "🎬 Starting CinemaCompass..."
echo "Installing dependencies..."

pip install -r requirements.txt

echo "Starting Streamlit app..."
streamlit run app.py

