import { render, screen, fireEvent, waitFor } from './test-utils';
import { rest } from 'msw';
import { server } from '../setupTests';
import { GameSelector } from '../components/games/GameSelector';

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
    // Reset server handlers before each test
    server.resetHandlers();
    
    // Set up default successful response
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
      // Delay the response to simulate loading
      server.use(
        rest.get('/api/games', (req, res, ctx) => {
          return res(ctx.delay(1000), ctx.json({ games: mockGames }));
        })
      );

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

    test('selects game when clicked', async () => {
      render(<GameSelector />);
      
      // Wait for games to load
      await waitFor(() => {
        expect(screen.getByText('Chess')).toBeInTheDocument();
      });

      // Click on the Chess game card
      const chessCard = screen.getByText('Chess').closest('div[role="button"], div');
      fireEvent.click(chessCard!);
      
      // Should show selected state
      await waitFor(() => {
        expect(screen.getByText('Currently Selected:')).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /selected/i })).toBeInTheDocument();
      });
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
      
      // Wait for games to load
      await waitFor(() => {
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