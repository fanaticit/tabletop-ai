import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface Game {
  game_id: string;
  name: string;
  description?: string;
  complexity?: string;
  rule_count: number;
  ai_tags?: string[];
  created_at?: string;
  updated_at?: string;
}

interface GameStore {
  selectedGame: Game | null;
  selectGame: (game: Game) => void;
  clearSelection: () => void;
}

export const useGameStore = create<GameStore>()(
  persist(
    (set) => ({
      selectedGame: null,
      
      selectGame: (game: Game) => {
        set({ selectedGame: game });
        console.log('Game selected:', game.name);
      },
      
      clearSelection: () => set({ selectedGame: null }),
    }),
    {
      name: 'game-selection',
      partialize: (state) => ({ selectedGame: state.selectedGame }),
    }
  )
);