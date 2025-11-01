/**
 * MovieCard Component
 * Displays movie poster with hover effects and explanation tooltip
 */

import React, { useState } from 'react';
import Image from 'next/image';
import styles from './MovieCard.module.css';

interface MovieCardProps {
  movie: {
    movie_id: string;
    title: string;
    poster_url?: string;
    score?: number;
    reason?: string;
    genres?: string;
    vote_average?: number;
  };
  onClick?: (movieId: string) => void;
  showExplanation?: boolean;
}

export const MovieCard: React.FC<MovieCardProps> = ({
  movie,
  onClick,
  showExplanation = true,
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const [showTooltip, setShowTooltip] = useState(false);

  const handleClick = () => {
    if (onClick) {
      onClick(movie.movie_id);
    }
  };

  return (
    <div
      className={styles.movieCard}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={handleClick}
      role="button"
      tabIndex={0}
      aria-label={`${movie.title} - ${movie.genres || 'Movie'}`}
    >
      <div className={`${styles.posterContainer} ${isHovered ? styles.hovered : ''}`}>
        {movie.poster_url ? (
          <Image
            src={movie.poster_url}
            alt={movie.title}
            fill
            className={styles.poster}
            sizes="(max-width: 768px) 150px, 200px"
          />
        ) : (
          <div className={styles.posterPlaceholder}>
            <span className={styles.posterIcon}>🎬</span>
          </div>
        )}
        
        {isHovered && (
          <div className={styles.overlay}>
            <div className={styles.overlayContent}>
              {movie.vote_average && (
                <div className={styles.rating}>
                  ⭐ {movie.vote_average.toFixed(1)}
                </div>
              )}
              {showExplanation && movie.reason && (
                <button
                  className={styles.explanationButton}
                  onMouseEnter={() => setShowTooltip(true)}
                  onMouseLeave={() => setShowTooltip(false)}
                  aria-label="View recommendation explanation"
                >
                  ℹ️
                </button>
              )}
            </div>
          </div>
        )}
      </div>
      
      {showTooltip && movie.reason && (
        <div className={styles.tooltip}>
          <p className={styles.tooltipText}>{movie.reason}</p>
        </div>
      )}
      
      <div className={styles.movieInfo}>
        <h3 className={styles.title}>{movie.title}</h3>
        {movie.genres && (
          <p className={styles.genres}>{movie.genres.split(', ').slice(0, 2).join(', ')}</p>
        )}
      </div>
    </div>
  );
};

export default MovieCard;

