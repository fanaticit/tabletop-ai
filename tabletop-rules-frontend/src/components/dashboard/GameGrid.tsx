// src/components/dashboard/GameGrid.tsx - Visual game cards with enhanced UI
import React from 'react';

interface Game {
  game_id: string;
  name: string;
  publisher?: string;
  version?: string;
  complexity?: 'easy' | 'medium' | 'hard';
  min_players?: number;
  max_players?: number;
  rule_count?: number;
  categories?: string[];
}

interface GameGridProps {
  games: Game[];
  onStartChat: (gameId: string, gameName: string) => void;
}

const GameGrid: React.FC<GameGridProps> = ({ games, onStartChat }) => {
  const getComplexityColor = (complexity?: string) => {
    switch (complexity) {
      case 'easy': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'hard': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getComplexityIcon = (complexity?: string) => {
    switch (complexity) {
      case 'easy': return '🟢';
      case 'medium': return '🟡';
      case 'hard': return '🔴';
      default: return '⚪';
    }
  };

  const getGameIcon = (gameId: string) => {
    // Return appropriate emoji for each game type
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

  const formatPlayerCount = (min?: number, max?: number) => {
    if (!min && !max) return 'Any players';
    if (min === max) return `${min} player${min === 1 ? '' : 's'}`;
    if (!max) return `${min}+ players`;
    if (!min) return `Up to ${max} players`;
    return `${min}-${max} players`;
  };

  if (games.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <span className="text-2xl">🎲</span>
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          No games available
        </h3>
        <p className="text-gray-500">
          Upload some game rules to get started with AI-powered rule assistance.
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {games.map((game) => (
        <div
          key={game.game_id}
          className="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow duration-200"
        >
          {/* Game Header */}
          <div className="p-6 pb-4">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center text-2xl">
                  {getGameIcon(game.game_id)}
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 leading-tight">
                    {game.name}
                  </h3>
                  {game.publisher && (
                    <p className="text-sm text-gray-500">
                      by {game.publisher}
                    </p>
                  )}
                </div>
              </div>
              
              {/* Complexity Badge */}
              <div className="flex items-center">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getComplexityColor(game.complexity)}`}>
                  <span className="mr-1">{getComplexityIcon(game.complexity)}</span>
                  {game.complexity || 'Unknown'}
                </span>
              </div>
            </div>

            {/* Game Details */}
            <div className="space-y-2">
              <div className="flex items-center text-sm text-gray-600">
                <span className="mr-2">👥</span>
                {formatPlayerCount(game.min_players, game.max_players)}
              </div>
              
              {game.rule_count && game.rule_count > 0 && (
                <div className="flex items-center text-sm text-gray-600">
                  <span className="mr-2">📚</span>
                  {game.rule_count} rule{game.rule_count === 1 ? '' : 's'} available
                </div>
              )}

              {game.version && (
                <div className="flex items-center text-sm text-gray-600">
                  <span className="mr-2">📋</span>
                  {game.version}
                </div>
              )}
            </div>

            {/* Categories */}
            {game.categories && game.categories.length > 0 && (
              <div className="mt-3">
                <div className="flex flex-wrap gap-1">
                  {game.categories.slice(0, 3).map((category) => (
                    <span
                      key={category}
                      className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-gray-100 text-gray-700"
                    >
                      {category}
                    </span>
                  ))}
                  {game.categories.length > 3 && (
                    <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-gray-100 text-gray-700">
                      +{game.categories.length - 3} more
                    </span>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Action Section */}
          <div className="px-6 py-4 bg-gray-50 rounded-b-lg border-t border-gray-100">
            <button
              onClick={() => onStartChat(game.game_id, game.name)}
              className="w-full inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200"
            >
              <span className="mr-2">💬</span>
              Start Chat
            </button>
            
            <div className="mt-2 text-center">
              <span className="text-xs text-gray-500">
                Ask questions about rules and gameplay
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default GameGrid;