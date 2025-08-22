import { render, screen, fireEvent, waitFor } from '../test-utils';
import { GameSelector } from '../components/games/GameSelector';

describe('Game Selection', () => {
  describe('GameSelector', () => {
    test('renders game selector with title', () => {
      render(<GameSelector />);
      
      expect(screen.getByText('Select a Game')).toBeInTheDocument();
    });

    test('displays available games after loading', async () => {
      render(<GameSelector />);
      
      await waitFor(() => {
        expect(screen.getByText('Chess')).toBeInTheDocument();
        expect(screen.getByText('Monopoly')).toBeInTheDocument();
      });
    });

    test('shows game descriptions and categories', async () => {
      render(<GameSelector />);
      
      await waitFor(() => {
        expect(screen.getByText('Classic strategy board game')).toBeInTheDocument();
        // Use getAllByText for elements that appear multiple times
        expect(screen.getAllByText('Strategy').length).toBeGreaterThanOrEqual(1);
        expect(screen.getAllByText('Economic').length).toBeGreaterThanOrEqual(1);
      });
    });

    test('selects game when clicked', async () => {
      render(<GameSelector />);
      
      // Wait for games to load
      await waitFor(() => {
        expect(screen.getByText('Chess')).toBeInTheDocument();
      });

      // Click on the Chess game card
      const chessCards = screen.getAllByText('Chess');
      const chessCard = chessCards[0].closest('div');
      fireEvent.click(chessCard!);
      
      // Should show selected state
      await waitFor(() => {
        expect(screen.getByText('Currently Selected:')).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /selected/i })).toBeInTheDocument();
      });
    });

    test('handles API error gracefully', async () => {
      // Mock fetch to return error for this test
      (global.fetch as jest.Mock).mockImplementationOnce(() => {
        return Promise.resolve({
          ok: false,
          status: 500,
          json: () => Promise.resolve({ error: 'Server error' }),
        });
      });

      render(<GameSelector />);
      
      await waitFor(() => {
        expect(screen.getByText(/failed to load games/i)).toBeInTheDocument();
      });
    });

    test('shows empty state when no games available', async () => {
      // Mock fetch to return empty games array for this test
      (global.fetch as jest.Mock).mockImplementationOnce(() => {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: () => Promise.resolve({ games: [] }),
        });
      });

      render(<GameSelector />);
      
      await waitFor(() => {
        expect(screen.getByText(/no games available/i)).toBeInTheDocument();
      });
    });

    test('filters games by category', async () => {
      render(<GameSelector />);
      
      // Wait for games to load
      await waitFor(() => {
        expect(screen.getAllByText('Chess').length).toBeGreaterThanOrEqual(1);
      });

      // Click on Strategy category filter
      const buttons = screen.getAllByRole('button');
      const strategyButton = buttons.find(button => button.textContent === 'Strategy');
      fireEvent.click(strategyButton!);
      
      // Should only show strategy games
      expect(screen.getAllByText('Chess').length).toBeGreaterThanOrEqual(1);
      expect(screen.queryByText('Monopoly')).not.toBeInTheDocument();
    });
  });
});