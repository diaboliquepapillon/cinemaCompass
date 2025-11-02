import { Movie } from "@/services/movieService";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Play } from "lucide-react";

interface MovieDetailsProps {
  movie: Movie | null;
  onClose: () => void;
}

const MovieDetails = ({ movie, onClose }: MovieDetailsProps) => {
  if (!movie) return null;

  const handleWatchOnNetflix = () => {
    window.open(`https://www.netflix.com/search?q=${encodeURIComponent(movie.title)}`, '_blank');
  };

  return (
    <Dialog open={!!movie} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl bg-netflix-black text-white">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold text-netflix-red">
            {movie.title}
          </DialogTitle>
        </DialogHeader>
        <div className="mt-4 space-y-4">
          <div className="flex items-center gap-2 text-sm text-gray-400">
            <span>{new Date(movie.release_date).getFullYear()}</span>
            <span>•</span>
            <span className="flex items-center gap-1">
              <span>⭐</span>
              <span>{movie.vote_average.toFixed(1)}</span>
            </span>
          </div>
          <p className="text-gray-300">{movie.overview}</p>
          <div className="flex gap-3 pt-4">
            <Button
              onClick={handleWatchOnNetflix}
              className="bg-white text-black hover:bg-white/90"
            >
              <Play className="mr-2 h-4 w-4" />
              Watch on Netflix
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default MovieDetails;