"""
Data loading and preprocessing utilities
"""

import pandas as pd
import os
from typing import Optional, Tuple


def load_sample_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load sample movie and ratings data
    
    Returns:
        Tuple of (movies_df, ratings_df)
    """
    # Sample movies data with metadata
    movies_data = {
        'movie_id': ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8', 'm9', 'm10',
                    'm11', 'm12', 'm13', 'm14', 'm15', 'm16', 'm17', 'm18', 'm19', 'm20'],
        'title': ['Inception', 'Interstellar', 'The Matrix', 'Blade Runner 2049', 'The Dark Knight',
                 'Pulp Fiction', 'Forrest Gump', 'The Shawshank Redemption', 'The Godfather', 'Fight Club',
                 'Parasite', 'The Departed', 'Goodfellas', 'Taxi Driver', 'Seven',
                 'Zodiac', 'Gone Girl', 'Se7en', 'Memento', 'The Prestige'],
        'genres': ['Sci-Fi, Thriller', 'Sci-Fi, Drama', 'Sci-Fi, Action', 'Sci-Fi, Thriller', 'Action, Crime',
                  'Crime, Drama', 'Drama, Romance', 'Drama', 'Crime, Drama', 'Drama, Thriller',
                  'Thriller, Drama', 'Crime, Thriller', 'Crime, Drama', 'Crime, Drama', 'Crime, Thriller',
                  'Crime, Thriller', 'Mystery, Thriller', 'Crime, Thriller', 'Mystery, Thriller', 'Drama, Mystery'],
        'director': ['Christopher Nolan', 'Christopher Nolan', 'The Wachowskis', 'Denis Villeneuve', 'Christopher Nolan',
                    'Quentin Tarantino', 'Robert Zemeckis', 'Frank Darabont', 'Francis Ford Coppola', 'David Fincher',
                    'Bong Joon-ho', 'Martin Scorsese', 'Martin Scorsese', 'Martin Scorsese', 'David Fincher',
                    'David Fincher', 'David Fincher', 'David Fincher', 'Christopher Nolan', 'Christopher Nolan'],
        'cast': ['Leonardo DiCaprio, Marion Cotillard', 'Matthew McConaughey, Anne Hathaway', 'Keanu Reeves, Laurence Fishburne',
                'Ryan Gosling, Harrison Ford', 'Christian Bale, Heath Ledger',
                'John Travolta, Samuel L. Jackson', 'Tom Hanks, Robin Wright', 'Tim Robbins, Morgan Freeman', 'Marlon Brando, Al Pacino',
                'Brad Pitt, Edward Norton', 'Song Kang-ho, Lee Sun-kyun', 'Leonardo DiCaprio, Matt Damon', 'Robert De Niro, Ray Liotta',
                'Robert De Niro, Jodie Foster', 'Brad Pitt, Morgan Freeman', 'Jake Gyllenhaal, Robert Downey Jr.', 'Ben Affleck, Rosamund Pike',
                'Brad Pitt, Morgan Freeman', 'Guy Pearce, Carrie-Anne Moss', 'Hugh Jackman, Christian Bale'],
        'tags': ['mind-bending, dreams', 'space, time, emotion', 'reality, simulation', 'dystopia, AI', 'batman, chaos',
                'non-linear, crime', 'life, running', 'hope, prison', 'mafia, power', 'identity, chaos',
                'class, social', 'undercover, betrayal', 'gangster, rise', 'loneliness, violence', 'seven sins, mystery',
                'serial killer, investigation', 'marriage, secrets', 'serial killer, detective', 'memory, revenge', 'magic, rivalry'],
        'poster_url': [
            'https://image.tmdb.org/t/p/w500/oYuLEt3zVCKq57qu2F8dT7NIa6f.jpg',  # Inception
            'https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg',  # Interstellar
            'https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg',  # The Matrix
            'https://image.tmdb.org/t/p/w500/gajva2L0rPYkEWj5FlNH6Uz0XRH.jpg',  # Blade Runner 2049
            'https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef8WH.jpg',  # The Dark Knight
            'https://image.tmdb.org/t/p/w500/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg',  # Pulp Fiction
            'https://image.tmdb.org/t/p/w500/arw2vcBveWOVZr6pxd9XTd1Td2a.jpg',  # Forrest Gump
            'https://image.tmdb.org/t/p/w500/9cqN21k4Xm9BMdCOD3jQ5VagZXs.jpg',  # The Shawshank Redemption
            'https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg',  # The Godfather
            'https://image.tmdb.org/t/p/w500/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg',  # Fight Club
            'https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg',  # Parasite
            'https://image.tmdb.org/t/p/w500/nT97ifVT2J1irMQvwsLoHy9KnNz.jpg',  # The Departed
            'https://image.tmdb.org/t/p/w500/aKuFiU8s7X9Sy5NN4kwvx6x4NnT.jpg',  # Goodfellas
            'https://image.tmdb.org/t/p/w500/ekstpH614fwDX8DUln1a2Opz0N8.jpg',  # Taxi Driver
            'https://image.tmdb.org/t/p/w500/69Sns8WoET6CfaYlIkHbla4l7Tn.jpg',  # Seven
            'https://image.tmdb.org/t/p/w500/p0uXS6yOxQU4Z1BDP5mZ5Vk0GVV.jpg',  # Zodiac
            'https://image.tmdb.org/t/p/w500/rCvQ7X0zJxZtP7rGvUqNWqLtEkl.jpg',  # Gone Girl
            'https://image.tmdb.org/t/p/w500/69Sns8WoET6CfaYlIkHbla4l7Tn.jpg',  # Se7en (same as Seven)
            'https://image.tmdb.org/t/p/w500/yuNs09hvpHVU1cBTCAkYzIzSqio.jpg',  # Memento
            'https://image.tmdb.org/t/p/w500/5MXyQfz8xUP3dJPTY0Ao5pX8SxL.jpg'   # The Prestige
        ]
    }
    
    movies_df = pd.DataFrame(movies_data)
    
    # Sample ratings data
    ratings_data = {
        'user_id': ['u1', 'u1', 'u1', 'u2', 'u2', 'u2', 'u3', 'u3', 'u3', 'u4', 'u4', 'u4',
                    'u5', 'u5', 'u5', 'u6', 'u6', 'u6', 'u7', 'u7', 'u7', 'u8', 'u8', 'u8',
                    'u9', 'u9', 'u9', 'u10', 'u10', 'u10'],
        'movie_id': ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm1', 'm5', 'm7', 'm8', 'm9', 'm10',
                    'm11', 'm12', 'm13', 'm14', 'm15', 'm16', 'm17', 'm18', 'm19', 'm2', 'm3', 'm20',
                    'm1', 'm2', 'm20', 'm4', 'm3', 'm5'],
        'rating': [5.0, 5.0, 4.5, 4.5, 5.0, 4.0, 5.0, 4.5, 4.0, 5.0, 5.0, 4.5,
                  4.5, 4.5, 5.0, 4.0, 4.5, 4.0, 4.5, 4.5, 4.0, 5.0, 4.5, 4.5,
                  5.0, 5.0, 4.5, 4.5, 4.0, 5.0]
    }
    
    ratings_df = pd.DataFrame(ratings_data)
    
    return movies_df, ratings_df


def load_from_csv(movies_path: Optional[str] = None, 
                  ratings_path: Optional[str] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load data from CSV files
    
    Args:
        movies_path: Path to movies CSV file
        ratings_path: Path to ratings CSV file
    
    Returns:
        Tuple of (movies_df, ratings_df)
    """
    if movies_path and os.path.exists(movies_path):
        movies_df = pd.read_csv(movies_path)
    else:
        movies_df, _ = load_sample_data()
    
    if ratings_path and os.path.exists(ratings_path):
        ratings_df = pd.read_csv(ratings_path)
    else:
        _, ratings_df = load_sample_data()
    
    return movies_df, ratings_df


