import { create } from 'zustand';
import { persist, devtools } from 'zustand/middleware';

interface User {
  id: string;
  email: string;
  username: string;
  preferences: {
    selectedGameId?: string;
    theme: 'light' | 'dark';
  };
}

interface AuthStore {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (token: string) => void;
  logout: () => void;
  updateUserPreferences: (preferences: Partial<User['preferences']>) => void;
  setLoading: (loading: boolean) => void;
}

export const useAuthStore = create<AuthStore>()(
  devtools(
    persist(
      (set, get) => ({
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        
        login: (token: string) => {
          try {
            // For now, we'll create a mock user - later we'll decode JWT
            const mockUser: User = {
              id: '1',
              username: 'testuser',
              email: 'test@example.com',
              preferences: {
                selectedGameId: undefined,
                theme: 'light',
              },
            };
            
            set({
              user: mockUser,
              token,
              isAuthenticated: true,
              isLoading: false,
            });
          } catch (error) {
            console.error('Login failed:', error);
            get().logout();
          }
        },
        
        logout: () => {
          set({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
          });
        },
        
        updateUserPreferences: (preferences) => {
          const user = get().user;
          if (user) {
            set({
              user: {
                ...user,
                preferences: { ...user.preferences, ...preferences }
              }
            });
          }
        },
        
        setLoading: (loading: boolean) => {
          set({ isLoading: loading });
        },
      }),
      {
        name: 'auth-storage',
        partialize: (state) => ({
          token: state.token,
          user: state.user,
          isAuthenticated: state.isAuthenticated,
        }),
      }
    ),
    { name: 'auth-store' }
  )
);