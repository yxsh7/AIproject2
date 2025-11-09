/**
 * API client for DevMetrics AI backend
 */

import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor (for adding auth tokens)
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor (for handling errors)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API Methods

export const authAPI = {
  login: (email: string, password: string) =>
    api.post('/api/auth/login', { email, password }),
  register: (data: any) => api.post('/api/auth/register', data),
  me: () => api.get('/api/auth/me'),
};

export const developersAPI = {
  list: () => api.get('/api/developers'),
  get: (id: number) => api.get(`/api/developers/${id}`),
  create: (data: any) => api.post('/api/developers', data),
  update: (id: number, data: any) => api.patch(`/api/developers/${id}`, data),
};

export const analyticsAPI = {
  team: () => api.get('/api/analytics/team'),
  developer: (id: number) => api.get(`/api/analytics/developer/${id}`),
  timeline: (id: number, start: string, end: string) =>
    api.get(`/api/analytics/developer/${id}/timeline`, {
      params: { start, end },
    }),
};

export const integrationsAPI = {
  list: () => api.get('/api/integrations'),
  configureGitHub: (data: any) => api.post('/api/integrations/github', data),
  configureJira: (data: any) => api.post('/api/integrations/jira', data),
  sync: (id: number) => api.post(`/api/integrations/${id}/sync`),
};

export const insightsAPI = {
  team: () => api.get('/api/insights/team'),
  developer: (id: number) => api.get(`/api/insights/developer/${id}`),
  acknowledge: (id: number) => api.post(`/api/insights/${id}/acknowledge`),
};

export default api;
