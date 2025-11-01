/**
 * Profile Page - User settings, preferences, and analytics
 */

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import RecommendationSlider from '../components/RecommendationSlider';
import styles from './Profile.module.css';

interface UserPreferences {
  favorite_genres: string[];
  explicit_content: boolean;
  recommendation_style: string;
}

interface WatchlistItem {
  movie_id: string;
  title: string;
  poster_url?: string;
  status: string;
  added_at: string;
}

export default function Profile() {
  const router = useRouter();
  const [preferences, setPreferences] = useState<UserPreferences>({
    favorite_genres: [],
    explicit_content: true,
    recommendation_style: 'balanced',
  });
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([]);
  const [contentWeight, setContentWeight] = useState(0.5);
  const [collaborativeWeight, setCollaborativeWeight] = useState(0.5);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProfile();
    fetchWatchlist();
  }, []);

  const fetchProfile = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const userId = localStorage.getItem('user_id');
      if (!userId) {
        router.push('/login');
        return;
      }

      const res = await fetch(`${apiUrl}/api/user/profile`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });
      const data = await res.json();
      
      if (data.preferences) {
        setPreferences(data.preferences);
      }
    } catch (error) {
      console.error('Error fetching profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchWatchlist = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const res = await fetch(`${apiUrl}/api/user/watchlist`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });
      const data = await res.json();
      setWatchlist(data.watchlist || []);
    } catch (error) {
      console.error('Error fetching watchlist:', error);
    }
  };

  const handlePreferenceUpdate = async (newPreferences: Partial<UserPreferences>) => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      await fetch(`${apiUrl}/api/user/preferences`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          ...preferences,
          ...newPreferences,
        }),
      });
      
      setPreferences(prev => ({ ...prev, ...newPreferences }));
    } catch (error) {
      console.error('Error updating preferences:', error);
    }
  };

  const handleSliderChange = (content: number, collaborative: number) => {
    setContentWeight(content);
    setCollaborativeWeight(collaborative);
    
    const style =
      content > 0.6 ? 'content' : content < 0.4 ? 'collaborative' : 'balanced';
    handlePreferenceUpdate({ recommendation_style: style });
  };

  if (loading) {
    return (
      <div className={styles.loading}>
        <div className={styles.spinner}></div>
        <p>Loading profile...</p>
      </div>
    );
  }

  return (
    <div className={styles.profile}>
      <div className={styles.header}>
        <h1 className={styles.title}>Profile & Settings</h1>
        <p className={styles.subtitle}>Customize your CinemaCompass experience</p>
      </div>

      {/* Recommendation Preferences */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Recommendation Preferences</h2>
        <RecommendationSlider
          contentWeight={contentWeight}
          collaborativeWeight={collaborativeWeight}
          onChange={handleSliderChange}
        />
      </section>

      {/* Genre Preferences */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Favorite Genres</h2>
        <div className={styles.genreList}>
          {['Action', 'Comedy', 'Drama', 'Sci-Fi', 'Horror', 'Romance', 'Thriller'].map(genre => (
            <label key={genre} className={styles.genreCheckbox}>
              <input
                type="checkbox"
                checked={preferences.favorite_genres.includes(genre)}
                onChange={(e) => {
                  const newGenres = e.target.checked
                    ? [...preferences.favorite_genres, genre]
                    : preferences.favorite_genres.filter(g => g !== genre);
                  handlePreferenceUpdate({ favorite_genres: newGenres });
                }}
              />
              <span>{genre}</span>
            </label>
          ))}
        </div>
      </section>

      {/* Content Preferences */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Content Preferences</h2>
        <label className={styles.switch}>
          <input
            type="checkbox"
            checked={preferences.explicit_content}
            onChange={(e) =>
              handlePreferenceUpdate({ explicit_content: e.target.checked })
            }
          />
          <span className={styles.sliderRound}></span>
          <span className={styles.switchLabel}>Show explicit content</span>
        </label>
      </section>

      {/* Watchlist */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>My Watchlist</h2>
        {watchlist.length === 0 ? (
          <p className={styles.empty}>Your watchlist is empty.</p>
        ) : (
          <div className={styles.watchlistGrid}>
            {watchlist.map(item => (
              <div key={item.movie_id} className={styles.watchlistItem}>
                {item.poster_url ? (
                  <img
                    src={item.poster_url}
                    alt={item.title}
                    className={styles.watchlistPoster}
                  />
                ) : (
                  <div className={styles.watchlistPlaceholder}>🎬</div>
                )}
                <div className={styles.watchlistInfo}>
                  <h3>{item.title}</h3>
                  <p className={styles.status}>{item.status}</p>
                </div>
                <button
                  className={styles.removeButton}
                  onClick={async () => {
                    try {
                      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
                      await fetch(`${apiUrl}/api/user/watchlist/remove?movie_id=${item.movie_id}`, {
                        method: 'DELETE',
                        headers: {
                          Authorization: `Bearer ${localStorage.getItem('token')}`,
                        },
                      });
                      fetchWatchlist();
                    } catch (error) {
                      console.error('Error removing from watchlist:', error);
                    }
                  }}
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Account Actions */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Account</h2>
        <button
          className={styles.logoutButton}
          onClick={() => {
            localStorage.removeItem('token');
            localStorage.removeItem('user_id');
            router.push('/login');
          }}
        >
          Log Out
        </button>
      </section>
    </div>
  );
}

