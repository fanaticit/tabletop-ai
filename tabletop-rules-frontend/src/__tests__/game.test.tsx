import { render, screen, fireEvent, waitFor } from './test-utils';
import { rest } from 'msw';
import { server } from '../setupTests';
import { GameSelector } from '../components/games/GameSelector';
import { useGameStore } from '../stores/gameStore';
import { mockGame } from './test-utils';

// Mock the game store
jest.mock('../stores/gameStore');

const mockGames = [
  {
    id: 'chess',
    name: 'Chess',
    description: 'Classic strategy board game',
    category: 'Strategy',
    rule_count: 5,
  },
  {
    id: 'monopoly',
    name: 'Monopoly',
    description: 'Real estate trading game',
    category: 'Economic',
    rule_count: 12,
  },
  {
    id: 'dnd5e',
    name: 'Dungeons & Dragons 5e',
    description: 'Fantasy tabletop role-playing game',
    category: 'RPG',
    rule_count: 150,
  },
];

describe('Game Selection', () => {
  beforeEach(() => {
    // Reset the mock store before each test
    (useGameStore as jest.Mock).mockReturnValue({
      selectedGame: null,
      availableGames: [],
      isLoading: false,
      selectGame: jest.fn(),
      clearSelection: jest.fn(),
      setGames: jest.fn(),
      setLoading: jest.fn(),
    });

    // Mock successful games API response
    server.use(
      rest.get('/api/games', (req, res, ctx) => {
        return res(ctx.json({ games: mockGames }));
      })
    );
  });

  describe('GameSelector', () => {
    test('renders game selector with title', () => {
      render(<GameSelector />);
      
      expect(screen.getByText('Select a Game')).toBeInTheDocument();
    });

    test('displays loading skeleton while fetching games', () => {
      (useGameStore as jest.Mock).mockReturnValue({
        selectedGame: null,
        availableGames: [],
        isLoading: true,
        selectGame: jest.fn(),
        clearSelection: jest.fn(),
        setGames: jest.fn(),
        setLoading: jest.fn(),
      });

      render(<GameSelector />);
      
      // Should show loading skeletons
      expect(screen.getAllByTestId('game-skeleton')).toHaveLength(6);
    });

    test('displays available games after loading', async () => {
      render(<GameSelector />);
      
      await waitFor(() => {
        expect(screen.getByText('Chess')).toBeInTheDocument();
        expect(screen.getByText('Monopoly')).toBeInTheDocument();
        expect(screen.getByText('Dungeons & Dragons 5e')).toBeInTheDocument();
      });
    });

    test('shows game descriptions and categories', async () => {
      render(<GameSelector />);
      
      await waitFor(() => {
        expect(screen.getByText('Classic strategy board game')).toBeInTheDocument();
        expect(screen.getByText('Strategy')).toBeInTheDocument();
        expect(screen.getByText('Economic')).toBeInTheDocument();
        expect(screen.getByText('RPG')).toBeInTheDocument();
      });
    });

    test('calls selectGame when a game is clicked', async () => {
      const mockSelectGame = jest.fn();
      (useGameStore as jest.Mock).mockReturnValue({
        selectedGame: null,
        availableGames: mockGames,
        isLoading: false,
        selectGame: mockSelectGame,
        clearSelection: jest.fn(),
        setGames: jest.fn(),
        setLoading: jest.fn(),
      });

      render(<GameSelector />);
      
      await waitFor(() => {
        const chessGame = screen.getByText('Chess');
        fireEvent.click(chessGame);
        
        expect(mockSelectGame).toHaveBeenCalledWith(
          expect.objectContaining({
            id: 'chess',
            name: 'Chess',
          })
        );
      });
    });

    test('highlights selected game', () => {
      (useGameStore as jest.Mock).mockReturnValue({
        selectedGame: mockGames[0], // Chess is selected
        availableGames: mockGames,
        isLoading: false,
        selectGame: jest.fn(),
        clearSelection: jest.fn(),
        setGames: jest.fn(),
        setLoading: jest.fn(),
      });

      render(<GameSelector />);
      
      expect(screen.getByText('Currently Selected:')).toBeInTheDocument();
      expect(screen.getByText('Chess')).toBeInTheDocument();
      
      // The selected game card should have different styling
      const selectedButton = screen.getByRole('button', { name: /selected/i });
      expect(selectedButton).toBeInTheDocument();
    });

    test('handles API error gracefully', async () => {
      // Mock API error
      server.use(
        rest.get('/api/games', (req, res, ctx) => {
          return res(ctx.status(500), ctx.json({ error: 'Server error' }));
        })
      );

      render(<GameSelector />);
      
      await waitFor(() => {
        expect(screen.getByText(/failed to load games/i)).toBeInTheDocument();
      });
    });

    test('shows empty state when no games available', async () => {
      // Mock empty games response
      server.use(
        rest.get('/api/games', (req, res, ctx) => {
          return res(ctx.json({ games: [] }));
        })
      );

      render(<GameSelector />);
      
      await waitFor(() => {
        expect(screen.getByText(/no games available/i)).toBeInTheDocument();
      });
    });

    test('filters games by category', async () => {
      render(<GameSelector />);
      
      await waitFor(() => {
        // Wait for games to load
        expect(screen.getByText('Chess')).toBeInTheDocument();
      });

      // Click on Strategy category filter
      const strategyFilter = screen.getByRole('button', { name: /strategy/i });
      fireEvent.click(strategyFilter);
      
      // Should only show strategy games
      expect(screen.getByText('Chess')).toBeInTheDocument();
      expect(screen.queryByText('Monopoly')).not.toBeInTheDocument();
    });
  });
});