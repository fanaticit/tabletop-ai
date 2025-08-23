import { create } from 'zustand';
import { persist, devtools } from 'zustand/middleware';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  gameId?: string;
  sources?: RuleChunk[];
}

export interface RuleChunk {
  game_id: string;
  category_id: string;
  title: string;
  content: string;
  chunk_metadata?: {
    source_file?: string;
    uploaded_without_ai?: boolean;
  };
}

interface ConversationStore {
  messages: Message[];
  isLoading: boolean;
  currentGameId: string | null;
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void;
  clearConversation: () => void;
  setLoading: (loading: boolean) => void;
  setCurrentGame: (gameId: string | null) => void;
  getMessagesForGame: (gameId: string) => Message[];
}

export const useConversationStore = create<ConversationStore>()(
  devtools(
    persist(
      (set, get) => ({
        messages: [],
        isLoading: false,
        currentGameId: null,

        addMessage: (messageData) => {
          const message: Message = {
            ...messageData,
            id: crypto.randomUUID(),
            timestamp: new Date(),
          };
          
          set((state) => ({
            messages: [...state.messages, message]
          }));
        },

        clearConversation: () => {
          set({ messages: [], isLoading: false });
        },

        setLoading: (loading: boolean) => {
          set({ isLoading: loading });
        },

        setCurrentGame: (gameId: string | null) => {
          set({ currentGameId: gameId });
        },

        getMessagesForGame: (gameId: string) => {
          return get().messages.filter(msg => msg.gameId === gameId);
        },
      }),
      {
        name: 'conversation-storage',
        partialize: (state) => ({
          messages: state.messages,
          currentGameId: state.currentGameId,
        }),
      }
    ),
    { name: 'conversation-store' }
  )
);