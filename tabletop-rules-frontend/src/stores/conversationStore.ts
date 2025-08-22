// Conversation store - to be implemented
// This is a placeholder file to prevent TypeScript module errors

export interface Conversation {
  id: string;
  gameId: string;
  title: string;
  createdAt: Date;
  updatedAt: Date;
  messageCount: number;
}

// Placeholder store - will be implemented later
export const useConversationStore = () => ({
  conversations: {},
  currentConversationId: null,
  startNewConversation: () => 'placeholder',
  setCurrentConversation: () => {},
  updateConversation: () => {},
  deleteConversation: () => {},
  getConversationsForGame: () => [],
});

export default useConversationStore;