import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface Game {
  id: string;
  name: string;
  description: string;
  category: string;
  rule_count: number;
  created_at?: string;
  updated_at?: string;
}

interface GameStore {
  selectedGame: Game | null;
  availableGames: Game[];
  isLoading: boolean;
  selectGame: (game: Game) => void;
  clearSelection: () => void;
  setGames: (games: Game[]) => void;
  setLoading: (loading: boolean) => void;
}

export const useGameStore = create<GameStore>()(
  persist(
    (set, get) => ({
      selectedGame: null,
      availableGames: [],
      isLoading: false,
      
      selectGame: (game: Game) => {
        set({ selectedGame: game });
        console.log('Game selected:', game.name);
      },
      
      clearSelection: () => set({ selectedGame: null }),
      
      setGames: (games: Game[]) => set({ availableGames: games }),
      
      setLoading: (loading: boolean) => set({ isLoading: loading }),
    }),
    {
      name: 'game-selection',
      partialize: (state) => ({ selectedGame: state.selectedGame }),
    }
  )
);