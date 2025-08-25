import { render, screen } from '../test-utils';
import { ChatInterface } from '../components/chat/ChatInterface';
import { useGameStore } from '../stores/gameStore';
import { useAuthStore } from '../stores/authStore';

describe('ChatInterface Basic Tests', () => {
  beforeEach(() => {
    // Set up basic auth state
    useAuthStore.getState().login('test-token');
  });

  afterEach(() => {
    // Clear stores after each test
    useGameStore.getState().clearSelection();
    useAuthStore.getState().logout();
  });

  test('shows game selection message when no game selected', () => {
    render(<ChatInterface />);
    
    expect(screen.getByText(/please select a game to start asking questions/i)).toBeInTheDocument();
  });

  test('renders chat interface when game is selected', () => {
    // Select a game first
    useGameStore.getState().selectGame({
      game_id: 'chess',
      name: 'Chess',
      description: 'Classic chess game',
      complexity: 'medium',
      rule_count: 10,
    });

    render(<ChatInterface />);
    
    expect(screen.getByText('Chess - Rules Chat')).toBeInTheDocument();
    expect(screen.getByText('Ask questions about the game rules')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Ask a question about the rules...')).toBeInTheDocument();
  });

  test('renders message input and send button', () => {
    useGameStore.getState().selectGame({
      game_id: 'chess',
      name: 'Chess',
      description: 'Classic chess game',
      complexity: 'medium',
      rule_count: 10,
    });

    render(<ChatInterface />);
    
    const input = screen.getByPlaceholderText('Ask a question about the rules...');
    const sendButton = screen.getByRole('button', { name: /send/i });
    
    expect(input).toBeInTheDocument();
    expect(sendButton).toBeInTheDocument();
    expect(sendButton).toBeDisabled(); // Should be disabled when input is empty
  });

  test('renders empty conversation state', () => {
    useGameStore.getState().selectGame({
      game_id: 'chess',
      name: 'Chess',
      description: 'Classic chess game',
      complexity: 'medium',
      rule_count: 10,
    });

    render(<ChatInterface />);
    
    expect(screen.getByText(/start a conversation by asking a question/i)).toBeInTheDocument();
  });
});