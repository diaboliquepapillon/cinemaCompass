import { useQuery } from "@tanstack/react-query";
import { getTrendingMovies, getPopularMovies, getUpcomingMovies } from "@/services/movieService";
import { Movie } from "@/services/movieService";
import MovieGrid from "./MovieGrid";
import { motion } from "framer-motion";
import { TrendingUp, Star, Calendar } from "lucide-react";

interface DiscoverySectionsProps {
  onMovieWatched: (movie: Movie) => void;
  onMovieClick: (movie: Movie) => void;
}

const DiscoverySections = ({ onMovieWatched, onMovieClick }: DiscoverySectionsProps) => {
  const { data: trendingMovies, isLoading: isLoadingTrending } = useQuery({
    queryKey: ["trending"],
    queryFn: () => getTrendingMovies('day'),
    staleTime: 1000 * 60 * 60, // 1 hour
  });

  const { data: popularMovies, isLoading: isLoadingPopular } = useQuery({
    queryKey: ["popular"],
    queryFn: () => getPopularMovies(),
    staleTime: 1000 * 60 * 60 * 24, // 24 hours
  });

  const { data: upcomingMovies, isLoading: isLoadingUpcoming } = useQuery({
    queryKey: ["upcoming"],
    queryFn: () => getUpcomingMovies(),
    staleTime: 1000 * 60 * 60, // 1 hour
  });

  const hasAnyData = trendingMovies?.length || popularMovies?.length || upcomingMovies?.length;
  const isLoading = isLoadingTrending || isLoadingPopular || isLoadingUpcoming;

  if (isLoading && !hasAnyData) {
    return null; // Don't show anything while loading initially
  }

  return (
    <div className="space-y-8">
      {trendingMovies && trendingMovies.length > 0 && (
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          <div className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-netflix-red" />
            <h2 className="text-xl font-bold text-white">Trending Today</h2>
          </div>
          <MovieGrid
            movies={trendingMovies.slice(0, 10)}
            onMovieWatched={onMovieWatched}
            onMovieClick={onMovieClick}
          />
        </motion.section>
      )}

      {popularMovies && popularMovies.length > 0 && (
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="space-y-4"
        >
          <div className="flex items-center gap-2">
            <Star className="h-5 w-5 text-netflix-red" />
            <h2 className="text-xl font-bold text-white">Popular Movies</h2>
          </div>
          <MovieGrid
            movies={popularMovies.slice(0, 10)}
            onMovieWatched={onMovieWatched}
            onMovieClick={onMovieClick}
          />
        </motion.section>
      )}

      {upcomingMovies && upcomingMovies.length > 0 && (
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="space-y-4"
        >
          <div className="flex items-center gap-2">
            <Calendar className="h-5 w-5 text-netflix-red" />
            <h2 className="text-xl font-bold text-white">Coming Soon</h2>
          </div>
          <MovieGrid
            movies={upcomingMovies.slice(0, 10)}
            onMovieWatched={onMovieWatched}
            onMovieClick={onMovieClick}
          />
        </motion.section>
      )}
    </div>
  );
};

export default DiscoverySections;

