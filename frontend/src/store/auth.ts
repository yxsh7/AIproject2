/**
 * Authentication store using Zustand
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User, LoginCredentials, RegisterData } from '@/types';
import { authAPI } from '@/lib/api';

/** FastAPI validation errors return `detail` as an array of {msg, loc, ...}
 * objects rather than a string — rendering that directly as JSX text crashes
 * React ("Objects are not valid as a React child"), so always coerce to string. */
function extractErrorMessage(error: any, fallback: string): string {
  const detail = error?.response?.data?.detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    return detail.map((d: any) => d?.msg || JSON.stringify(d)).join('; ');
  }
  return fallback;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  error: string | null;
  // True until the initial auth check (rehydrate persisted token, then
  // fetchUser if one exists) has resolved. Page guards must wait for this to
  // go false before deciding whether to redirect to /login — otherwise a
  // valid session gets bounced because `user` is still null on the very
  // first render, before the async fetch has had a chance to complete.
  isInitializing: boolean;

  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  fetchUser: () => Promise<void>;
  clearError: () => void;
  setInitializing: (value: boolean) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isLoading: false,
      error: null,
      isInitializing: true,

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
          set({ error: extractErrorMessage(error, 'Login failed'), isLoading: false });
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
          set({ error: extractErrorMessage(error, 'Registration failed'), isLoading: false });
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
          // 401 = invalid/expired token, 403 = valid token but access denied
          // (e.g. organization suspended) — either way the token is now
          // useless, so drop it rather than leaving it stuck in storage.
          if (error.response?.status === 401 || error.response?.status === 403) {
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
      setInitializing: (value) => set({ isInitializing: value }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ token: state.token }),
      // Only `token` is persisted — `user` starts null on every fresh page
      // load/hard refresh until something re-fetches it. Without this, a
      // valid session gets bounced to /login because every dashboard page's
      // guard checks `user`, not `token`. fetchUser() already handles an
      // invalid/expired token by logging out.
      onRehydrateStorage: () => (state, error) => {
        if (error || !state?.token) {
          state?.setInitializing?.(false);
          return;
        }
        state.fetchUser().catch(() => {}).finally(() => state.setInitializing(false));
      },
    }
  )
);
