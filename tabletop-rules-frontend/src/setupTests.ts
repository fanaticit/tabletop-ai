// jest-dom adds custom jest matchers for asserting on DOM nodes.
import '@testing-library/jest-dom';

// Polyfills for Node.js environment
import { TextEncoder, TextDecoder } from 'util';

// Add TextEncoder/TextDecoder to global scope for MSW
Object.assign(global, { TextDecoder, TextEncoder });

// Mock fetch if not available
import 'whatwg-fetch';

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
    addListener: jest.fn(), // deprecated
    removeListener: jest.fn(), // deprecated
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

// Now we can safely import MSW after polyfills are set up
import { setupServer } from 'msw/node';
import { rest } from 'msw';

// Setup MSW server
export const server = setupServer(
  // Default handlers
  rest.get('/api/games', (req, res, ctx) => {
    return res(ctx.json({ 
      games: [
        {
          id: 'chess',
          name: 'Chess',
          description: 'Classic strategy board game',
          category: 'Strategy',
          rule_count: 5,
        }
      ] 
    }));
  }),
  
  rest.post('/api/auth/login', (req, res, ctx) => {
    return res(ctx.json({ 
      access_token: 'mock-token', 
      token_type: 'bearer',
      user: { id: '1', username: 'testuser', email: 'test@example.com' }
    }));
  }),

  rest.post('/api/auth/register', (req, res, ctx) => {
    return res(ctx.json({ 
      message: 'Registration successful',
      user: { id: '2', username: 'newuser', email: 'new@example.com' }
    }));
  })
);

// Start server before all tests
beforeAll(() => server.listen({ onUnhandledRequest: 'bypass' }));

// Reset handlers after each test
afterEach(() => server.resetHandlers());

// Clean up after all tests
afterAll(() => server.close());