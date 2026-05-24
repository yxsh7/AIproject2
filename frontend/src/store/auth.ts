/**
 * Authentication store using Zustand
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User, LoginCredentials, RegisterData } from '@/types';
import { authAPI } from '@/lib/api';

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  error: string | null;

  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  fetchUser: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isLoading: false,
      error: null,

      login: async (credentials) => {
        try {
          set({ isLoading: true, error: null });

          const response = await authAPI.login(credentials.email, credentials.password);
          const { access_token } = response.data;

          // Store token
          localStorage.setItem('token', access_token);
          set({ token: access_token });

          // Fetch user data
          await get().fetchUser();
        } catch (error: any) {
          const message = error.response?.data?.detail || 'Login failed';
          set({ error: message, isLoading: false });
          throw error;
        }
      },

      register: async (data) => {
        try {
          set({ isLoading: true, error: null });

          await authAPI.register(data);

          // Auto-login after registration
          await get().login({
            email: data.email,
            password: data.password,
          });
        } catch (error: any) {
          const message = error.response?.data?.detail || 'Registration failed';
          set({ error: message, isLoading: false });
          throw error;
        }
      },

      fetchUser: async () => {
        try {
          set({ isLoading: true });

          const response = await authAPI.me();
          set({ user: response.data, isLoading: false });
        } catch (error: any) {
          set({ error: 'Failed to fetch user data', isLoading: false });
          // If token is invalid, logout
          if (error.response?.status === 401) {
            get().logout();
          }
          throw error;
        }
      },

      logout: () => {
        localStorage.removeItem('token');
        set({ user: null, token: null, error: null });
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ token: state.token }),
    }
  )
);
