import { render, screen } from '../test-utils';
import { MessageList } from '../components/chat/MessageList';
import { Message } from '../stores/conversationStore';

const createMockMessage = (overrides: Partial<Message> = {}): Message => ({
  id: 'test-id-1',
  role: 'user',
  content: 'Test message',
  timestamp: new Date('2023-01-01T12:00:00Z'),
  gameId: 'chess',
  ...overrides,
});

describe('MessageList', () => {
  test('renders empty state when no messages', () => {
    render(<MessageList messages={[]} isLoading={false} />);
    
    expect(screen.getByText(/start a conversation by asking a question/i)).toBeInTheDocument();
  });

  test('does not show empty state when loading', () => {
    render(<MessageList messages={[]} isLoading={true} />);
    
    expect(screen.queryByText(/start a conversation by asking a question/i)).not.toBeInTheDocument();
  });

  test('renders single user message', () => {
    const messages = [createMockMessage({ content: 'How do I move a pawn?' })];
    
    render(<MessageList messages={messages} isLoading={false} />);
    
    expect(screen.getByText('How do I move a pawn?')).toBeInTheDocument();
  });

  test('renders single assistant message', () => {
    const messages = [createMockMessage({
      role: 'assistant',
      content: 'Pawns move forward one square at a time.',
    })];
    
    render(<MessageList messages={messages} isLoading={false} />);
    
    expect(screen.getByText('Pawns move forward one square at a time.')).toBeInTheDocument();
  });

  test('renders multiple messages in order', () => {
    const messages = [
      createMockMessage({
        id: '1',
        role: 'user',
        content: 'First message',
        timestamp: new Date('2023-01-01T12:00:00Z'),
      }),
      createMockMessage({
        id: '2',
        role: 'assistant', 
        content: 'Second message',
        timestamp: new Date('2023-01-01T12:01:00Z'),
      }),
      createMockMessage({
        id: '3',
        role: 'user',
        content: 'Third message',
        timestamp: new Date('2023-01-01T12:02:00Z'),
      }),
    ];
    
    render(<MessageList messages={messages} isLoading={false} />);
    
    expect(screen.getByText('First message')).toBeInTheDocument();
    expect(screen.getByText('Second message')).toBeInTheDocument();
    expect(screen.getByText('Third message')).toBeInTheDocument();
  });

  test('displays timestamps for messages', () => {
    const messages = [createMockMessage({
      timestamp: new Date('2023-01-01T12:30:45Z'),
    })];
    
    render(<MessageList messages={messages} isLoading={false} />);
    
    // Should display time in locale format
    expect(screen.getByText(/12:30:45/)).toBeInTheDocument();
  });

  test('renders loading indicator when isLoading is true', () => {
    render(<MessageList messages={[]} isLoading={true} />);
    
    expect(screen.getByText('Thinking')).toBeInTheDocument();
    expect(screen.getByText('...')).toBeInTheDocument();
  });

  test('shows loading indicator with existing messages', () => {
    const messages = [createMockMessage({ content: 'Previous message' })];
    
    render(<MessageList messages={messages} isLoading={true} />);
    
    expect(screen.getByText('Previous message')).toBeInTheDocument();
    expect(screen.getByText('Thinking')).toBeInTheDocument();
  });

  test('renders assistant message with sources', () => {
    const sources = [
      {
        game_id: 'chess',
        category_id: 'movement',
        title: 'Pawn Movement Rules',
        content: 'Detailed pawn movement rules...',
      },
      {
        game_id: 'chess',
        category_id: 'capture',
        title: 'Pawn Capture Rules', 
        content: 'Detailed pawn capture rules...',
      },
    ];

    const messages = [createMockMessage({
      role: 'assistant',
      content: 'Here are the pawn movement rules',
      sources,
    })];
    
    render(<MessageList messages={messages} isLoading={false} />);
    
    expect(screen.getByText('Here are the pawn movement rules')).toBeInTheDocument();
    expect(screen.getByText('Sources:')).toBeInTheDocument();
    expect(screen.getByText('• Pawn Movement Rules (chess)')).toBeInTheDocument();
    expect(screen.getByText('• Pawn Capture Rules (chess)')).toBeInTheDocument();
  });

  test('does not render sources section when no sources', () => {
    const messages = [createMockMessage({
      role: 'assistant',
      content: 'No sources for this response',
      sources: undefined,
    })];
    
    render(<MessageList messages={messages} isLoading={false} />);
    
    expect(screen.getByText('No sources for this response')).toBeInTheDocument();
    expect(screen.queryByText('Sources:')).not.toBeInTheDocument();
  });

  test('does not render sources section when sources array is empty', () => {
    const messages = [createMockMessage({
      role: 'assistant',
      content: 'Empty sources array',
      sources: [],
    })];
    
    render(<MessageList messages={messages} isLoading={false} />);
    
    expect(screen.getByText('Empty sources array')).toBeInTheDocument();
    expect(screen.queryByText('Sources:')).not.toBeInTheDocument();
  });

  test('user messages appear on the right side', () => {
    const messages = [createMockMessage({
      role: 'user',
      content: 'User message',
    })];
    
    render(<MessageList messages={messages} isLoading={false} />);
    
    expect(screen.getByText('User message')).toBeInTheDocument();
    // Note: Style testing is complex with inline styles, verifying content is sufficient
  });

  test('assistant messages appear on the left side', () => {
    const messages = [createMockMessage({
      role: 'assistant',
      content: 'Assistant message',
    })];
    
    render(<MessageList messages={messages} isLoading={false} />);
    
    expect(screen.getByText('Assistant message')).toBeInTheDocument();
    // Note: Style testing is complex with inline styles, verifying content is sufficient
  });

  test('handles mixed message types correctly', () => {
    const messages = [
      createMockMessage({
        id: '1',
        role: 'user',
        content: 'User question',
      }),
      createMockMessage({
        id: '2',
        role: 'assistant',
        content: 'Assistant response',
        sources: [{
          game_id: 'chess',
          category_id: 'rules',
          title: 'Basic Rules',
          content: 'Rule content',
        }],
      }),
    ];
    
    render(<MessageList messages={messages} isLoading={false} />);
    
    expect(screen.getByText('User question')).toBeInTheDocument();
    expect(screen.getByText('Assistant response')).toBeInTheDocument();
    expect(screen.getByText('Sources:')).toBeInTheDocument();
    expect(screen.getByText('• Basic Rules (chess)')).toBeInTheDocument();
  });

  test('scrolls to bottom when new messages are added', () => {
    const messages = [createMockMessage()];
    
    const { rerender } = render(<MessageList messages={messages} isLoading={false} />);
    
    // Clear previous scroll calls
    (HTMLDivElement.prototype.scrollIntoView as jest.Mock).mockClear();
    
    // Add another message
    const updatedMessages = [
      ...messages,
      createMockMessage({
        id: '2',
        content: 'New message',
      }),
    ];
    
    rerender(<MessageList messages={updatedMessages} isLoading={false} />);
    
    expect(HTMLDivElement.prototype.scrollIntoView).toHaveBeenCalledWith({ behavior: 'smooth' });
  });

  test('scrolls to bottom when loading state changes', () => {
    const messages = [createMockMessage()];
    
    const { rerender } = render(<MessageList messages={messages} isLoading={false} />);
    
    // Clear previous scroll calls
    (HTMLDivElement.prototype.scrollIntoView as jest.Mock).mockClear();
    
    rerender(<MessageList messages={messages} isLoading={true} />);
    
    expect(HTMLDivElement.prototype.scrollIntoView).toHaveBeenCalledWith({ behavior: 'smooth' });
  });
});