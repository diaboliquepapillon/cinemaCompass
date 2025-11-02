/**
 * Recommendation service for hybrid content + collaborative filtering
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface Recommendation {
  movie_id: string;
  title: string;
  score: number;
  reason: string;
  genres?: string;
  poster_path?: string;
  vote_average?: number;
}

export interface EvaluationMetrics {
  precision_at_k: number;
  recall_at_k: number;
  ndcg_at_k: number;
  k: number;
}

/**
 * Get hybrid recommendations combining content-based and collaborative filtering
 */
export const getHybridRecommendations = async (
  likedMovieIds: string[],
  userId?: string,
  topN: number = 10
): Promise<Recommendation[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/recommendations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        liked_movie_ids: likedMovieIds,
        top_n: topN,
      }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching recommendations:', error);
    // Fallback: return empty array
    return [];
  }
};

/**
 * Evaluate recommendation quality
 */
export const evaluateRecommendations = async (
  likedMovies: string[],
  relevantMovies: string[],
  userId?: string,
  k: number = 10
): Promise<EvaluationMetrics> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/evaluate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        liked_movies: likedMovies,
        relevant_movies: relevantMovies,
        k: k,
      }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error evaluating recommendations:', error);
    throw error;
  }
};

