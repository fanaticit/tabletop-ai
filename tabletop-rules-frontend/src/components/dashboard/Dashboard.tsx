// src/components/dashboard/Dashboard.tsx - Post-login command center
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useAuthStore } from '../../stores/authStore';
import { useGameStore } from '../../stores/gameStore';
import { useConversationStore } from '../../stores/conversationStore';
import GameGrid from './GameGrid';
import ConversationHistory from './ConversationHistory';
import QuickActions from './QuickActions';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const { selectGame } = useGameStore();
  const { 
    conversations, 
    createNewConversation,
    loadRecentConversations 
  } = useConversationStore();
  
  const [selectedView, setSelectedView] = useState<'games' | 'recent'>('games');

  // Fetch games using React Query
  const { 
    data: games = [], 
    isLoading: gamesLoading, 
    error: gamesError 
  } = useQuery({
    queryKey: ['games'],
    queryFn: async () => {
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/games/`);
      if (!response.ok) {
        throw new Error('Failed to fetch games');
      }
      const data = await response.json();
      return data.games || [];
    },
  });

  useEffect(() => {
    // Load recent conversations on dashboard mount
    loadRecentConversations();
  }, [loadRecentConversations]);

  const handleStartNewChat = async (gameId: string, gameName: string) => {
    try {
      const conversation = await createNewConversation(gameId, gameName);
      navigate(`/chat/${gameId}/${conversation.id}`);
    } catch (error) {
      console.error('Failed to start new chat:', error);
    }
  };

  const handleContinueConversation = (conversation: any) => {
    navigate(`/chat/${conversation.gameId}/${conversation.id}`);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (gamesLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">
                🎲 Tabletop Rules AI
              </h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <span className="text-gray-600">Welcome, {user?.username}</span>
              <button
                onClick={handleLogout}
                className="text-gray-500 hover:text-gray-700 px-3 py-1 rounded-md text-sm font-medium"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Ready to explore game rules?
          </h2>
          <p className="text-lg text-gray-600">
            Choose a game to start asking questions, or continue a previous conversation.
          </p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                  <span className="text-blue-600 font-bold">🎮</span>
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Available Games</p>
                <p className="text-2xl font-bold text-gray-900">{games.length}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                  <span className="text-green-600 font-bold">💬</span>
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Conversations</p>
                <p className="text-2xl font-bold text-gray-900">{conversations.length}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                  <span className="text-purple-600 font-bold">⭐</span>
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Recent Chats</p>
                <p className="text-2xl font-bold text-gray-900">
                  {conversations.filter(c => {
                    const dayAgo = new Date();
                    dayAgo.setDate(dayAgo.getDate() - 1);
                    return new Date(c.lastMessageAt) > dayAgo;
                  }).length}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* View Toggle */}
        <div className="flex space-x-1 mb-6 bg-gray-100 p-1 rounded-lg w-fit">
          <button
            onClick={() => setSelectedView('games')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              selectedView === 'games'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Browse Games
          </button>
          <button
            onClick={() => setSelectedView('recent')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              selectedView === 'recent'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Recent Conversations
          </button>
        </div>

        {/* Content Area */}
        <div className="space-y-8">
          {selectedView === 'games' && (
            <section>
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-xl font-semibold text-gray-900">
                  Choose a Game
                </h3>
                <QuickActions />
              </div>
              
              {gamesError ? (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <p className="text-red-700">Error loading games: {(gamesError as Error).message}</p>
                </div>
              ) : (
                <GameGrid 
                  games={games} 
                  onStartChat={handleStartNewChat}
                />
              )}
            </section>
          )}

          {selectedView === 'recent' && (
            <section>
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-xl font-semibold text-gray-900">
                  Recent Conversations
                </h3>
                <button
                  onClick={() => setSelectedView('games')}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  Start New Chat
                </button>
              </div>
              
              <ConversationHistory 
                conversations={conversations}
                onContinueConversation={handleContinueConversation}
              />
            </section>
          )}
        </div>

        {/* Empty State */}
        {conversations.length === 0 && selectedView === 'recent' && (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">💬</span>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No conversations yet
            </h3>
            <p className="text-gray-500 mb-6">
              Start your first conversation by selecting a game and asking about rules.
            </p>
            <button
              onClick={() => setSelectedView('games')}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
            >
              Browse Games
            </button>
          </div>
        )}
      </main>
    </div>
  );
};

export default Dashboard;