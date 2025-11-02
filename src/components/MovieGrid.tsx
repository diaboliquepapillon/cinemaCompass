import { useState } from "react";
import { Movie } from "@/services/movieService";
import MovieCard from "./MovieCard";
import MovieDetails from "./MovieDetails";

interface MovieGridProps {
  movies: Movie[];
  onMovieWatched?: (movie: Movie) => void;
  onMovieClick?: (movie: Movie) => void;
}

const MovieGrid = ({ movies, onMovieWatched, onMovieClick }: MovieGridProps) => {
  const [selectedMovie, setSelectedMovie] = useState<Movie | null>(null);

  const handleMovieClick = (movie: Movie) => {
    if (onMovieClick) {
      onMovieClick(movie);
    } else {
      setSelectedMovie(movie);
    }
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
        onClose={() => setSelectedMovie(null)}
      />
    </>
  );
};

export default MovieGrid;