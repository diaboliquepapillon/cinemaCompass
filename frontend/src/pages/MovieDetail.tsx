/**
 * Movie Detail Page - Full movie information with recommendations
 */

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Image from 'next/image';
import MovieCard from '../components/MovieCard';
import ExplanationTooltip from '../components/ExplanationTooltip';
import styles from './MovieDetail.module.css';

interface Movie {
  movie_id: string;
  title: string;
  genres?: string;
  director?: string;
  cast?: string;
  overview?: string;
  poster_url?: string;
  backdrop_url?: string;
  year?: number;
  runtime?: number;
  vote_average?: number;
  vote_count?: number;
}

export default function MovieDetail() {
  const router = useRouter();
  const { id } = router.query;
  const [movie, setMovie] = useState<Movie | null>(null);
  const [similarMovies, setSimilarMovies] = useState<Movie[]>([]);
  const [loading, setLoading] = useState(true);
  const [userRating, setUserRating] = useState<number | null>(null);
  const [inWatchlist, setInWatchlist] = useState(false);
  const [showExplanation, setShowExplanation] = useState(false);

  useEffect(() => {
    if (id) {
      fetchMovieDetail();
      fetchSimilarMovies();
      checkWatchlist();
    }
  }, [id]);

  const fetchMovieDetail = async () => {
    if (!id) return;

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const res = await fetch(`${apiUrl}/api/movies/${id}`);
      const data = await res.json();
      setMovie(data);
    } catch (error) {
      console.error('Error fetching movie:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchSimilarMovies = async () => {
    if (!id) return;

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      // Use recommendations endpoint or similar movies endpoint
      const userId = localStorage.getItem('user_id');
      if (userId) {
        const res = await fetch(`${apiUrl}/api/recommendations/${userId}?top_k=10`);
        const data = await res.json();
        setSimilarMovies(data.slice(0, 6)); // Show top 6 similar
      }
    } catch (error) {
      console.error('Error fetching similar movies:', error);
    }
  };

  const checkWatchlist = async () => {
    if (!id) return;

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const userId = localStorage.getItem('user_id');
      if (!userId) return;

      const res = await fetch(`${apiUrl}/api/user/watchlist`);
      const data = await res.json();
      const inList = data.watchlist?.some(
        (item: any) => item.movie_id === id
      );
      setInWatchlist(inList || false);
    } catch (error) {
      console.error('Error checking watchlist:', error);
    }
  };

  const handleRate = async (rating: number) => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const userId = localStorage.getItem('user_id');
      if (!userId) {
        router.push('/login');
        return;
      }

      await fetch(`${apiUrl}/api/movies/${id}/rate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ rating, user_id: userId }),
      });

      setUserRating(rating);
    } catch (error) {
      console.error('Error rating movie:', error);
    }
  };

  const handleWatchlistToggle = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const userId = localStorage.getItem('user_id');
      if (!userId) {
        router.push('/login');
        return;
      }

      if (inWatchlist) {
        await fetch(`${apiUrl}/api/user/watchlist/remove?movie_id=${id}`, {
          method: 'DELETE',
        });
      } else {
        await fetch(`${apiUrl}/api/user/watchlist/add?movie_id=${id}&status=want_to_watch`, {
          method: 'POST',
        });
      }

      setInWatchlist(!inWatchlist);
    } catch (error) {
      console.error('Error updating watchlist:', error);
    }
  };

  if (loading) {
    return (
      <div className={styles.loading}>
        <div className={styles.spinner}></div>
        <p>Loading movie details...</p>
      </div>
    );
  }

  if (!movie) {
    return (
      <div className={styles.error}>
        <h2>Movie not found</h2>
        <button onClick={() => router.push('/')}>Go Home</button>
      </div>
    );
  }

  return (
    <div className={styles.movieDetail}>
      {/* Hero Section with Backdrop */}
      <div
        className={styles.hero}
        style={{
          backgroundImage: movie.backdrop_url
            ? `url(${movie.backdrop_url})`
            : 'linear-gradient(135deg, #6B4EE6 0%, #E50914 100%)',
        }}
      >
        <div className={styles.heroOverlay}></div>
        <div className={styles.heroContent}>
          <div className={styles.posterContainer}>
            {movie.poster_url ? (
              <Image
                src={movie.poster_url}
                alt={movie.title}
                width={300}
                height={450}
                className={styles.poster}
              />
            ) : (
              <div className={styles.posterPlaceholder}>
                <span>🎬</span>
              </div>
            )}
          </div>

          <div className={styles.movieInfo}>
            <h1 className={styles.title}>{movie.title}</h1>
            
            <div className={styles.meta}>
              {movie.year && <span>{movie.year}</span>}
              {movie.runtime && <span>{movie.runtime} min</span>}
              {movie.genres && (
                <span className={styles.genres}>{movie.genres}</span>
              )}
            </div>

            {movie.vote_average && (
              <div className={styles.rating}>
                <span className={styles.star}>⭐</span>
                <span className={styles.ratingValue}>
                  {movie.vote_average.toFixed(1)}
                </span>
                {movie.vote_count && (
                  <span className={styles.voteCount}>
                    ({movie.vote_count} votes)
                  </span>
                )}
              </div>
            )}

            {movie.overview && (
              <p className={styles.overview}>{movie.overview}</p>
            )}

            {movie.director && (
              <div className={styles.credits}>
                <p><strong>Director:</strong> {movie.director}</p>
                {movie.cast && (
                  <p><strong>Cast:</strong> {movie.cast}</p>
                )}
              </div>
            )}

            <div className={styles.actions}>
              <button className={styles.playButton}>▶ Play</button>
              <button
                className={`${styles.watchlistButton} ${inWatchlist ? styles.added : ''}`}
                onClick={handleWatchlistToggle}
              >
                {inWatchlist ? '✓ In Watchlist' : '+ Add to Watchlist'}
              </button>
              <button
                className={styles.explanationButton}
                onMouseEnter={() => setShowExplanation(true)}
                onMouseLeave={() => setShowExplanation(false)}
              >
                ℹ️ Why Recommended?
              </button>
            </div>

            {/* User Rating */}
            <div className={styles.userRating}>
              <p>Rate this movie:</p>
              <div className={styles.ratingButtons}>
                {[1, 2, 3, 4, 5].map(rating => (
                  <button
                    key={rating}
                    className={`${styles.ratingButton} ${userRating === rating ? styles.active : ''}`}
                    onClick={() => handleRate(rating)}
                  >
                    ⭐
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Similar Movies */}
      {similarMovies.length > 0 && (
        <section className={styles.similarSection}>
          <h2 className={styles.sectionTitle}>More Like This</h2>
          <div className={styles.similarMovies}>
            {similarMovies.map(similar => (
              <MovieCard
                key={similar.movie_id}
                movie={similar}
                onClick={(id) => router.push(`/movie/${id}`)}
              />
            ))}
          </div>
        </section>
      )}

      {showExplanation && (
        <ExplanationTooltip
          explanation="This movie is recommended based on your viewing history and similar user preferences."
          show={showExplanation}
          position="top"
        />
      )}
    </div>
  );
}

