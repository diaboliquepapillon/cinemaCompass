import { Movie } from "@/services/movieService";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Play, ExternalLink, Clock, Users, Film } from "lucide-react";
import { motion } from "framer-motion";

interface MovieDetailsProps {
  movie: Movie | null;
  movieDetails: any | null; // Full TMDb details
  onClose: () => void;
}

const streamingServices = {
  netflix: { name: "Netflix", url: "https://www.netflix.com/search?q=" },
  prime: { name: "Prime Video", url: "https://www.amazon.com/s?k=" },
  disney: { name: "Disney+", url: "https://www.disneyplus.com/search?q=" },
  hulu: { name: "Hulu", url: "https://www.hulu.com/search?q=" },
  hbo: { name: "HBO Max", url: "https://www.hbomax.com/search?q=" },
  apple: { name: "Apple TV+", url: "https://tv.apple.com/search?q=" },
};

const MovieDetails = ({ movie, movieDetails, onClose }: MovieDetailsProps) => {
  if (!movie) return null;

  const handleStreamingService = (service: keyof typeof streamingServices) => {
    const serviceUrl = streamingServices[service].url;
    window.open(`${serviceUrl}${encodeURIComponent(movie.title)}`, '_blank');
  };

  const trailerUrl = movieDetails?.videos?.results?.find(
    (v: any) => v.type === 'Trailer' && v.site === 'YouTube'
  )?.key;

  return (
    <Dialog open={!!movie} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto bg-netflix-black text-white border-white/10">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold text-netflix-red">
            {movie.title}
          </DialogTitle>
        </DialogHeader>
        
        <div className="mt-4 space-y-6">
          {/* Trailer Section */}
          {trailerUrl && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="relative aspect-video rounded-lg overflow-hidden bg-black"
            >
              <iframe
                src={`https://www.youtube.com/embed/${trailerUrl}?autoplay=0`}
                className="w-full h-full"
                allowFullScreen
                title={`${movie.title} Trailer`}
              />
            </motion.div>
          )}

          {/* Meta Info */}
          <div className="flex flex-wrap items-center gap-4 text-sm text-gray-400">
            <span className="flex items-center gap-1">
              <span>⭐</span>
              <span className="text-white font-semibold">{movie.vote_average.toFixed(1)}</span>
              <span>({movie.vote_count.toLocaleString()} votes)</span>
            </span>
            <span>•</span>
            <span>{new Date(movie.release_date).getFullYear()}</span>
            {movieDetails?.runtime && (
              <>
                <span>•</span>
                <span className="flex items-center gap-1">
                  <Clock className="h-4 w-4" />
                  {movieDetails.runtime} min
                </span>
              </>
            )}
            {movieDetails?.genres && movieDetails.genres.length > 0 && (
              <>
                <span>•</span>
                <span>{movieDetails.genres.map((g: any) => g.name).join(', ')}</span>
              </>
            )}
          </div>

          {/* Overview */}
          {movie.overview && (
            <div>
              <h3 className="font-semibold mb-2 text-netflix-red">Overview</h3>
              <p className="text-gray-300 leading-relaxed">{movie.overview}</p>
            </div>
          )}

          {/* Director & Cast */}
          {movieDetails?.credits && (
            <div className="grid md:grid-cols-2 gap-6">
              {movieDetails.credits.crew?.find((c: any) => c.job === 'Director') && (
                <div>
                  <h4 className="font-semibold mb-2 text-netflix-red flex items-center gap-2">
                    <Film className="h-4 w-4" />
                    Director
                  </h4>
                  <p className="text-gray-300">
                    {movieDetails.credits.crew.find((c: any) => c.job === 'Director').name}
                  </p>
                </div>
              )}
              {movieDetails.credits.cast && movieDetails.credits.cast.length > 0 && (
                <div>
                  <h4 className="font-semibold mb-2 text-netflix-red flex items-center gap-2">
                    <Users className="h-4 w-4" />
                    Cast
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {movieDetails.credits.cast.slice(0, 8).map((actor: any) => (
                      <span 
                        key={actor.id} 
                        className="text-gray-300 text-sm bg-white/5 px-2 py-1 rounded"
                      >
                        {actor.name}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Streaming Services */}
          <div>
            <h4 className="font-semibold mb-3 text-netflix-red">Watch On</h4>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
              {Object.entries(streamingServices).map(([key, service]) => (
                <Button
                  key={key}
                  variant="outline"
                  onClick={() => handleStreamingService(key as keyof typeof streamingServices)}
                  className="bg-black/40 border-white/20 text-white hover:bg-netflix-red hover:border-netflix-red"
                >
                  <ExternalLink className="mr-2 h-4 w-4" />
                  {service.name}
                </Button>
              ))}
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default MovieDetails;
