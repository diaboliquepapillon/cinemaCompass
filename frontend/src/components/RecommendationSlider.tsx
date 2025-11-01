/**
 * RecommendationSlider Component
 * Adaptive slider to adjust content vs collaborative filtering weights
 */

import React from 'react';
import styles from './RecommendationSlider.module.css';

interface RecommendationSliderProps {
  contentWeight: number;
  collaborativeWeight: number;
  onChange: (contentWeight: number, collaborativeWeight: number) => void;
  disabled?: boolean;
}

export const RecommendationSlider: React.FC<RecommendationSliderProps> = ({
  contentWeight,
  collaborativeWeight,
  onChange,
  disabled = false,
}) => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newContentWeight = parseFloat(e.target.value);
    const newCollaborativeWeight = 1 - newContentWeight;
    onChange(newContentWeight, newCollaborativeWeight);
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h3 className={styles.title}>Recommendation Style</h3>
        <div className={styles.weights}>
          <span className={styles.weightLabel}>
            Content: <strong>{Math.round(contentWeight * 100)}%</strong>
          </span>
          <span className={styles.weightLabel}>
            Collaborative: <strong>{Math.round(collaborativeWeight * 100)}%</strong>
          </span>
        </div>
      </div>
      
      <div className={styles.sliderContainer}>
        <div className={styles.sliderLabels}>
          <span className={styles.label}>Content-Based</span>
          <span className={styles.label}>Balanced</span>
          <span className={styles.label}>Collaborative</span>
        </div>
        
        <input
          type="range"
          min="0"
          max="1"
          step="0.05"
          value={contentWeight}
          onChange={handleChange}
          disabled={disabled}
          className={styles.slider}
          aria-label="Adjust recommendation style"
          aria-valuemin={0}
          aria-valuemax={1}
          aria-valuenow={contentWeight}
        />
        
        <div className={styles.sliderTrack}>
          <div
            className={styles.sliderFill}
            style={{
              width: `${contentWeight * 100}%`,
              background: `linear-gradient(90deg, #6B4EE6 0%, #E50914 ${contentWeight * 100}%)`,
            }}
          />
        </div>
      </div>
      
      <div className={styles.description}>
        {contentWeight > 0.6 ? (
          <p>🎨 Focusing on movie characteristics and metadata</p>
        ) : contentWeight < 0.4 ? (
          <p>👥 Focusing on user preferences and community wisdom</p>
        ) : (
          <p>⚖️ Balanced approach combining both methods</p>
        )}
      </div>
    </div>
  );
};

export default RecommendationSlider;

