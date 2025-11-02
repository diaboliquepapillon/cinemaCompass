import { Button } from "@/components/ui/button";
import { motion } from "framer-motion";
import { Film } from "lucide-react";

interface Genre {
  id: number;
  name: string;
}

const genres = [
  { id: 28, name: "Action" },
  { id: 12, name: "Adventure" },
  { id: 16, name: "Animation" },
  { id: 35, name: "Comedy" },
  { id: 80, name: "Crime" },
  { id: 18, name: "Drama" },
  { id: 14, name: "Fantasy" },
  { id: 27, name: "Horror" },
  { id: 10749, name: "Romance" },
  { id: 878, name: "Science Fiction" },
  { id: 53, name: "Thriller" }
];

interface GenreBlenderProps {
  onGenresSelected: (genres: Genre[]) => void;
  selectedGenres: Genre[];
}

const GenreBlender = ({ onGenresSelected, selectedGenres }: GenreBlenderProps) => {
  const handleGenreClick = (genre: Genre) => {
    if (selectedGenres.find(g => g.id === genre.id)) {
      onGenresSelected(selectedGenres.filter(g => g.id !== genre.id));
    } else if (selectedGenres.length < 2) {
      onGenresSelected([...selectedGenres, genre]);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Film className="h-5 w-5 text-netflix-red" />
        <h3 className="text-lg font-semibold text-white">Blend Genres</h3>
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
        {genres.map((genre) => (
          <motion.div
            key={genre.id}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <Button
              variant="outline"
              className={`w-full ${
                selectedGenres.find(g => g.id === genre.id)
                  ? "bg-netflix-red text-white border-netflix-red"
                  : "bg-black/20 text-white/80 border-white/10 hover:bg-white/10"
              }`}
              onClick={() => handleGenreClick(genre)}
            >
              {genre.name}
            </Button>
          </motion.div>
        ))}
      </div>
      {selectedGenres.length > 0 && (
        <p className="text-sm text-white/60">
          {selectedGenres.length === 1
            ? "Select one more genre to blend"
            : `Blending ${selectedGenres.map(g => g.name).join(" + ")}`}
        </p>
      )}
    </div>
  );
};

export default GenreBlender;