def load_cleaned_datasets(
    movies_path: str = "data/processed/movies_cleaned.csv",
    ratings_path: str = "data/processed/ratings_cleaned.csv"
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load cleaned and processed datasets
    
    Args:
        movies_path: Path to cleaned movies CSV
        ratings_path: Path to cleaned ratings CSV
    
    Returns:
        Tuple of (movies_df, ratings_df)
    
    Raises:
        FileNotFoundError: If cleaned datasets don't exist
    """
    if not os.path.exists(movies_path):
        raise FileNotFoundError(
            f"Cleaned movies file not found: {movies_path}\n"
            "Run data/scripts/run_pipeline.py to generate cleaned datasets"
        )
    
    if not os.path.exists(ratings_path):
        raise FileNotFoundError(
            f"Cleaned ratings file not found: {ratings_path}\n"
            "Run data/scripts/run_pipeline.py to generate cleaned datasets"
        )
    
    movies_df = pd.read_csv(movies_path)
    ratings_df = pd.read_csv(ratings_path)
    
    # Ensure proper types
    movies_df['movie_id'] = movies_df['movie_id'].astype(str)
    ratings_df['movie_id'] = ratings_df['movie_id'].astype(str)
    ratings_df['user_id'] = ratings_df['user_id'].astype(str)
    
    return movies_df, ratings_df

