import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { LoginForm } from './components/auth/LoginForm';
import { RegistrationForm } from './components/auth/RegistrationForm';
import { GameSelector } from './components/games/GameSelector';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes (was cacheTime)
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="App">
          <Routes>
            <Route path="/login" element={<LoginForm />} />
            <Route path="/register" element={<RegistrationForm />} />
            <Route path="/games" element={<GameSelector />} />
            <Route path="/" element={
              <div style={{ padding: '2rem', textAlign: 'center' }}>
                <h1>Tabletop Rules Assistant</h1>
                <p>Frontend is ready! Navigate to:</p>
                <ul style={{ listStyle: 'none', padding: 0 }}>
                  <li><a href="/login">Login</a></li>
                  <li><a href="/register">Register</a></li>
                  <li><a href="/games">Browse Games</a></li>
                </ul>
              </div>
            } />
          </Routes>
        </div>
      </Router>
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}

export default App;