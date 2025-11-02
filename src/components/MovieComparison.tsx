import { Movie } from "@/services/movieService";
import { motion } from "framer-motion";
import { Star, Calendar, TrendingUp } from "lucide-react";

interface MovieComparisonProps {
  movies: Movie[];
}

const MovieComparison = ({ movies }: MovieComparisonProps) => {
  if (movies.length < 2) return null;

  return (
    <div className="grid grid-cols-2 gap-4 p-4 bg-black/20 rounded-lg">
      {movies.map((movie, index) => (
        <motion.div
          key={movie.id}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.2 }}
          className="space-y-4"
        >
          <h3 className="text-lg font-semibold text-white truncate">{movie.title}</h3>
          
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-white/80">
              <Star className="h-4 w-4 text-netflix-red" />
              <span>{movie.vote_average.toFixed(1)} Rating</span>
            </div>
            
            <div className="flex items-center gap-2 text-white/80">
              <Calendar className="h-4 w-4 text-netflix-red" />
              <span>{new Date(movie.release_date).getFullYear()}</span>
            </div>
            
            <div className="flex items-center gap-2 text-white/80">
              <TrendingUp className="h-4 w-4 text-netflix-red" />
              <span>{movie.vote_count} Votes</span>
            </div>
          </div>
          
          <p className="text-sm text-white/60 line-clamp-3">{movie.overview}</p>
        </motion.div>
      ))}
    </div>
  );
};

export default MovieComparison;