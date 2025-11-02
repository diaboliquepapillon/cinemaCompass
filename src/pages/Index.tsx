import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Movie, searchMovies, getSimilarMovies, getMoviesByGenres } from "@/services/movieService";
import { getHybridRecommendations, Recommendation } from "@/services/recommendationService";
import { useToast } from "@/hooks/use-toast";
import { useIsMobile } from "@/hooks/use-mobile";
import { motion } from "framer-motion";
import { WelcomeDialog } from "@/components/WelcomeDialog";
import SearchHeader from "@/components/SearchHeader";
import MovieResults from "@/components/MovieResults";
import WatchList from "@/components/WatchList";

const moodToGenres = {
  happy: [35, 16, 10751],
  sad: [18, 10749],
  adventurous: [28, 12, 878],
  romantic: [10749, 35],
  excited: [28, 53],
  nostalgic: [10751, 36],
};

const Index = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedMood, setSelectedMood] = useState<string | null>(null);
  const [watchedMovies, setWatchedMovies] = useState<Movie[]>([]);
  const [selectedGenres, setSelectedGenres] = useState<{ id: number; name: string; }[]>([]);
  const [comparisonMovies, setComparisonMovies] = useState<Movie[]>([]);
  const { toast } = useToast();
  const isMobile = useIsMobile();

  const {
    data: searchResults,
    isLoading: isSearching,
    error: searchError,
  } = useQuery({
    queryKey: ["search", searchTerm],
    queryFn: () => searchMovies(searchTerm),
    enabled: searchTerm.length > 0,
  });

  const {
    data: recommendedMovies,
    isLoading: isLoadingRecommendations,
  } = useQuery({
    queryKey: ["recommendations", watchedMovies, selectedMood],
    queryFn: async () => {
      if (watchedMovies.length === 0) return [];
      
      try {
        // Use hybrid recommendation system
        const likedMovieIds = watchedMovies.map(m => m.id.toString());
        const hybridRecs = await getHybridRecommendations(likedMovieIds, undefined, 20);
        
        // Convert to Movie format if needed
        if (hybridRecs.length > 0) {
          // If hybrid recommendations have the right format, use them
          // Otherwise fall back to TMDb similar movies
          const lastWatchedMovie = watchedMovies[watchedMovies.length - 1];
          let recommendations = await getSimilarMovies(lastWatchedMovie.id);
          
          // Filter by mood if selected
          if (selectedMood && recommendations) {
            const moodGenres = moodToGenres[selectedMood as keyof typeof moodToGenres];
            recommendations = recommendations.filter(movie => 
              movie.genre_ids?.some(genreId => moodGenres.includes(genreId))
            );

            if (recommendations.length < 5) {
              const moodBasedMovies = await getMoviesByGenres(moodGenres);
              recommendations = [...recommendations, ...moodBasedMovies].slice(0, 20);
            }
          }
          
          // Enhance recommendations with hybrid explanations
          recommendations = recommendations.map(movie => ({
            ...movie,
            // Add explanation if available from hybrid recs
            explanation: hybridRecs.find(r => r.movie_id === movie.id.toString())?.reason
          }));
          
          return recommendations;
        }
      } catch (error) {
        console.error("Error fetching hybrid recommendations:", error);
        // Fallback to TMDb similar movies
      }
      
      // Fallback: Use TMDb similar movies
      const lastWatchedMovie = watchedMovies[watchedMovies.length - 1];
      let recommendations = await getSimilarMovies(lastWatchedMovie.id);
      
      if (selectedMood && recommendations) {
        const moodGenres = moodToGenres[selectedMood as keyof typeof moodToGenres];
        recommendations = recommendations.filter(movie => 
          movie.genre_ids?.some(genreId => moodGenres.includes(genreId))
        );

        if (recommendations.length < 5) {
          const moodBasedMovies = await getMoviesByGenres(moodGenres);
          recommendations = [...recommendations, ...moodBasedMovies].slice(0, 20);
        }

        toast({
          title: "Recommendations Updated",
          description: `Showing movies matching your ${selectedMood} mood`,
          duration: 3000,
        });
      }
      
      return recommendations;
    },
    enabled: watchedMovies.length > 0,
  });

  const {
    data: genreBlendedMovies,
    isLoading: isLoadingGenreMovies,
  } = useQuery({
    queryKey: ["genreMovies", selectedGenres],
    queryFn: () => getMoviesByGenres(selectedGenres.map(g => g.id)),
    enabled: selectedGenres.length === 2,
  });

  const handleDeleteMovie = (movieId: number) => {
    setWatchedMovies(prev => prev.filter(movie => movie.id !== movieId));
    toast({
      title: "Movie Removed",
      description: "The movie has been removed from your list.",
    });
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchTerm.trim()) {
      toast({
        title: "Please enter a movie title",
        variant: "destructive",
      });
      return;
    }
  };

  const handleMovieWatched = (movie: Movie) => {
    if (!watchedMovies.find(m => m.id === movie.id)) {
      setWatchedMovies([...watchedMovies, movie]);
      setSearchTerm(""); // Clear search bar after adding movie
      toast({
        title: "Added to My List",
        description: `${movie.title} has been added to your list.`,
      });
      
      if (isMobile) {
        toast({
          title: "Tip",
          description: "Keep swiping right to add more movies to your list!",
          duration: 3000,
        });
      }
    }
  };

  const handleMoodSelect = (mood: string | null) => {
    setSelectedMood(mood);
    if (mood) {
      toast({
        title: "Mood Selected",
        description: `Updating recommendations to match your ${mood} mood`,
      });
    } else {
      toast({
        title: "Mood Cleared",
        description: "Showing general recommendations",
      });
    }
  };

  const handleMovieClick = (movie: Movie) => {
    if (comparisonMovies.find(m => m.id === movie.id)) {
      setComparisonMovies(comparisonMovies.filter(m => m.id !== movie.id));
    } else if (comparisonMovies.length < 2) {
      setComparisonMovies([...comparisonMovies, movie]);
    }
  };

  if (searchError) {
    console.error("API Error:", searchError);
  }

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="min-h-screen bg-gradient-to-br from-cine-darker via-netflix-black to-cine-dark"
    >
      <WelcomeDialog />
      
      <SearchHeader
        searchTerm={searchTerm}
        onSearchChange={setSearchTerm}
        onSubmit={handleSearch}
      />

      <main className="mx-auto grid max-w-7xl gap-6 p-4 sm:p-6 md:grid-cols-[1fr_300px] lg:grid-cols-[1fr_350px]">
        <MovieResults
          isSearching={isSearching}
          isLoadingGenreMovies={isLoadingGenreMovies}
          searchResults={searchResults}
          genreBlendedMovies={genreBlendedMovies}
          recommendedMovies={recommendedMovies}
          comparisonMovies={comparisonMovies}
          selectedGenres={selectedGenres}
          selectedMood={selectedMood}
          onGenresSelected={setSelectedGenres}
          onMoodSelect={handleMoodSelect}
          onMovieWatched={handleMovieWatched}
          onMovieClick={handleMovieClick}
        />

        <WatchList
          watchedMovies={watchedMovies}
          onDeleteMovie={handleDeleteMovie}
        />
      </main>

      <motion.footer 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="mt-8 pb-4 text-center text-sm"
      >
        <p className="text-transparent bg-clip-text bg-gradient-to-r from-netflix-red to-purple-500">
          Made with ❤️ by Aylin Vahabova
        </p>
      </motion.footer>
    </motion.div>
  );
};

export default Index;