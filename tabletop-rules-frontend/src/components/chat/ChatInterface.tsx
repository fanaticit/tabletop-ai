import React from 'react';
import { useMutation } from '@tanstack/react-query';
import { useConversationStore } from '../../stores/conversationStore';
import { useGameStore } from '../../stores/gameStore';
import { useAuthStore } from '../../stores/authStore';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';

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
  const { messages, isLoading, currentGameId, addMessage, setLoading, setCurrentGame } = useConversationStore();
  const { selectedGame } = useGameStore();
  const { token } = useAuthStore();

  React.useEffect(() => {
    if (selectedGame && currentGameId !== selectedGame.game_id) {
      setCurrentGame(selectedGame.game_id);
    }
  }, [selectedGame, currentGameId, setCurrentGame]);

  const queryMutation = useMutation({
    mutationFn: async (query: string): Promise<QueryResponse> => {
      if (!selectedGame) {
        throw new Error('No game selected');
      }

      const response = await fetch('/api/chat/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          query,
          game_system: selectedGame.game_id,
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('API Error:', response.status, response.statusText, errorText);
        throw new Error(`Failed to query rules (${response.status}): ${errorText}`);
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
    onSuccess: (data: QueryResponse) => {
      const responseContent = data.results.length > 0
        ? `Found ${data.results.length} relevant rule${data.results.length === 1 ? '' : 's'}:\n\n${data.results.map(rule => `**${rule.title}**\n${rule.content}`).join('\n\n')}`
        : 'No specific rules found for your query.';

      addMessage({
        role: 'assistant',
        content: responseContent,
        gameId: selectedGame?.game_id,
        sources: data.results,
      });
    },
    onError: (error: Error) => {
      addMessage({
        role: 'assistant',
        content: `Sorry, I encountered an error: ${error.message}`,
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
    <div style={{ 
      display: 'flex', 
      flexDirection: 'column', 
      height: '100%',
      maxHeight: '100%',
    }}>
      <div style={{ 
        padding: '16px',
        borderBottom: '1px solid #eee',
        backgroundColor: '#f8f9fa',
      }}>
        <h2 style={{ 
          margin: 0, 
          fontSize: '18px',
          color: '#333' 
        }}>
          {selectedGame.name} - Rules Chat
        </h2>
        <p style={{ 
          margin: '4px 0 0 0', 
          fontSize: '14px', 
          color: '#666' 
        }}>
          Ask questions about the game rules
        </p>
      </div>
      
      <MessageList 
        messages={currentMessages} 
        isLoading={isLoading} 
      />
      
      <div style={{ 
        padding: '16px',
        borderTop: '1px solid #eee',
        backgroundColor: '#fff',
      }}>
        <MessageInput
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
          disabled={!selectedGame}
        />
      </div>
    </div>
  );
};