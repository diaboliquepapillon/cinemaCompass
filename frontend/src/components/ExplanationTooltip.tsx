/**
 * ExplanationTooltip Component
 * Shows detailed explanation for recommendations with feature attribution
 */

import React from 'react';
import styles from './ExplanationTooltip.module.css';

interface ExplanationTooltipProps {
  explanation: string;
  featureContributions?: {
    genres?: number;
    director?: number;
    cast?: number;
    collaborative?: number;
  };
  show?: boolean;
  position?: 'top' | 'bottom' | 'left' | 'right';
}

export const ExplanationTooltip: React.FC<ExplanationTooltipProps> = ({
  explanation,
  featureContributions,
  show = false,
  position = 'top',
}) => {
  if (!show) return null;

  return (
    <div className={`${styles.tooltip} ${styles[position]}`} role="tooltip">
      <div className={styles.content}>
        <p className={styles.explanation}>{explanation}</p>
        
        {featureContributions && (
          <div className={styles.attribution}>
            <h4 className={styles.attributionTitle}>Why this recommendation:</h4>
            <div className={styles.features}>
              {featureContributions.genres !== undefined && (
                <div className={styles.feature}>
                  <span className={styles.featureLabel}>Genre Match:</span>
                  <div className={styles.featureBar}>
                    <div
                      className={styles.featureFill}
                      style={{ width: `${featureContributions.genres * 100}%` }}
                    />
                  </div>
                  <span className={styles.featureValue}>
                    {Math.round(featureContributions.genres * 100)}%
                  </span>
                </div>
              )}
              
              {featureContributions.director !== undefined && (
                <div className={styles.feature}>
                  <span className={styles.featureLabel}>Director:</span>
                  <div className={styles.featureBar}>
                    <div
                      className={styles.featureFill}
                      style={{ width: `${featureContributions.director * 100}%` }}
                    />
                  </div>
                  <span className={styles.featureValue}>
                    {Math.round(featureContributions.director * 100)}%
                  </span>
                </div>
              )}
              
              {featureContributions.cast !== undefined && (
                <div className={styles.feature}>
                  <span className={styles.featureLabel}>Cast:</span>
                  <div className={styles.featureBar}>
                    <div
                      className={styles.featureFill}
                      style={{ width: `${featureContributions.cast * 100}%` }}
                    />
                  </div>
                  <span className={styles.featureValue}>
                    {Math.round(featureContributions.cast * 100)}%
                  </span>
                </div>
              )}
              
              {featureContributions.collaborative !== undefined && (
                <div className={styles.feature}>
                  <span className={styles.featureLabel}>Similar Users:</span>
                  <div className={styles.featureBar}>
                    <div
                      className={styles.featureFill}
                      style={{ width: `${featureContributions.collaborative * 100}%` }}
                    />
                  </div>
                  <span className={styles.featureValue}>
                    {Math.round(featureContributions.collaborative * 100)}%
                  </span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
      
      <div className={styles.arrow} />
    </div>
  );
};

export default ExplanationTooltip;

