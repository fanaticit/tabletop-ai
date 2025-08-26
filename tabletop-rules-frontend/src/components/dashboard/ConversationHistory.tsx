// src/components/dashboard/ConversationHistory.tsx - Recent conversations with preview
import React from 'react';

interface Conversation {
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

interface ConversationHistoryProps {
  conversations: Conversation[];
  onContinueConversation: (conversation: Conversation) => void;
}

const ConversationHistory: React.FC<ConversationHistoryProps> = ({ 
  conversations, 
  onContinueConversation 
}) => {
  const formatRelativeTime = (date: Date) => {
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);
    
    if (diffInSeconds < 60) {
      return 'Just now';
    } else if (diffInSeconds < 3600) {
      const minutes = Math.floor(diffInSeconds / 60);
      return `${minutes} minute${minutes === 1 ? '' : 's'} ago`;
    } else if (diffInSeconds < 86400) {
      const hours = Math.floor(diffInSeconds / 3600);
      return `${hours} hour${hours === 1 ? '' : 's'} ago`;
    } else if (diffInSeconds < 604800) {
      const days = Math.floor(diffInSeconds / 86400);
      return `${days} day${days === 1 ? '' : 's'} ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  const getGameIcon = (gameId: string) => {
    const icons: { [key: string]: string } = {
      chess: '♟️',
      checkers: '⚫',
      monopoly: '🏠',
      scrabble: '🔤',
      risk: '🌍',
      settlers: '🏘️',
      dnd5e: '🐉',
      pathfinder: '⚔️',
      magic: '🎴',
      poker: '🃏',
      blackjack: '🎰',
    };
    
    return icons[gameId] || '🎲';
  };

  const truncateMessage = (message: string, maxLength: number = 100) => {
    if (message.length <= maxLength) return message;
    return message.slice(0, maxLength) + '...';
  };

  if (conversations.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <span className="text-2xl">💬</span>
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          No conversations yet
        </h3>
        <p className="text-gray-500">
          Start your first conversation by selecting a game and asking about rules.
        </p>
      </div>
    );
  }

  // Sort conversations by last message time (most recent first)
  const sortedConversations = [...conversations].sort((a, b) => 
    new Date(b.lastMessageAt).getTime() - new Date(a.lastMessageAt).getTime()
  );

  return (
    <div className="space-y-4">
      {sortedConversations.map((conversation) => (
        <div
          key={conversation.id}
          className={`bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-all duration-200 cursor-pointer ${
            conversation.isActive ? 'ring-2 ring-blue-500 border-blue-300' : ''
          }`}
          onClick={() => onContinueConversation(conversation)}
        >
          <div className="p-6">
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-4 flex-1 min-w-0">
                {/* Game Icon */}
                <div className="flex-shrink-0">
                  <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center text-lg">
                    {getGameIcon(conversation.gameId)}
                  </div>
                </div>

                {/* Conversation Details */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-1">
                    <h3 className="text-lg font-semibold text-gray-900 truncate">
                      {conversation.title}
                    </h3>
                    {conversation.isActive && (
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        Active
                      </span>
                    )}
                  </div>
                  
                  <div className="flex items-center space-x-2 text-sm text-gray-500 mb-2">
                    <span>{conversation.gameName}</span>
                    <span>•</span>
                    <span>{conversation.messageCount} message{conversation.messageCount === 1 ? '' : 's'}</span>
                    <span>•</span>
                    <span>{formatRelativeTime(new Date(conversation.lastMessageAt))}</span>
                  </div>

                  {/* Last Message Preview */}
                  <div className="text-sm text-gray-600 bg-gray-50 rounded-md p-3 border-l-4 border-gray-200">
                    <p className="italic">
                      "{truncateMessage(conversation.lastMessage)}"
                    </p>
                  </div>
                </div>
              </div>

              {/* Continue Button */}
              <div className="flex-shrink-0 ml-4">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onContinueConversation(conversation);
                  }}
                  className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200"
                >
                  Continue
                  <span className="ml-1">→</span>
                </button>
              </div>
            </div>

            {/* Conversation Metadata */}
            <div className="mt-4 pt-4 border-t border-gray-100">
              <div className="flex items-center justify-between text-xs text-gray-500">
                <span>
                  Started {formatRelativeTime(new Date(conversation.createdAt))}
                </span>
                <div className="flex items-center space-x-4">
                  <span className="flex items-center">
                    <span className="mr-1">💬</span>
                    {conversation.messageCount} messages
                  </span>
                  <span className="flex items-center">
                    <span className="mr-1">🎲</span>
                    {conversation.gameName}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      ))}

      {/* Load More Button (if needed in future) */}
      {conversations.length >= 10 && (
        <div className="text-center py-4">
          <button className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
            Load More Conversations
          </button>
        </div>
      )}
    </div>
  );
};

export default ConversationHistory;