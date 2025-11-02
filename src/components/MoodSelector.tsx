import { Button } from "@/components/ui/button";
import { motion } from "framer-motion";
import { Smile, Frown, Compass, Heart, Zap, Star } from "lucide-react";

interface MoodSelectorProps {
  onMoodSelect: (mood: string | null) => void;
  selectedMood: string | null;
}

const moods = [
  { id: 'happy', icon: Smile, label: 'Happy', color: 'from-yellow-400 to-orange-500', genres: ['comedy', 'animation', 'family'] },
  { id: 'sad', icon: Frown, label: 'Melancholic', color: 'from-blue-400 to-indigo-500', genres: ['drama', 'romance'] },
  { id: 'adventurous', icon: Compass, label: 'Adventurous', color: 'from-green-400 to-emerald-500', genres: ['action', 'adventure', 'sci-fi'] },
  { id: 'romantic', icon: Heart, label: 'Romantic', color: 'from-pink-400 to-rose-500', genres: ['romance', 'comedy'] },
  { id: 'excited', icon: Zap, label: 'Excited', color: 'from-purple-400 to-violet-500', genres: ['action', 'thriller'] },
  { id: 'nostalgic', icon: Star, label: 'Nostalgic', color: 'from-amber-400 to-yellow-500', genres: ['classic', 'family'] },
];

const MoodSelector = ({ onMoodSelect, selectedMood }: MoodSelectorProps) => {
  return (
    <div className="mb-8 bg-black/20 p-6 rounded-xl backdrop-blur-sm">
      <h2 className="text-xl font-semibold text-white mb-6 flex items-center gap-3">
        <Smile className="h-6 w-6 text-netflix-red animate-bounce" />
        How are you feeling today?
      </h2>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3">
        {moods.map((mood) => {
          const Icon = mood.icon;
          const isSelected = selectedMood === mood.id;
          
          return (
            <motion.div
              key={mood.id}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="relative"
            >
              <Button
                variant="outline"
                className={`
                  w-full h-full min-h-[100px] flex flex-col items-center gap-3 
                  border-2 transition-all duration-300
                  ${isSelected 
                    ? 'bg-netflix-red border-netflix-red shadow-lg shadow-netflix-red/20' 
                    : `bg-gradient-to-br ${mood.color} bg-opacity-10 hover:bg-opacity-20 border-white/20 hover:border-white/40`}
                `}
                onClick={() => onMoodSelect(isSelected ? null : mood.id)}
              >
                <Icon className={`h-8 w-8 ${isSelected ? 'text-white' : 'text-white/70'}`} />
                <span className={`text-sm font-medium ${isSelected ? 'text-white' : 'text-white/70'}`}>
                  {mood.label}
                </span>
                {isSelected && (
                  <motion.div
                    className="absolute inset-0 rounded-md"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.3 }}
                  >
                    <div className="absolute inset-0 bg-netflix-red opacity-20" />
                    <div className="absolute -inset-px rounded-md border-2 border-netflix-red" />
                  </motion.div>
                )}
              </Button>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};

export default MoodSelector;