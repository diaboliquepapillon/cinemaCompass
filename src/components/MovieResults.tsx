import { Movie } from "@/services/movieService";
import { motion } from "framer-motion";
import { Loader2 } from "lucide-react";
import MovieGrid from "./MovieGrid";
import MovieComparison from "./MovieComparison";
import GenreBlender from "./GenreBlender";
import MoodSelector from "./MoodSelector";
import DiscoverySections from "./DiscoverySections";

interface MovieResultsProps {
  isSearching: boolean;
  isLoadingGenreMovies: boolean;
  searchResults: Movie[] | undefined;
  genreBlendedMovies: Movie[] | undefined;
  recommendedMovies: Movie[] | undefined;
  comparisonMovies: Movie[];
  selectedGenres: { id: number; name: string; }[];
  selectedMood: string | null;
  onGenresSelected: (genres: { id: number; name: string; }[]) => void;
  onMoodSelect: (mood: string | null) => void;
  onMovieWatched: (movie: Movie) => void;
  onMovieClick: (movie: Movie) => void;
}

const MovieResults = ({
  isSearching,
  isLoadingGenreMovies,
  searchResults,
  genreBlendedMovies,
  recommendedMovies,
  comparisonMovies,
  selectedGenres,
  selectedMood,
  onGenresSelected,
  onMoodSelect,
  onMovieWatched,
  onMovieClick,
}: MovieResultsProps) => {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="min-h-[500px] rounded-lg bg-gradient-to-br from-black/40 via-black/30 to-black/40 p-4 sm:p-6 backdrop-blur-sm order-last md:order-first border border-white/5 shadow-xl"
    >
      <GenreBlender
        selectedGenres={selectedGenres}
        onGenresSelected={onGenresSelected}
      />

      {comparisonMovies.length > 0 && (
        <div className="mt-6">
          <MovieComparison movies={comparisonMovies} />
        </div>
      )}

      <div className="mt-6">
        <MoodSelector onMoodSelect={onMoodSelect} selectedMood={selectedMood} />
      </div>

      {isSearching && !searchResults && (
        <motion.div 
          className="flex items-center justify-center py-12"
          animate={{ 
            scale: [1, 1.2, 1],
            rotate: [0, 360, 0]
          }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          <Loader2 className="h-8 w-8 text-netflix-red" />
        </motion.div>
      )}

      {searchResults && searchResults.length > 0 && (
        <MovieGrid 
          movies={searchResults} 
          onMovieWatched={onMovieWatched}
          onMovieClick={onMovieClick}
        />
      )}

      {!searchResults && selectedGenres.length === 2 && (
        <>
          {isLoadingGenreMovies ? (
            <motion.div 
              className="flex items-center justify-center py-12"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <Loader2 className="h-8 w-8 text-netflix-red animate-spin" />
            </motion.div>
          ) : genreBlendedMovies && genreBlendedMovies.length > 0 ? (
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-8"
            >
              <div className="mb-4">
                <h3 className="text-lg font-semibold text-white">
                  {genreBlendedMovies.length} {genreBlendedMovies.length === 1 ? 'movie' : 'movies'} found
                </h3>
              </div>
              <MovieGrid 
                movies={genreBlendedMovies} 
                onMovieWatched={onMovieWatched}
                onMovieClick={onMovieClick}
              />
            </motion.div>
          ) : genreBlendedMovies && genreBlendedMovies.length === 0 ? (
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-8 text-center py-12"
            >
              <p className="text-white/60 text-lg mb-2">No movies found</p>
              <p className="text-white/40 text-sm">
                Try selecting different genres or clear your selection to browse all movies.
              </p>
            </motion.div>
          ) : null}
        </>
      )}

      {recommendedMovies && recommendedMovies.length > 0 && !searchResults && (
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-8"
        >
          <MovieGrid 
            movies={recommendedMovies} 
            onMovieWatched={onMovieWatched}
            onMovieClick={onMovieClick}
          />
        </motion.div>
      )}

      {/* Show discovery sections when no search, genre blend, or recommendations */}
      {!searchResults && 
       !genreBlendedMovies && 
       !recommendedMovies && 
       !isSearching && 
       !isLoadingGenreMovies && (
        <div className="mt-8">
          <DiscoverySections
            onMovieWatched={onMovieWatched}
            onMovieClick={onMovieClick}
          />
        </div>
      )}
    </motion.div>
  );
};

export default MovieResults;