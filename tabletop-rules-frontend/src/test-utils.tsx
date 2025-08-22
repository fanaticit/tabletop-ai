import React, { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { act } from 'react';

// Create a test query client with no retries for faster tests
const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
      gcTime: 0, // Was cacheTime
      staleTime: 0,
    },
    mutations: {
      retry: false,
    },
  },
});

const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
  const queryClient = createTestQueryClient();
  
  return (
    <BrowserRouter future={{ 
      v7_startTransition: true,
      v7_relativeSplatPath: true 
    }}>
      <QueryClientProvider client={queryClient}>
        <div data-testid="test-wrapper">
          {children}
        </div>
      </QueryClientProvider>
    </BrowserRouter>
  );
};

// Custom render function that includes providers
const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>,
) => render(ui, { wrapper: AllTheProviders, ...options });

// Re-export everything
export * from '@testing-library/react';
export { customRender as render };
export { act };

// Mock data for tests
export const mockUser = {
  id: '1',
  username: 'testuser',
  email: 'test@example.com',
  preferences: {
    selectedGameId: 'chess',
    theme: 'light' as const,
  },
};

export const mockGame = {
  id: 'chess',
  name: 'Chess',
  description: 'Classic strategy game',
  category: 'Strategy',
  rule_count: 3,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
};

export const mockToken = 'mock-jwt-token';