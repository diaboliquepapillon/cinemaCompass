const BASE_URL = "https://api.themoviedb.org/3";
const API_KEY = "c17e4ee4cc6e8f947e7062828e0e762b"; // This is the actual API key extracted from your JWT token

export interface Movie {
  id: number;
  title: string;
  poster_path: string;
  vote_average: number;
  release_date: string;
  overview: string;
  genre_ids?: number[];
  vote_count: number;
  explanation?: string; // Personalized explanation from hybrid recommendations
  // Enhanced fields
  runtime?: number;
  genres?: { id: number; name: string; }[];
  director?: string;
  cast?: { name: string; character: string; profile_path: string; }[];
  trailer_key?: string;
  backdrop_path?: string;
  budget?: number;
  revenue?: number;
  production_companies?: { name: string; logo_path: string; }[];
}

export const searchMovies = async (query: string) => {
  if (!query) return [];

  try {
    const response = await fetch(`${BASE_URL}/search/movie?api_key=${API_KEY}&query=${query}`, {
      headers: {
        'Accept': 'application/json'
      }
    });
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.status_message || 'Failed to fetch movies');
    }
    
    return data.results;
  } catch (error) {
    console.error("Error fetching movies:", error);
    return [];
  }
};

export const getSimilarMovies = async (movieId: number) => {
  try {
    const response = await fetch(`${BASE_URL}/movie/${movieId}/recommendations?api_key=${API_KEY}`, {
      headers: {
        'Accept': 'application/json'
      }
    });
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.status_message || 'Failed to fetch recommendations');
    }
    
    return data.results;
  } catch (error) {
    console.error("Error fetching recommendations:", error);
    return [];
  }
};

export const getImageUrl = (path: string) =>
  path ? `https://image.tmdb.org/t/p/w500${path}` : (import.meta.env.MODE === 'production' ? '/cinemaCompass/placeholder.svg' : '/placeholder.svg');

export const getMoviesByGenres = async (genreIds: number[]) => {
  try {
    const response = await fetch(
      `${BASE_URL}/discover/movie?api_key=${API_KEY}&with_genres=${genreIds.join(',')}&sort_by=popularity.desc`,
      {
        headers: {
          'Accept': 'application/json'
        }
      }
    );
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.status_message || 'Failed to fetch movies by genres');
    }
    
    return data.results;
  } catch (error) {
    console.error("Error fetching movies by genres:", error);
    return [];
  }
};

export const getMoviesByPerson = async (query: string) => {
  try {
    // First search for the person
    const personResponse = await fetch(
      `${BASE_URL}/search/person?api_key=${API_KEY}&query=${query}`,
      {
        headers: {
          'Accept': 'application/json'
        }
      }
    );
    const personData = await personResponse.json();
    
    if (!personResponse.ok || !personData.results.length) {
      return [];
    }

    // Then get their movies
    const personId = personData.results[0].id;
    const moviesResponse = await fetch(
      `${BASE_URL}/person/${personId}/movie_credits?api_key=${API_KEY}`,
      {
        headers: {
          'Accept': 'application/json'
        }
      }
    );
    const moviesData = await moviesResponse.json();
    
    if (!moviesResponse.ok) {
      throw new Error(moviesData.status_message || 'Failed to fetch person movies');
    }
    
    return moviesData.cast || [];
  } catch (error) {
    console.error("Error fetching person movies:", error);
    return [];
  }
};

// Get detailed movie info with videos, credits, etc.
export const getMovieDetails = async (movieId: number) => {
  try {
    const response = await fetch(
      `${BASE_URL}/movie/${movieId}?api_key=${API_KEY}&append_to_response=videos,credits,release_dates`,
      {
        headers: {
          'Accept': 'application/json'
        }
      }
    );
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.status_message || 'Failed to fetch movie details');
    }
    
    return data;
  } catch (error) {
    console.error("Error fetching movie details:", error);
    return null;
  }
};

// Get trending movies
export const getTrendingMovies = async (timeWindow: 'day' | 'week' = 'day') => {
  try {
    const response = await fetch(
      `${BASE_URL}/trending/movie/${timeWindow}?api_key=${API_KEY}`,
      {
        headers: {
          'Accept': 'application/json'
        }
      }
    );
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.status_message || 'Failed to fetch trending movies');
    }
    
    return data.results;
  } catch (error) {
    console.error("Error fetching trending movies:", error);
    return [];
  }
};

// Get popular movies
export const getPopularMovies = async () => {
  try {
    const response = await fetch(
      `${BASE_URL}/movie/popular?api_key=${API_KEY}`,
      {
        headers: {
          'Accept': 'application/json'
        }
      }
    );
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.status_message || 'Failed to fetch popular movies');
    }
    
    return data.results;
  } catch (error) {
    console.error("Error fetching popular movies:", error);
    return [];
  }
};

// Get upcoming movies
export const getUpcomingMovies = async () => {
  try {
    const response = await fetch(
      `${BASE_URL}/movie/upcoming?api_key=${API_KEY}`,
      {
        headers: {
          'Accept': 'application/json'
        }
      }
    );
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.status_message || 'Failed to fetch upcoming movies');
    }
    
    return data.results;
  } catch (error) {
    console.error("Error fetching upcoming movies:", error);
    return [];
  }
};

// Get movie genres list
export const getGenres = async () => {
  try {
    const response = await fetch(
      `${BASE_URL}/genre/movie/list?api_key=${API_KEY}`,
      {
        headers: {
          'Accept': 'application/json'
        }
      }
    );
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.status_message || 'Failed to fetch genres');
    }
    
    return data.genres;
  } catch (error) {
    console.error("Error fetching genres:", error);
    return [];
  }
};