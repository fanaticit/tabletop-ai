import { act, renderHook } from '@testing-library/react';
import { useConversationStore } from '../stores/conversationStore';

describe('ConversationStore', () => {
  beforeEach(() => {
    // Clear store state before each test
    useConversationStore.getState().clearConversation();
    useConversationStore.getState().setCurrentGame(null);
    
    // Set UUID mock return value (already mocked globally in setupTests.ts)
    (global.crypto.randomUUID as jest.Mock).mockReturnValue('test-message-id');
  });

  test('should initialize with empty state', () => {
    const { result } = renderHook(() => useConversationStore());
    
    expect(result.current.messages).toEqual([]);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.currentGameId).toBe(null);
  });

  test('should add messages with generated ID and timestamp', () => {
    const { result } = renderHook(() => useConversationStore());
    const mockDate = new Date('2023-01-01T00:00:00Z');
    jest.spyOn(global, 'Date').mockImplementation(() => mockDate as any);

    act(() => {
      result.current.addMessage({
        role: 'user',
        content: 'Test message',
        gameId: 'chess',
      });
    });

    expect(result.current.messages).toHaveLength(1);
    expect(result.current.messages[0]).toEqual({
      id: 'test-message-id',
      role: 'user',
      content: 'Test message',
      gameId: 'chess',
      timestamp: mockDate,
    });

    (global.Date as any).mockRestore();
  });

  test('should add assistant message with sources', () => {
    const { result } = renderHook(() => useConversationStore());
    const mockSources = [
      {
        game_id: 'chess',
        category_id: 'movement',
        title: 'Pawn Movement',
        content: 'Pawns move forward...',
      }
    ];

    act(() => {
      result.current.addMessage({
        role: 'assistant',
        content: 'Here are the rules for pawn movement',
        gameId: 'chess',
        sources: mockSources,
      });
    });

    expect(result.current.messages).toHaveLength(1);
    expect(result.current.messages[0].sources).toEqual(mockSources);
    expect(result.current.messages[0].role).toBe('assistant');
  });

  test('should set loading state', () => {
    const { result } = renderHook(() => useConversationStore());

    act(() => {
      result.current.setLoading(true);
    });

    expect(result.current.isLoading).toBe(true);

    act(() => {
      result.current.setLoading(false);
    });

    expect(result.current.isLoading).toBe(false);
  });

  test('should set current game', () => {
    const { result } = renderHook(() => useConversationStore());

    act(() => {
      result.current.setCurrentGame('chess');
    });

    expect(result.current.currentGameId).toBe('chess');

    act(() => {
      result.current.setCurrentGame(null);
    });

    expect(result.current.currentGameId).toBe(null);
  });

  test('should clear conversation', () => {
    const { result } = renderHook(() => useConversationStore());

    // Add some messages first
    act(() => {
      result.current.addMessage({
        role: 'user',
        content: 'Test message 1',
        gameId: 'chess',
      });
      result.current.addMessage({
        role: 'assistant',
        content: 'Test response 1',
        gameId: 'chess',
      });
      result.current.setLoading(true);
    });

    expect(result.current.messages).toHaveLength(2);
    expect(result.current.isLoading).toBe(true);

    act(() => {
      result.current.clearConversation();
    });

    expect(result.current.messages).toEqual([]);
    expect(result.current.isLoading).toBe(false);
  });

  test('should filter messages for specific game', () => {
    const { result } = renderHook(() => useConversationStore());

    // Add messages for different games
    act(() => {
      result.current.addMessage({
        role: 'user',
        content: 'Chess question',
        gameId: 'chess',
      });
      result.current.addMessage({
        role: 'user',
        content: 'Monopoly question',
        gameId: 'monopoly',
      });
      result.current.addMessage({
        role: 'user',
        content: 'Another chess question',
        gameId: 'chess',
      });
    });

    const chessMessages = result.current.getMessagesForGame('chess');
    const monopolyMessages = result.current.getMessagesForGame('monopoly');

    expect(chessMessages).toHaveLength(2);
    expect(monopolyMessages).toHaveLength(1);
    expect(chessMessages[0].content).toBe('Chess question');
    expect(chessMessages[1].content).toBe('Another chess question');
    expect(monopolyMessages[0].content).toBe('Monopoly question');
  });

  test('should return empty array for game with no messages', () => {
    const { result } = renderHook(() => useConversationStore());

    const messages = result.current.getMessagesForGame('nonexistent-game');
    expect(messages).toEqual([]);
  });
});