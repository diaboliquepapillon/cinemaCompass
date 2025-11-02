import { useState, useEffect } from "react";
import { Movie, getMovieDetails } from "@/services/movieService";
import MovieCard from "./MovieCard";
import MovieDetails from "./MovieDetails";
import { useQuery } from "@tanstack/react-query";

interface MovieGridProps {
  movies: Movie[];
  onMovieWatched?: (movie: Movie) => void;
  onMovieClick?: (movie: Movie) => void;
}

const MovieGrid = ({ movies, onMovieWatched, onMovieClick }: MovieGridProps) => {
  const [selectedMovie, setSelectedMovie] = useState<Movie | null>(null);
  const [movieDetails, setMovieDetails] = useState<any>(null);

  const { data: fetchedDetails, isLoading: isLoadingDetails } = useQuery({
    queryKey: ["movieDetails", selectedMovie?.id],
    queryFn: () => selectedMovie ? getMovieDetails(selectedMovie.id) : null,
    enabled: !!selectedMovie,
  });

  useEffect(() => {
    if (fetchedDetails) {
      setMovieDetails(fetchedDetails);
    }
  }, [fetchedDetails]);

  const handleMovieClick = async (movie: Movie) => {
    // Always open movie details dialog
    setSelectedMovie(movie);
    setMovieDetails(null); // Reset details when selecting new movie
    
    // Also notify parent for comparison feature if provided
    if (onMovieClick) {
      onMovieClick(movie);
    }
  };

  const handleClose = () => {
    setSelectedMovie(null);
    setMovieDetails(null);
  };

  return (
    <>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
        {movies.map((movie) => (
          <MovieCard
            key={movie.id}
            movie={movie}
            onDragEnd={onMovieWatched}
            onClick={() => handleMovieClick(movie)}
          />
        ))}
      </div>
      <MovieDetails
        movie={selectedMovie}
        movieDetails={movieDetails}
        isLoading={isLoadingDetails}
        onClose={handleClose}
      />
    </>
  );
};

export default MovieGrid;