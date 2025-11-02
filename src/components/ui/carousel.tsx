import * as React from "react";
import { useState } from "react";
import { searchMovies, getSimilarMovies } from "@/services/movieService";
import useEmblaCarousel, { type UseEmblaCarouselType } from "embla-carousel-react";
import { ArrowLeft, ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

type CarouselApi = UseEmblaCarouselType[1];
type UseCarouselParameters = Parameters<typeof useEmblaCarousel>;
type CarouselOptions = UseCarouselParameters[0];
type CarouselPlugin = UseCarouselParameters[1];

type CarouselProps = {
  opts?: CarouselOptions;
  plugins?: CarouselPlugin;
  orientation?: "horizontal" | "vertical";
  setApi?: (api: CarouselApi) => void;
};

type CarouselContextProps = {
  carouselRef: ReturnType<typeof useEmblaCarousel>[0];
  api: ReturnType<typeof useEmblaCarousel>[1];
  scrollPrev: () => void;
  scrollNext: () => void;
  canScrollPrev: boolean;
  canScrollNext: boolean;
} & CarouselProps;

const CarouselContext = React.createContext<CarouselContextProps | null>(null);

function useCarousel() {
  const context = React.useContext(CarouselContext);
  if (!context) {
    throw new Error("useCarousel must be used within a <Carousel />");
  }
  return context;
}

const MovieCarousel = () => {
  const [query, setQuery] = useState("");
  const [movies, setMovies] = useState<any[]>([]);
  const [recommendations, setRecommendations] = useState<any[]>([]);

  const handleSearch = async () => {
    if (!query.trim()) return;
    try {
      const results = await searchMovies(query);
      setMovies(results || []);
    } catch (error) {
      console.error("Error fetching movies:", error);
    }
  };

  const fetchRecommendations = async (movieId: number) => {
    try {
      const recs = await getSimilarMovies(movieId);
      setRecommendations(recs || []);
    } catch (error) {
      console.error("Error fetching recommendations:", error);
    }
  };

  return (
    <div className="p-4">
      <input
        type="text"
        placeholder="Search for a movie..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="p-2 border rounded"
      />
      <Button onClick={handleSearch} className="ml-2">Search</Button>

      <h2 className="mt-4 text-lg font-bold">Search Results:</h2>
      <ul className="mt-2">
        {movies.length > 0 ? movies.map((movie) => (
          <li key={movie.id} className="flex justify-between items-center p-2 border-b">
            {movie.title}
            <Button onClick={() => fetchRecommendations(movie.id)}>Get Recommendations</Button>
          </li>
        )) : <p>No movies found.</p>}
      </ul>

      <h2 className="mt-4 text-lg font-bold">Recommendations:</h2>
      <ul className="mt-2">
        {recommendations.length > 0 ? recommendations.map((rec) => (
          <li key={rec.id} className="p-2 border-b">{rec.title}</li>
        )) : <p>No recommendations available.</p>}
      </ul>
    </div>
  );
};

export default MovieCarousel;
