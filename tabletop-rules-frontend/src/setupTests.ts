// jest-dom adds custom jest matchers for asserting on DOM nodes.
import '@testing-library/jest-dom';

// Mock fetch for our tests
global.fetch = jest.fn();

// Mock local storage
Object.defineProperty(window, 'localStorage', {
  value: {
    getItem: jest.fn(),
    setItem: jest.fn(),
    removeItem: jest.fn(),
    clear: jest.fn(),
  },
  writable: true,
});

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(), 
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock ResizeObserver
global.ResizeObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

// Mock IntersectionObserver  
global.IntersectionObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

// Setup mock responses for our API endpoints
beforeEach(() => {
  // Reset all mocks before each test
  jest.clearAllMocks();
  
  // Setup default fetch mock responses
  (global.fetch as jest.Mock).mockImplementation((url: string, options?: any) => {
    // Mock login endpoint
    if (url.includes('/api/auth/login')) {
      if (options?.body?.includes('wronguser')) {
        return Promise.resolve({
          ok: false,
          status: 401,
          json: () => Promise.resolve({ detail: 'Invalid credentials' }),
        });
      }
      return Promise.resolve({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ 
          access_token: 'mock-token',
          token_type: 'bearer',
          user: { id: '1', username: 'testuser', email: 'test@example.com' }
        }),
      });
    }
    
    // Mock register endpoint
    if (url.includes('/api/auth/register')) {
      return Promise.resolve({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ 
          message: 'Registration successful',
          user: { id: '2', username: 'newuser', email: 'new@example.com' }
        }),
      });
    }
    
    // Mock games endpoint
    if (url.includes('/api/games')) {
      return Promise.resolve({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ 
          games: [
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
            }
          ]
        }),
      });
    }
    
    // Default response for unknown endpoints
    return Promise.resolve({
      ok: true,
      status: 200,
      json: () => Promise.resolve({}),
    });
  });
});