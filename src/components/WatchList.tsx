import { Movie, getImageUrl } from "@/services/movieService";
import { motion, AnimatePresence } from "framer-motion";
import { Film, Star, Clock } from "lucide-react";

interface WatchListProps {
  watchedMovies: Movie[];
  onDeleteMovie: (movieId: number) => void;
}

const WatchList = ({ watchedMovies, onDeleteMovie }: WatchListProps) => {
  return (
    <motion.div 
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      className="rounded-lg bg-gradient-to-br from-black/40 via-black/30 to-black/40 p-4 sm:p-6 backdrop-blur-sm order-first md:order-last border border-white/5 shadow-xl"
    >
      <motion.div 
        className="flex items-center justify-between border-b border-white/10 pb-4"
        whileHover={{ scale: 1.02 }}
      >
        <h2 className="text-lg font-semibold text-transparent bg-clip-text bg-gradient-to-r from-netflix-red to-purple-500">
          MY LIST
        </h2>
      </motion.div>

      <motion.div 
        className="mt-4 flex items-center justify-between text-sm text-white/80"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        <motion.div 
          className="flex items-center gap-2"
          whileHover={{ scale: 1.05 }}
        >
          <Film className="h-4 w-4 text-netflix-red" />
          <span>{watchedMovies.length} titles</span>
        </motion.div>
        <motion.div 
          className="flex items-center gap-2"
          whileHover={{ scale: 1.05 }}
        >
          <Star className="h-4 w-4 text-netflix-red" />
          <span>
            {watchedMovies.length > 0 
              ? (watchedMovies.reduce((acc, movie) => acc + movie.vote_average, 0) / watchedMovies.length).toFixed(1) 
              : 0}
          </span>
        </motion.div>
        <motion.div 
          className="flex items-center gap-2"
          whileHover={{ scale: 1.05 }}
        >
          <Clock className="h-4 w-4 text-netflix-red" />
          <span>{watchedMovies.length * 120} min</span>
        </motion.div>
      </motion.div>

      <AnimatePresence mode="popLayout">
        {watchedMovies.length === 0 ? (
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="mt-8 rounded-lg bg-gradient-to-br from-white/5 to-white/10 p-6 text-center"
          >
            <motion.p 
              className="text-white/60"
              animate={{ 
                scale: [1, 1.02, 1],
              }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              Your list is empty
            </motion.p>
            <motion.p 
              className="mt-2 text-netflix-red"
              animate={{ y: [0, -2, 0] }}
              transition={{ duration: 1.5, repeat: Infinity }}
            >
              Drag movies here to add them... 🎬
            </motion.p>
          </motion.div>
        ) : (
          <motion.div 
            className="mt-4 space-y-2"
            layout
          >
            {watchedMovies.map((movie, index) => (
              <motion.div
                key={movie.id}
                layout
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ delay: index * 0.1 }}
                className="group flex items-center gap-2 rounded-lg bg-gradient-to-r from-white/5 to-white/10 p-2 text-white transition-all duration-300 hover:from-white/10 hover:to-white/15"
              >
                <motion.img 
                  src={getImageUrl(movie.poster_path)} 
                  alt={movie.title} 
                  className="h-16 w-12 rounded object-cover"
                  whileHover={{ scale: 1.1 }}
                  layoutId={`movie-image-${movie.id}`}
                />
                <div className="flex-1 min-w-0">
                  <p className="font-medium truncate">{movie.title}</p>
                  <p className="text-sm text-white/60">
                    {new Date(movie.release_date).getFullYear()} • ⭐ {movie.vote_average.toFixed(1)}
                  </p>
                </div>
                <motion.button 
                  onClick={() => onDeleteMovie(movie.id)}
                  className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-netflix-red/20 rounded"
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  aria-label="Remove from list"
                >
                  <svg className="w-4 h-4 text-netflix-red" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </motion.button>
              </motion.div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default WatchList;