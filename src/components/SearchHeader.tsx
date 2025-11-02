import { Input } from "@/components/ui/input";
import { Search } from "lucide-react";
import { motion } from "framer-motion";
import { useIsMobile } from "@/hooks/use-mobile";
import { Compass } from "lucide-react";

interface SearchHeaderProps {
  searchTerm: string;
  onSearchChange: (value: string) => void;
  onSubmit: (e: React.FormEvent) => void;
}

const SearchHeader = ({ searchTerm, onSearchChange, onSubmit }: SearchHeaderProps) => {
  const isMobile = useIsMobile();

  return (
    <motion.header 
      initial={{ y: -20 }}
      animate={{ y: 0 }}
      className="sticky top-0 z-50 bg-gradient-to-b from-black/80 to-transparent backdrop-blur-sm"
    >
      <div className="mx-auto flex max-w-7xl flex-col sm:flex-row items-center gap-4 px-4 py-4">
        <motion.div 
          className="flex items-center gap-2"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          >
            <Compass className="h-6 w-6 sm:h-8 sm:w-8 text-netflix-red" />
          </motion.div>
          <h1 className="text-xl sm:text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-netflix-red to-purple-500">
            CineCompass
          </h1>
        </motion.div>
        
        <form onSubmit={onSubmit} className="w-full sm:flex-1 px-2 sm:px-4 md:max-w-2xl">
          <motion.div 
            className="group relative transition-all duration-300 focus-within:scale-105"
            whileHover={{ scale: 1.02 }}
          >
            <Input
              type="text"
              placeholder={isMobile ? "Search & swipe right to add..." : "Search for movies..."}
              value={searchTerm}
              onChange={(e) => onSearchChange(e.target.value)}
              className="w-full bg-black/20 pl-10 text-white placeholder:text-white/50 focus:ring-2 focus:ring-netflix-red/50 border-white/10 transition-all duration-300 hover:border-white/20"
            />
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 transform text-white/50 group-focus-within:text-netflix-red" />
          </motion.div>
        </form>

        <motion.div 
          className="text-sm font-medium text-white/80 hidden sm:block"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          {searchTerm.length} results
        </motion.div>
      </div>
    </motion.header>
  );
};

export default SearchHeader;