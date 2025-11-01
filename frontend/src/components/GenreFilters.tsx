/**
 * GenreFilters Component
 * Horizontal scrollable genre filter pills with multi-select
 */

import React from 'react';
import styles from './GenreFilters.module.css';

interface GenreFiltersProps {
  genres: string[];
  selectedGenres: string[];
  onToggleGenre: (genre: string) => void;
  genreCounts?: Record<string, number>;
}

export const GenreFilters: React.FC<GenreFiltersProps> = ({
  genres,
  selectedGenres,
  onToggleGenre,
  genreCounts = {},
}) => {
  return (
    <div className={styles.container} role="group" aria-label="Genre filters">
      <div className={styles.scrollContainer}>
        {genres.map((genre) => {
          const isSelected = selectedGenres.includes(genre);
          const count = genreCounts[genre] || 0;
          
          return (
            <button
              key={genre}
              className={`${styles.genrePill} ${isSelected ? styles.selected : ''}`}
              onClick={() => onToggleGenre(genre)}
              aria-pressed={isSelected}
              aria-label={`${genre} ${count > 0 ? `(${count} movies)` : ''}`}
            >
              <span className={styles.genreName}>{genre}</span>
              {count > 0 && (
                <span className={styles.count}>({count})</span>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default GenreFilters;

