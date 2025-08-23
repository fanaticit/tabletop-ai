import { render, screen, fireEvent, waitFor } from '../test-utils';
import userEvent from '@testing-library/user-event';
import { MessageInput } from '../components/chat/MessageInput';

describe('MessageInput', () => {
  const mockOnSendMessage = jest.fn();

  const defaultProps = {
    onSendMessage: mockOnSendMessage,
    isLoading: false,
  };

  beforeEach(() => {
    mockOnSendMessage.mockClear();
  });

  test('renders textarea with default placeholder', () => {
    render(<MessageInput {...defaultProps} />);
    
    const textarea = screen.getByPlaceholderText('Ask a question about the rules...');
    expect(textarea).toBeInTheDocument();
    expect(textarea).toBeInstanceOf(HTMLTextAreaElement);
  });

  test('renders with custom placeholder', () => {
    render(<MessageInput {...defaultProps} placeholder="Custom placeholder" />);
    
    const textarea = screen.getByPlaceholderText('Custom placeholder');
    expect(textarea).toBeInTheDocument();
  });

  test('renders send button', () => {
    render(<MessageInput {...defaultProps} />);
    
    const sendButton = screen.getByRole('button', { name: /send/i });
    expect(sendButton).toBeInTheDocument();
  });

  test('allows typing in textarea', async () => {
    const user = userEvent.setup();
    render(<MessageInput {...defaultProps} />);
    
    const textarea = screen.getByPlaceholderText('Ask a question about the rules...');
    
    await user.type(textarea, 'How do I move a pawn?');
    
    expect(textarea).toHaveValue('How do I move a pawn?');
  });

  test('calls onSendMessage when form is submitted with text', async () => {
    const user = userEvent.setup();
    render(<MessageInput {...defaultProps} />);
    
    const textarea = screen.getByPlaceholderText('Ask a question about the rules...');
    const sendButton = screen.getByRole('button', { name: /send/i });
    
    await user.type(textarea, 'Test message');
    await user.click(sendButton);
    
    expect(mockOnSendMessage).toHaveBeenCalledWith('Test message');
    expect(textarea).toHaveValue(''); // Should clear after sending
  });

  test('calls onSendMessage when Enter is pressed', async () => {
    const user = userEvent.setup();
    render(<MessageInput {...defaultProps} />);
    
    const textarea = screen.getByPlaceholderText('Ask a question about the rules...');
    
    await user.type(textarea, 'Test message{Enter}');
    
    expect(mockOnSendMessage).toHaveBeenCalledWith('Test message');
    expect(textarea).toHaveValue('');
  });

  test('does not submit when Shift+Enter is pressed', async () => {
    const user = userEvent.setup();
    render(<MessageInput {...defaultProps} />);
    
    const textarea = screen.getByPlaceholderText('Ask a question about the rules...');
    
    await user.type(textarea, 'Test message');
    
    // Simulate keydown event manually to test the handler
    fireEvent.keyDown(textarea, { 
      key: 'Enter', 
      shiftKey: true, 
      preventDefault: jest.fn() 
    });
    
    expect(mockOnSendMessage).not.toHaveBeenCalled();
    expect(textarea).toHaveValue('Test message'); // Should keep the text
  });

  test('trims whitespace from message', async () => {
    const user = userEvent.setup();
    render(<MessageInput {...defaultProps} />);
    
    const textarea = screen.getByPlaceholderText('Ask a question about the rules...');
    const sendButton = screen.getByRole('button', { name: /send/i });
    
    await user.type(textarea, '   Test message   ');
    await user.click(sendButton);
    
    expect(mockOnSendMessage).toHaveBeenCalledWith('Test message');
  });

  test('does not submit empty or whitespace-only messages', async () => {
    const user = userEvent.setup();
    render(<MessageInput {...defaultProps} />);
    
    const textarea = screen.getByPlaceholderText('Ask a question about the rules...');
    const sendButton = screen.getByRole('button', { name: /send/i });
    
    // Test empty message
    await user.click(sendButton);
    expect(mockOnSendMessage).not.toHaveBeenCalled();
    
    // Test whitespace-only message
    await user.type(textarea, '   ');
    await user.click(sendButton);
    expect(mockOnSendMessage).not.toHaveBeenCalled();
  });

  test('disables form when isLoading is true', () => {
    render(<MessageInput {...defaultProps} isLoading={true} />);
    
    const textarea = screen.getByPlaceholderText('Ask a question about the rules...');
    const sendButton = screen.getByRole('button', { name: /sending/i });
    
    expect(textarea).toBeDisabled();
    expect(sendButton).toBeDisabled();
    expect(sendButton).toHaveTextContent('Sending...');
  });

  test('disables form when disabled prop is true', () => {
    render(<MessageInput {...defaultProps} disabled={true} />);
    
    const textarea = screen.getByPlaceholderText('Ask a question about the rules...');
    const sendButton = screen.getByRole('button', { name: /send/i });
    
    expect(textarea).toBeDisabled();
    expect(sendButton).toBeDisabled();
  });

  test('does not submit when disabled', async () => {
    const user = userEvent.setup();
    render(<MessageInput {...defaultProps} disabled={true} />);
    
    const textarea = screen.getByPlaceholderText('Ask a question about the rules...');
    const sendButton = screen.getByRole('button', { name: /send/i });
    
    // Try to type (should not work when disabled)
    await user.type(textarea, 'Test message');
    await user.click(sendButton);
    
    expect(mockOnSendMessage).not.toHaveBeenCalled();
  });

  test('does not submit when loading', async () => {
    const user = userEvent.setup();
    render(<MessageInput {...defaultProps} isLoading={true} />);
    
    const textarea = screen.getByPlaceholderText('Ask a question about the rules...');
    const sendButton = screen.getByRole('button', { name: /sending/i });
    
    await user.type(textarea, 'Test message');
    await user.click(sendButton);
    
    expect(mockOnSendMessage).not.toHaveBeenCalled();
  });

  test('send button is disabled when input is empty', () => {
    render(<MessageInput {...defaultProps} />);
    
    const sendButton = screen.getByRole('button', { name: /send/i });
    expect(sendButton).toBeDisabled();
  });

  test('send button is enabled when input has text', async () => {
    const user = userEvent.setup();
    render(<MessageInput {...defaultProps} />);
    
    const textarea = screen.getByPlaceholderText('Ask a question about the rules...');
    const sendButton = screen.getByRole('button', { name: /send/i });
    
    expect(sendButton).toBeDisabled();
    
    await user.type(textarea, 'Test message');
    expect(sendButton).not.toBeDisabled();
  });

  test('form submission works correctly', async () => {
    const user = userEvent.setup();
    render(<MessageInput {...defaultProps} />);
    
    const textarea = screen.getByPlaceholderText('Ask a question about the rules...');
    const sendButton = screen.getByRole('button', { name: /send/i });
    
    await user.type(textarea, 'Test message');
    await user.click(sendButton);
    
    expect(mockOnSendMessage).toHaveBeenCalledWith('Test message');
    expect(textarea).toHaveValue(''); // Should clear after sending
  });
});