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
  // Developer Analytics
  getOverview: (id: number, params?: { start_date?: string; end_date?: string }) =>
    api.get(`/api/analytics/developers/${id}/overview`, { params }),
  getProductivity: (id: number, params?: { start_date?: string; end_date?: string; include_comparison?: boolean }) =>
    api.get(`/api/analytics/developers/${id}/productivity`, { params }),
  getTrends: (id: number, periods: number = 12) =>
    api.get(`/api/analytics/developers/${id}/trends`, { params: { periods } }),
  getWorkBreakdown: (id: number, params?: { start_date?: string; end_date?: string; limit?: number }) =>
    api.get(`/api/analytics/developers/${id}/work-breakdown`, { params }),
  getInsights: (id: number, params?: { start_date?: string; end_date?: string; regenerate?: boolean }) =>
    api.get(`/api/analytics/developers/${id}/insights`, { params }),

  // Team Analytics
  getTeamOverview: (team: string, params?: { start_date?: string; end_date?: string }) =>
    api.get(`/api/analytics/teams/${team}/overview`, { params }),

  // Score Calculation
  calculateScore: (data: {
    developer_id?: number;
    start_date?: string;
    end_date?: string;
    force_recalculate?: boolean;
  }) => api.post('/api/analytics/calculate-score', data),

  // Manual AI Analysis Trigger (COSTS MONEY)
  triggerAnalysis: (id: number, limit: number = 50) =>
    api.post(`/api/analytics/developers/${id}/analyze`, null, { params: { limit } }),
};

export const organizationsAPI = {
  me: () => api.get('/api/organizations/me'),
  listInvites: () => api.get('/api/organizations/invites'),
  createInvite: (data: { role: string; max_uses?: number; expires_in_days?: number }) =>
    api.post('/api/organizations/invites', data),
  revokeInvite: (id: number) => api.delete(`/api/organizations/invites/${id}`),
};

export const adminAPI = {
  listOrganizations: () => api.get('/api/admin/organizations'),
  getOrganization: (id: number) => api.get(`/api/admin/organizations/${id}`),
  updateOrganization: (id: number, data: { is_active: boolean }) =>
    api.patch(`/api/admin/organizations/${id}`, data),
  listUsers: (organizationId?: number) =>
    api.get('/api/admin/users', { params: organizationId ? { organization_id: organizationId } : undefined }),
  updateUser: (id: number, data: { is_active: boolean }) =>
    api.patch(`/api/admin/users/${id}`, data),
};

export const integrationsAPI = {
  list: () => api.get('/api/integrations'),
  configureGitHub: (data: { organization_name: string; access_token: string; repos?: string[] }) =>
    api.post('/api/integrations/github', data),
  configureJira: (data: {
    workspace_url: string;
    username: string;
    api_token: string;
    project_keys?: string[];
  }) => api.post('/api/integrations/jira', data),
  sync: (id: number, days_back: number = 30) =>
    api.post(`/api/integrations/${id}/sync`, { days_back }),
  getStatus: (id: number) => api.get(`/api/integrations/${id}/status`),
  test: (id: number) => api.post(`/api/integrations/${id}/test`),
  delete: (id: number) => api.delete(`/api/integrations/${id}`),
};

export default api;
