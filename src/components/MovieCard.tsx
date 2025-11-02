import { Movie, getImageUrl } from "@/services/movieService";
import { Card } from "@/components/ui/card";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { motion, useMotionValue, useTransform } from "framer-motion";
import { useIsMobile } from "@/hooks/use-mobile";
import { useToast } from "@/hooks/use-toast";

interface MovieCardProps {
  movie: Movie;
  onDragEnd?: (movie: Movie) => void;
  onClick?: (movie: Movie) => void;
}

const MovieCard = ({ movie, onDragEnd, onClick }: MovieCardProps) => {
  const x = useMotionValue(0);
  const rotate = useTransform(x, [-200, 200], [-10, 10]);
  const opacity = useTransform(x, [-200, 0, 200], [0.5, 1, 0.5]);
  const isMobile = useIsMobile();
  const { toast } = useToast();

  const handleDragStart = () => {
    if (isMobile) {
      toast({
        title: "Swipe right to add to list",
        description: "Release to confirm",
        duration: 2000,
      });
    }
  };

  const handleDragEnd = (event: any, info: any) => {
    const threshold = window.innerWidth > 768 ? window.innerWidth / 2 : window.innerWidth * 0.75;
    if (info.point.x > threshold && onDragEnd) {
      onDragEnd(movie);
    }
  };

  const handleClick = (e: React.MouseEvent) => {
    // Only trigger click if not dragging
    if (Math.abs(x.get()) < 5 && onClick) {
      onClick(movie);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={{ x, rotate, opacity }}
      drag="x"
      dragConstraints={{ left: 0, right: 0 }}
      dragElastic={0.7}
      dragTransition={{ bounceStiffness: 300, bounceDamping: 20 }}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onDragEnd={handleDragEnd}
      onDragStart={handleDragStart}
      onClick={handleClick}
      className="cursor-grab touch-pan-x active:cursor-grabbing"
    >
      <Card
        className="group relative overflow-hidden rounded-lg transition-all duration-300 hover:ring-2 hover:ring-white/20"
      >
        <div className="aspect-[2/3] w-full">
          <motion.img
            src={getImageUrl(movie.poster_path)}
            alt={movie.title}
            className="h-full w-full object-cover"
            onError={(e) => {
              e.currentTarget.src = "/placeholder.svg";
            }}
            layoutId={`movie-image-${movie.id}`}
          />
        </div>
        <motion.div 
          className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/50 to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100"
          initial={{ opacity: 0 }}
          whileHover={{ opacity: 1 }}
        >
          <div className="absolute bottom-0 p-3 sm:p-4 text-white">
            <motion.h3 
              className="text-sm sm:text-base font-bold line-clamp-2"
              initial={{ y: 20, opacity: 0 }}
              whileHover={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.2 }}
            >
              {movie.title}
            </motion.h3>
            <motion.div 
              className="mt-1 sm:mt-2 flex items-center gap-2 text-xs sm:text-sm"
              initial={{ y: 20, opacity: 0 }}
              whileHover={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.2, delay: 0.1 }}
            >
              <span>{new Date(movie.release_date).getFullYear()}</span>
              <span>•</span>
              <span className="flex items-center gap-1">
                ⭐ {movie.vote_average.toFixed(1)}
              </span>
            </motion.div>
            {movie.explanation && (
              <motion.div
                className="mt-2 text-xs text-white/80 line-clamp-2"
                initial={{ y: 20, opacity: 0 }}
                whileHover={{ y: 0, opacity: 1 }}
                transition={{ duration: 0.2, delay: 0.15 }}
              >
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <span className="cursor-help underline decoration-dotted">
                        💡 Why recommended?
                      </span>
                    </TooltipTrigger>
                    <TooltipContent className="max-w-xs">
                      <p>{movie.explanation}</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              </motion.div>
            )}
          </div>
        </motion.div>

        {/* Drag indicator */}
        <motion.div
          className="absolute inset-0 flex items-center justify-center bg-black/60 text-white opacity-0 px-4"
          style={{ opacity: useTransform(x, [-100, 0, 100], [0.8, 0, 0.8]) }}
        >
          <div className="text-center">
            <p className="text-sm sm:text-lg font-semibold">
              {isMobile ? "Swipe right" : "Drag"} to add to My List
            </p>
            <p className="text-xs sm:text-sm text-white/70">Release to confirm</p>
          </div>
        </motion.div>
      </Card>
    </motion.div>
  );
};

export default MovieCard;