import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useGameStore } from '../../stores/gameStore';

interface Game {
  id: string;
  name: string;
  description: string;
  category: string;
  rule_count: number;
}

export const GameSelector: React.FC = () => {
  const { selectedGame, selectGame } = useGameStore();
  const [filterCategory, setFilterCategory] = useState<string | null>(null);

  const { data: gamesData, isLoading, error } = useQuery({
    queryKey: ['games'],
    queryFn: async () => {
      const response = await fetch('/api/games');
      if (!response.ok) {
        throw new Error('Failed to load games');
      }
      return response.json();
    },
    staleTime: 10 * 60 * 1000, // 10 minutes
  });

  const games = gamesData?.games || [];

  // Filter games by category
  const filteredGames = filterCategory 
    ? games.filter((game: Game) => game.category.toLowerCase() === filterCategory.toLowerCase())
    : games;

  // Get unique categories
  const categories = [...new Set(games.map((game: Game) => game.category))];

  if (error) {
    return (
      <div style={{ color: 'red', padding: '20px' }}>
        Failed to load games. Please try again later.
      </div>
    );
  }

  if (isLoading) {
    return (
      <div>
        <h2>Select a Game</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px' }}>
          {[...Array(6)].map((_, i) => (
            <div 
              key={i} 
              data-testid="game-skeleton"
              style={{ 
                height: '200px', 
                backgroundColor: '#f0f0f0', 
                borderRadius: '8px',
                animation: 'pulse 1.5s ease-in-out infinite'
              }}
            />
          ))}
        </div>
      </div>
    );
  }

  if (games.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '40px' }}>
        <p style={{ fontSize: '18px', color: '#666' }}>
          No games available. Please check back later.
        </p>
      </div>
    );
  }

  return (
    <div>
      <h2>Select a Game</h2>
      
      {selectedGame && (
        <div style={{ 
          marginBottom: '20px', 
          padding: '15px', 
          backgroundColor: '#e6f3ff', 
          borderRadius: '8px' 
        }}>
          <p style={{ fontWeight: 'bold', margin: '0 0 5px 0' }}>Currently Selected:</p>
          <p style={{ fontSize: '18px', margin: '0' }}>{selectedGame.name}</p>
        </div>
      )}

      {/* Category Filters */}
      {categories.length > 1 && (
        <div style={{ marginBottom: '20px' }}>
          <p style={{ fontWeight: 'bold', marginBottom: '10px' }}>Filter by Category:</p>
          <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
            <button 
              onClick={() => setFilterCategory(null)}
              style={{
                padding: '5px 12px',
                border: '1px solid #ccc',
                backgroundColor: filterCategory === null ? '#0066cc' : 'white',
                color: filterCategory === null ? 'white' : 'black',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              All
            </button>
            {categories.map((category) => (
              <button
                key={category}
                onClick={() => setFilterCategory(category)}
                style={{
                  padding: '5px 12px',
                  border: '1px solid #ccc',
                  backgroundColor: filterCategory === category ? '#0066cc' : 'white',
                  color: filterCategory === category ? 'white' : 'black',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                {category}
              </button>
            ))}
          </div>
        </div>
      )}
      
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', 
        gap: '20px' 
      }}>
        {filteredGames.map((game: Game) => (
          <div
            key={game.id}
            onClick={() => selectGame(game)}
            style={{
              padding: '20px',
              backgroundColor: 'white',
              border: selectedGame?.id === game.id ? '2px solid #0066cc' : '1px solid #ddd',
              borderRadius: '8px',
              cursor: 'pointer',
              transition: 'all 0.2s',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-2px)';
              e.currentTarget.style.boxShadow = '0 4px 8px rgba(0,0,0,0.15)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '10px' }}>
              <h3 style={{ margin: '0', fontSize: '20px' }}>
                {game.name}
              </h3>
              <span style={{ 
                padding: '2px 8px', 
                backgroundColor: '#28a745', 
                color: 'white', 
                borderRadius: '12px', 
                fontSize: '12px' 
              }}>
                {game.category}
              </span>
            </div>
            
            <p style={{ 
              color: '#666', 
              margin: '10px 0', 
              lineHeight: '1.4',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              display: '-webkit-box',
              WebkitLineClamp: 3,
              WebkitBoxOrient: 'vertical'
            }}>
              {game.description}
            </p>

            <p style={{ fontSize: '14px', color: '#888', margin: '10px 0' }}>
              {game.rule_count} rules available
            </p>
            
            <button 
              style={{
                width: '100%',
                padding: '8px',
                backgroundColor: selectedGame?.id === game.id ? '#0066cc' : '#f8f9fa',
                color: selectedGame?.id === game.id ? 'white' : '#333',
                border: selectedGame?.id === game.id ? 'none' : '1px solid #ddd',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '14px'
              }}
            >
              {selectedGame?.id === game.id ? 'Selected' : 'Select Game'}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};