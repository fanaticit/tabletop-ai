import React from 'react';
import { useMutation } from '@tanstack/react-query';
import { useNavigate, useParams } from 'react-router-dom';
import { useConversationStore } from '../../stores/conversationStore';
import { useGameStore } from '../../stores/gameStore';
import { useAuthStore } from '../../stores/authStore';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';

interface StructuredChatResponse {
  query: string;
  game_system: string;
  structured_response: {
    id: string;
    content: {
      summary: {
        text: string;
        confidence: number;
      };
      sections: Array<{
        id: string;
        title: string;
        content: string;
        type: string;
        level: number;
        collapsible: boolean;
        expanded: boolean;
      }>;
      sources: Array<{
        type: string;
        reference: string;
        url?: string;
        page?: number;
      }>;
    };
  };
  search_method: string;
  timestamp: string;
}

// Legacy format for backwards compatibility
interface QueryResponse {
  results: Array<{
    game_id: string;
    category_id: string;
    title: string;
    content: string;
    chunk_metadata?: {
      source_file?: string;
      uploaded_without_ai?: boolean;
    };
  }>;
  query: string;
}

export const ChatInterface: React.FC = () => {
  const navigate = useNavigate();
  const { gameId, conversationId } = useParams<{ gameId?: string; conversationId?: string }>();
  const { messages, isLoading, currentGameId, addMessage, setLoading, setCurrentGame } = useConversationStore();
  const { selectedGame } = useGameStore();
  const { token, user, logout } = useAuthStore();

  React.useEffect(() => {
    if (selectedGame && currentGameId !== selectedGame.game_id) {
      setCurrentGame(selectedGame.game_id);
    }
  }, [selectedGame, currentGameId, setCurrentGame]);

  const queryMutation = useMutation({
    mutationFn: async (query: string): Promise<StructuredChatResponse | QueryResponse> => {
      if (!selectedGame) {
        throw new Error('No game selected');
      }

      const response = await fetch('/api/chat/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          query,
          game_system: selectedGame.game_id,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to query chat API');
      }

      return response.json();
    },
    onMutate: async (query: string) => {
      setLoading(true);
      addMessage({
        role: 'user',
        content: query,
        gameId: selectedGame?.game_id,
      });
    },
    onSuccess: (data: StructuredChatResponse | QueryResponse) => {
      // Check if this is the new structured response format
      if ('structured_response' in data) {
        // Handle new structured response
        const structuredData = data as StructuredChatResponse;
        
        // Transform API response to match frontend types
        const transformedResponse = {
          ...structuredData.structured_response,
          content: {
            ...structuredData.structured_response.content,
            sections: structuredData.structured_response.content.sections.map(section => ({
              ...section,
              type: section.type as 'summary' | 'explanation' | 'examples' | 'edge_cases',
              subsections: []
            })),
            sources: structuredData.structured_response.content.sources.map(source => ({
              ...source,
              type: source.type as 'rulebook' | 'faq' | 'designer_notes' | 'community'
            }))
          }
        };

        addMessage({
          role: 'assistant',
          content: structuredData.structured_response.content.summary.text, // Fallback content
          gameId: selectedGame?.game_id,
          structuredResponse: transformedResponse,
        });
      } else {
        // Handle legacy response format for backwards compatibility
        const legacyData = data as QueryResponse;
        const responseContent = legacyData.results.length > 0
          ? `Found ${legacyData.results.length} relevant rule${legacyData.results.length === 1 ? '' : 's'}:\n\n${legacyData.results.map(rule => `**${rule.title}**\n${rule.content}`).join('\n\n')}`
          : 'No specific rules found for your query.';

        addMessage({
          role: 'assistant',
          content: responseContent,
          gameId: selectedGame?.game_id,
          sources: legacyData.results.map(rule => ({
            game_id: rule.game_id,
            category_id: rule.category_id,
            title: rule.title,
            content: rule.content,
            chunk_metadata: rule.chunk_metadata,
          })),
        });
      }
    },
    onError: (error) => {
      console.error('Query failed:', error);
      addMessage({
        role: 'assistant',
        content: 'Sorry, I encountered an error while processing your question. Please try again.',
        gameId: selectedGame?.game_id,
      });
    },
    onSettled: () => {
      setLoading(false);
    },
  });

  const handleSendMessage = (message: string) => {
    if (!selectedGame) {
      addMessage({
        role: 'assistant',
        content: 'Please select a game first to ask questions about its rules.',
      });
      return;
    }
    
    queryMutation.mutate(message);
  };

  const currentMessages = currentGameId 
    ? messages.filter(msg => msg.gameId === currentGameId)
    : messages;

  if (!selectedGame) {
    return (
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center', 
        height: '100%',
        color: '#666',
        fontSize: '16px' 
      }}>
        Please select a game to start asking questions about its rules.
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Navigation Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Left side - Logo and Navigation */}
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/')}
                className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-gray-700 hover:text-blue-600 hover:bg-gray-50 transition-colors"
              >
                <span className="mr-2">🎲</span>
                Dashboard
              </button>
              
              <div className="h-6 w-px bg-gray-300"></div>
              
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-sm">
                  {selectedGame ? (selectedGame.game_id === 'chess' ? '♟️' : '🎲') : '🎲'}
                </div>
                <div>
                  <h1 className="text-lg font-semibold text-gray-900">
                    {selectedGame?.name || 'Select a Game'} Chat
                  </h1>
                  {conversationId && (
                    <p className="text-xs text-gray-500">
                      Conversation: {conversationId.slice(0, 8)}...
                    </p>
                  )}
                </div>
              </div>
            </div>

            {/* Right side - Actions and User */}
            <div className="flex items-center space-x-3">
              <button
                onClick={() => navigate('/games')}
                className="inline-flex items-center px-3 py-1.5 border border-gray-300 text-xs font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Switch Game
              </button>
              
              <button
                onClick={() => navigate('/')}
                className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <span className="mr-1">🏠</span>
                Home
              </button>
              
              <div className="h-6 w-px bg-gray-300"></div>
              
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-600">
                  {user?.username || 'User'}
                </span>
                <button
                  onClick={() => {
                    logout();
                    navigate('/login');
                  }}
                  className="text-gray-500 hover:text-gray-700 text-sm"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Chat Content */}
      <div className="flex-1 flex flex-col" style={{ maxHeight: 'calc(100vh - 64px)' }}>
        {/* Game status bar */}
        {selectedGame && (
          <div className="bg-blue-50 border-b border-blue-200 px-4 py-2">
            <div className="flex items-center justify-between">
              <p className="text-sm text-blue-700">
                <span className="font-medium">Ready to help with {selectedGame.name} rules!</span>
                <span className="ml-2 text-blue-500">Ask any question about gameplay, rules, or strategies.</span>
              </p>
              <div className="flex items-center space-x-2 text-xs text-blue-600">
                <span className="inline-flex items-center">
                  <span className="w-2 h-2 bg-green-400 rounded-full mr-1"></span>
                  AI Powered
                </span>
              </div>
            </div>
          </div>
        )}
        
        <MessageList 
          messages={currentMessages} 
          isLoading={isLoading} 
        />
        
        <div className="bg-white border-t border-gray-200 p-4">
          <MessageInput
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
            disabled={!selectedGame}
          />
        </div>
      </div>
    </div>
  );
};