import React, { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { ChakraProvider } from '@chakra-ui/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';

// Create a test query client with no retries for faster tests
const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
      cacheTime: 0,
      staleTime: 0,
    },
    mutations: {
      retry: false,
    },
  },
  logger: {
    log: () => {},
    warn: () => {},
    error: () => {},
  },
});

// All the providers wrapper
const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
  const queryClient = createTestQueryClient();
  
  return (
    <BrowserRouter>
      <ChakraProvider>
        <QueryClientProvider client={queryClient}>
          {children}
        </QueryClientProvider>
      </ChakraProvider>
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