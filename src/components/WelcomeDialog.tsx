import { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Search, Film, Star } from "lucide-react";

export function WelcomeDialog() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const hasSeenWelcome = localStorage.getItem("hasSeenWelcome");
    if (!hasSeenWelcome) {
      setOpen(true);
      localStorage.setItem("hasSeenWelcome", "true");
    }
  }, []);

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogContent className="sm:max-w-[425px] bg-netflix-black border-white/10">
        <DialogHeader>
          <DialogTitle className="text-2xl text-white">Welcome to CineCompass! 🎬</DialogTitle>
          <DialogDescription className="text-white/70">
            Let's help you discover your next favorite movie
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-6 py-4">
          <div className="flex items-start gap-4">
            <Search className="w-6 h-6 text-netflix-red mt-1" />
            <div>
              <h3 className="font-medium text-white">Search Movies</h3>
              <p className="text-sm text-white/70">
                Use the search bar to find any movie you're interested in. Clear the search to see your recommendations!
              </p>
            </div>
          </div>
          <div className="flex items-start gap-4">
            <Film className="w-6 h-6 text-netflix-red mt-1" />
            <div>
              <h3 className="font-medium text-white">Build Your List</h3>
              <p className="text-sm text-white/70">
                Add movies to your list by dragging them to the right. Your list helps personalize your recommendations.
              </p>
            </div>
          </div>
          <div className="flex items-start gap-4">
            <Star className="w-6 h-6 text-netflix-red mt-1" />
            <div>
              <h3 className="font-medium text-white">Get Recommendations</h3>
              <p className="text-sm text-white/70">
                Based on your list, we'll suggest similar movies. Remember to clear the search bar to see your personalized recommendations!
              </p>
            </div>
          </div>
        </div>
        <DialogFooter>
          <Button 
            onClick={() => setOpen(false)}
            className="w-full bg-netflix-red hover:bg-netflix-red/90"
          >
            Got it, let's explore!
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}