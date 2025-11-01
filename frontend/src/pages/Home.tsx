/**
 * Home Page - Netflix-style hero section with recommendation rows
 */

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import MovieCard from '../components/MovieCard';
import GenreFilters from '../components/GenreFilters';
import RecommendationSlider from '../components/RecommendationSlider';
import styles from './Home.module.css';

interface Movie {
  movie_id: string;
  title: string;
  poster_url?: string;
  score?: number;
  reason?: string;
  genres?: string;
  vote_average?: number;
}

export default function Home() {
  const router = useRouter();
  const [trendingMovies, setTrendingMovies] = useState<Movie[]>([]);
  const [recommendations, setRecommendations] = useState<Movie[]>([]);
  const [topRated, setTopRated] = useState<Movie[]>([]);
  const [heroMovie, setHeroMovie] = useState<Movie | null>(null);
  const [selectedGenres, setSelectedGenres] = useState<string[]>([]);
  const [contentWeight, setContentWeight] = useState(0.5);
  const [collaborativeWeight, setCollaborativeWeight] = useState(0.5);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    if (selectedGenres.length > 0 || contentWeight !== 0.5) {
      fetchRecommendations();
    }
  }, [selectedGenres, contentWeight, collaborativeWeight]);

  const fetchData = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      
      // Fetch trending movies
      const trendingRes = await fetch(`${apiUrl}/api/movies/trending/list?limit=20`);
      const trendingData = await trendingRes.json();
      setTrendingMovies(trendingData.results || []);
      
      // Set hero movie
      if (trendingData.results && trendingData.results.length > 0) {
        setHeroMovie(trendingData.results[0]);
      }
      
      // Fetch top rated
      const topRatedRes = await fetch(`${apiUrl}/api/movies/search/list?limit=20`);
      const topRatedData = await topRatedRes.json();
      setTopRated(topRatedData.results || []);
      
      // Fetch initial recommendations (requires user_id)
      const userId = localStorage.getItem('user_id');
      if (userId) {
        await fetchRecommendations(userId);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchRecommendations = async (userId?: string) => {
    const user = userId || localStorage.getItem('user_id');
    if (!user) return;

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const res = await fetch(`${apiUrl}/api/recommendations/${user}?top_k=10`);
      const data = await res.json();
      setRecommendations(data || []);
    } catch (error) {
      console.error('Error fetching recommendations:', error);
    }
  };

  const handleGenreToggle = (genre: string) => {
    setSelectedGenres(prev =>
      prev.includes(genre)
        ? prev.filter(g => g !== genre)
        : [...prev, genre]
    );
  };

  const handleMovieClick = (movieId: string) => {
    router.push(`/movie/${movieId}`);
  };

  const handleSliderChange = (content: number, collaborative: number) => {
    setContentWeight(content);
    setCollaborativeWeight(collaborative);
    // TODO: Call API to update user preferences
  };

  // Extract unique genres from movies
  const allGenres = Array.from(
    new Set(
      [...trendingMovies, ...recommendations, ...topRated]
        .flatMap(m => m.genres?.split(', ') || [])
        .filter(Boolean)
    )
  );

  if (loading) {
    return (
      <div className={styles.loading}>
        <div className={styles.spinner}></div>
        <p>Loading CinemaCompass...</p>
      </div>
    );
  }

  return (
    <div className={styles.home}>
      {/* Hero Section */}
      {heroMovie && (
        <section className={styles.hero}>
          <div
            className={styles.heroBackground}
            style={{
              backgroundImage: heroMovie.backdrop_url
                ? `url(${heroMovie.backdrop_url})`
                : 'linear-gradient(135deg, #6B4EE6 0%, #E50914 100%)',
            }}
          >
            <div className={styles.heroOverlay}></div>
            <div className={styles.heroContent}>
              <h1 className={styles.heroTitle}>{heroMovie.title}</h1>
              <p className={styles.heroDescription}>
                Discover personalized movie recommendations powered by AI
              </p>
              <div className={styles.heroActions}>
                <button
                  className={styles.watchButton}
                  onClick={() => handleMovieClick(heroMovie.movie_id)}
                >
                  ▶ Play
                </button>
                <button
                  className={styles.infoButton}
                  onClick={() => handleMovieClick(heroMovie.movie_id)}
                >
                  ℹ️ More Info
                </button>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Recommendation Settings */}
      <section className={styles.settingsSection}>
        <RecommendationSlider
          contentWeight={contentWeight}
          collaborativeWeight={collaborativeWeight}
          onChange={handleSliderChange}
        />
      </section>

      {/* Genre Filters */}
      <section className={styles.filtersSection}>
        <GenreFilters
          genres={allGenres}
          selectedGenres={selectedGenres}
          onToggleGenre={handleGenreToggle}
        />
      </section>

      {/* Recommendations Row */}
      {recommendations.length > 0 && (
        <section className={styles.movieRow}>
          <h2 className={styles.sectionTitle}>Recommended For You</h2>
          <div className={styles.movieRowContent}>
            {recommendations.map(movie => (
              <MovieCard
                key={movie.movie_id}
                movie={movie}
                onClick={handleMovieClick}
                showExplanation={true}
              />
            ))}
          </div>
        </section>
      )}

      {/* Trending Row */}
      {trendingMovies.length > 0 && (
        <section className={styles.movieRow}>
          <h2 className={styles.sectionTitle}>Trending Now</h2>
          <div className={styles.movieRowContent}>
            {trendingMovies.map(movie => (
              <MovieCard
                key={movie.movie_id}
                movie={movie}
                onClick={handleMovieClick}
              />
            ))}
          </div>
        </section>
      )}

      {/* Top Rated Row */}
      {topRated.length > 0 && (
        <section className={styles.movieRow}>
          <h2 className={styles.sectionTitle}>Top Rated</h2>
          <div className={styles.movieRowContent}>
            {topRated.map(movie => (
              <MovieCard
                key={movie.movie_id}
                movie={movie}
                onClick={handleMovieClick}
              />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

