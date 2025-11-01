/**
 * Discover Page - Advanced filtering and search
 */

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import MovieCard from '../components/MovieCard';
import GenreFilters from '../components/GenreFilters';
import styles from './Discover.module.css';

interface Movie {
  movie_id: string;
  title: string;
  poster_url?: string;
  genres?: string;
  year?: number;
  vote_average?: number;
}

export default function Discover() {
  const router = useRouter();
  const [movies, setMovies] = useState<Movie[]>([]);
  const [filteredMovies, setFilteredMovies] = useState<Movie[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedGenres, setSelectedGenres] = useState<string[]>([]);
  const [yearFilter, setYearFilter] = useState<string>('');
  const [sortBy, setSortBy] = useState<string>('popularity');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  useEffect(() => {
    fetchMovies();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [movies, searchQuery, selectedGenres, yearFilter, sortBy]);

  const fetchMovies = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const res = await fetch(`${apiUrl}/api/movies/search/list?limit=100`);
      const data = await res.json();
      setMovies(data.results || []);
      setFilteredMovies(data.results || []);
    } catch (error) {
      console.error('Error fetching movies:', error);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...movies];

    // Search filter
    if (searchQuery) {
      filtered = filtered.filter(movie =>
        movie.title.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Genre filter
    if (selectedGenres.length > 0) {
      filtered = filtered.filter(movie =>
        selectedGenres.some(genre =>
          movie.genres?.toLowerCase().includes(genre.toLowerCase())
        )
      );
    }

    // Year filter
    if (yearFilter) {
      const year = parseInt(yearFilter);
      filtered = filtered.filter(movie => movie.year === year);
    }

    // Sort
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'popularity':
          return (b.vote_average || 0) - (a.vote_average || 0);
        case 'rating':
          return (b.vote_average || 0) - (a.vote_average || 0);
        case 'year':
          return (b.year || 0) - (a.year || 0);
        case 'title':
          return a.title.localeCompare(b.title);
        default:
          return 0;
      }
    });

    setFilteredMovies(filtered);
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

  // Extract unique genres
  const allGenres = Array.from(
    new Set(
      movies.flatMap(m => m.genres?.split(', ') || []).filter(Boolean)
    )
  );

  // Get unique years
  const years = Array.from(
    new Set(movies.map(m => m.year).filter(Boolean))
  ).sort((a, b) => (b || 0) - (a || 0));

  if (loading) {
    return (
      <div className={styles.loading}>
        <div className={styles.spinner}></div>
        <p>Discovering movies...</p>
      </div>
    );
  }

  return (
    <div className={styles.discover}>
      <div className={styles.header}>
        <h1 className={styles.title}>Discover Movies</h1>
        <p className={styles.subtitle}>
          Explore our collection of {movies.length} movies
        </p>
      </div>

      {/* Search and Filters */}
      <div className={styles.filtersContainer}>
        <div className={styles.searchBar}>
          <input
            type="text"
            placeholder="Search movies..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className={styles.searchInput}
          />
        </div>

        <div className={styles.filterControls}>
          <div className={styles.filterGroup}>
            <label htmlFor="year">Year:</label>
            <select
              id="year"
              value={yearFilter}
              onChange={(e) => setYearFilter(e.target.value)}
              className={styles.select}
            >
              <option value="">All Years</option>
              {years.slice(0, 20).map(year => (
                <option key={year} value={year}>{year}</option>
              ))}
            </select>
          </div>

          <div className={styles.filterGroup}>
            <label htmlFor="sort">Sort By:</label>
            <select
              id="sort"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className={styles.select}
            >
              <option value="popularity">Popularity</option>
              <option value="rating">Rating</option>
              <option value="year">Year</option>
              <option value="title">Title</option>
            </select>
          </div>

          <div className={styles.viewToggle}>
            <button
              className={`${styles.viewButton} ${viewMode === 'grid' ? styles.active : ''}`}
              onClick={() => setViewMode('grid')}
              aria-label="Grid view"
            >
              ⊞
            </button>
            <button
              className={`${styles.viewButton} ${viewMode === 'list' ? styles.active : ''}`}
              onClick={() => setViewMode('list')}
              aria-label="List view"
            >
              ☰
            </button>
          </div>
        </div>
      </div>

      {/* Genre Filters */}
      <GenreFilters
        genres={allGenres}
        selectedGenres={selectedGenres}
        onToggleGenre={handleGenreToggle}
      />

      {/* Results */}
      <div className={styles.results}>
        <div className={styles.resultsHeader}>
          <p className={styles.resultsCount}>
            {filteredMovies.length} {filteredMovies.length === 1 ? 'movie' : 'movies'} found
          </p>
        </div>

        <div className={`${styles.movieGrid} ${viewMode === 'list' ? styles.listView : ''}`}>
          {filteredMovies.map(movie => (
            <MovieCard
              key={movie.movie_id}
              movie={movie}
              onClick={handleMovieClick}
            />
          ))}
        </div>

        {filteredMovies.length === 0 && (
          <div className={styles.noResults}>
            <p>No movies found matching your criteria.</p>
            <button
              className={styles.clearFilters}
              onClick={() => {
                setSearchQuery('');
                setSelectedGenres([]);
                setYearFilter('');
              }}
            >
              Clear Filters
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

