import { create } from 'zustand';
import { persist, devtools } from 'zustand/middleware';
import { StructuredRuleResponse } from '../components/chat/StructuredResponse';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  gameId?: string;
  conversationId?: string;
  sources?: RuleChunk[];
  structuredResponse?: StructuredRuleResponse;
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

export interface Conversation {
  id: string;
  gameId: string;
  gameName: string;
  title: string;
  lastMessage: string;
  lastMessageAt: Date;
  messageCount: number;
  createdAt: Date;
  isActive?: boolean;
}

interface ConversationStore {
  // Legacy support for current messages (active conversation)
  messages: Message[];
  isLoading: boolean;
  currentGameId: string | null;
  
  // New conversation management
  conversations: Conversation[];
  activeConversationId: string | null;
  
  // Legacy methods (maintained for compatibility)
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void;
  clearConversation: () => void;
  setLoading: (loading: boolean) => void;
  setCurrentGame: (gameId: string | null) => void;
  getMessagesForGame: (gameId: string) => Message[];
  
  // New conversation methods
  createNewConversation: (gameId: string, gameName: string) => Promise<Conversation>;
  loadConversation: (conversationId: string) => Promise<void>;
  deleteConversation: (conversationId: string) => void;
  getGameConversations: (gameId: string) => Conversation[];
  generateChatTitle: (firstMessage: string) => string;
  loadRecentConversations: () => Promise<void>;
  updateConversationLastMessage: (conversationId: string, message: string) => void;
}

export const useConversationStore = create<ConversationStore>()(
  devtools(
    persist(
      (set, get) => ({
        messages: [],
        isLoading: false,
        currentGameId: null,
        conversations: [],
        activeConversationId: null,

        // Legacy methods (maintained for compatibility)
        addMessage: (messageData) => {
          const message: Message = {
            ...messageData,
            id: crypto.randomUUID(),
            timestamp: new Date(),
          };
          
          set((state) => ({
            messages: [...state.messages, message]
          }));

          // If we have an active conversation, update its last message
          const state = get();
          if (state.activeConversationId && messageData.role === 'user') {
            get().updateConversationLastMessage(state.activeConversationId, messageData.content);
          }
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

        // New conversation methods
        createNewConversation: async (gameId: string, gameName: string): Promise<Conversation> => {
          const now = new Date();
          const conversation: Conversation = {
            id: crypto.randomUUID(),
            gameId,
            gameName,
            title: `New ${gameName} Chat`,
            lastMessage: '',
            lastMessageAt: now,
            messageCount: 0,
            createdAt: now,
            isActive: true,
          };

          set((state) => ({
            conversations: [conversation, ...state.conversations],
            activeConversationId: conversation.id,
            currentGameId: gameId,
            messages: [], // Clear current messages for new conversation
          }));

          return conversation;
        },

        loadConversation: async (conversationId: string): Promise<void> => {
          // For now, just simulate loading - in the future this would fetch from backend
          const state = get();
          const conversation = state.conversations.find(c => c.id === conversationId);
          
          if (conversation) {
            // Mark as active and set current game
            set((prevState) => ({
              activeConversationId: conversationId,
              currentGameId: conversation.gameId,
              conversations: prevState.conversations.map(c => ({
                ...c,
                isActive: c.id === conversationId
              })),
              messages: [], // In future, load actual messages from backend
            }));
          }
        },

        deleteConversation: (conversationId: string) => {
          set((state) => ({
            conversations: state.conversations.filter(c => c.id !== conversationId),
            ...(state.activeConversationId === conversationId ? {
              activeConversationId: null,
              messages: [],
              currentGameId: null,
            } : {})
          }));
        },

        getGameConversations: (gameId: string) => {
          return get().conversations.filter(c => c.gameId === gameId);
        },

        generateChatTitle: (firstMessage: string): string => {
          // Extract meaningful title from first user message
          const words = firstMessage.split(' ').slice(0, 4);
          const title = words.join(' ');
          return title.length > 40 ? title.slice(0, 40) + '...' : title;
        },

        loadRecentConversations: async (): Promise<void> => {
          // For now, just return existing conversations
          // In the future, this would fetch from backend API
          set((state) => ({
            conversations: state.conversations.sort((a, b) => 
              new Date(b.lastMessageAt).getTime() - new Date(a.lastMessageAt).getTime()
            )
          }));
        },

        updateConversationLastMessage: (conversationId: string, message: string) => {
          set((state) => ({
            conversations: state.conversations.map(c => 
              c.id === conversationId 
                ? {
                    ...c,
                    lastMessage: message,
                    lastMessageAt: new Date(),
                    messageCount: c.messageCount + 1,
                    title: c.title === `New ${c.gameName} Chat` ? get().generateChatTitle(message) : c.title
                  }
                : c
            )
          }));
        },
      }),
      {
        name: 'conversation-storage',
        partialize: (state) => ({
          messages: state.messages,
          currentGameId: state.currentGameId,
          conversations: state.conversations,
          activeConversationId: state.activeConversationId,
        }),
      }
    ),
    { name: 'conversation-store' }
  )
);