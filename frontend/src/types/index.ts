/**
 * TypeScript types for DevMetrics AI
 */

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: 'admin' | 'manager' | 'developer';
  is_active: boolean;
  organization_id: number;
  is_superadmin: boolean;
  created_at: string;
}

export interface Organization {
  id: number;
  name: string;
  slug: string;
  is_active: boolean;
  created_at?: string;
}

export interface OrganizationInvite {
  id: number;
  organization_id: number;
  code: string;
  role: string;
  max_uses?: number | null;
  used_count: number;
  expires_at?: string | null;
  is_active: boolean;
  created_at?: string;
}

export interface AdminOrganization {
  id: number;
  name: string;
  slug: string;
  is_active: boolean;
  user_count: number;
  developer_count: number;
  created_at?: string;
}

export interface AdminUser {
  id: number;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  is_superadmin: boolean;
  organization_id: number;
  organization_name: string;
  created_at?: string;
}

export interface DeveloperProfile {
  id: number;
  user_id: number;
  user?: User;
  role_level: 'intern' | 'junior' | 'mid' | 'senior' | 'staff' | 'principal';
  team?: string;
  github_username?: string;
  jira_username?: string;
  skills: string[];
  bio?: string;
  location?: string;
  timezone?: string;
  created_at: string;
  updated_at: string;
}

export interface ProductivityScore {
  id: number;
  developer_id: number;
  period_start: string;
  period_end: string;
  overall_score: number;
  complexity_score: number;
  velocity_score: number;
  quality_score: number;
  impact_score: number;
  collaboration_score: number;
  mentoring_score: number;
  total_commits: number;
  total_prs: number;
  total_tickets: number;
  lines_added: number;
  lines_deleted: number;
  work_breakdown: Record<string, number>;
  metadata?: Record<string, any>;
}

export interface DeveloperAnalyticsOverview {
  developer_id: number;
  developer_name: string;
  role_level: string;
  team?: string;
  period_start: string;
  period_end: string;
  productivity_score?: ProductivityScore;
  activity_summary: {
    total_activities: number;
    total_commits: number;
    total_tickets: number;
    days_active: number;
    avg_complexity: number;
    avg_impact: number;
  };
  work_breakdown: Record<string, number>;
}

export interface DeveloperProductivity {
  developer_id: number;
  developer_name: string;
  role_level: string;
  team?: string;
  period_start: string;
  period_end: string;
  overall_score: number;
  score_breakdown: {
    complexity: number;
    velocity: number;
    quality: number;
    impact: number;
    collaboration: number;
    mentoring: number;
  };
  evaluation_weights: {
    complexity: number;
    velocity: number;
    quality: number;
    impact: number;
    collaboration: number;
    mentoring: number;
  };
  work_breakdown: Record<string, number>;
  activity_stats: Record<string, any>;
  comparison_to_team?: {
    overall: {
      developer: number;
      team_average: number;
      difference: number;
    };
    [key: string]: any;
  };
  comparison_to_role?: Record<string, any>;
}

export interface TrendDataPoint {
  period_start: string;
  period_end: string;
  overall_score: number;
  complexity_score: number;
  velocity_score: number;
  quality_score: number;
  impact_score: number;
  collaboration_score: number;
  mentoring_score: number;
}

export interface DeveloperTrends {
  developer_id: number;
  developer_name: string;
  trends: TrendDataPoint[];
  trend_analysis: {
    latest_score: number;
    previous_score: number;
    change: number;
    trend_direction: 'improving' | 'declining' | 'stable';
    average_score: number;
  };
}

export interface WorkActivity {
  id: number;
  activity_date: string;
  work_type: string;
  complexity_score: number;
  impact_score: number;
  quality_score: number;
  time_estimate_hours: number;
  source_type: string;
  ai_analysis?: Record<string, any>;
  artifacts?: Array<Record<string, any>>;
}

export interface WorkBreakdown {
  developer_id: number;
  developer_name: string;
  period_start: string;
  period_end: string;
  work_type_distribution: Record<string, number>;
  complexity_distribution: {
    low: number;
    medium: number;
    high: number;
  };
  source_distribution: Record<string, number>;
  recent_activities: WorkActivity[];
  total_activities: number;
}

export interface TeamMemberScore {
  developer_id: number;
  developer_name: string;
  role_level: string;
  overall_score: number;
  complexity_score: number;
  velocity_score: number;
  quality_score: number;
  impact_score: number;
  collaboration_score: number;
  mentoring_score: number;
}

export interface TeamAnalytics {
  team: string;
  team_size: number;
  period_start: string;
  period_end: string;
  average_overall_score: number;
  average_complexity_score: number;
  average_velocity_score: number;
  average_quality_score: number;
  average_impact_score: number;
  average_collaboration_score: number;
  average_mentoring_score: number;
  top_performers: TeamMemberScore[];
  individual_scores: TeamMemberScore[];
}

export interface Insight {
  insight_type: string;
  title: string;
  description: string;
  confidence: number;
  recommendations: string[];
  supporting_data: Record<string, any>;
}

export interface DeveloperInsights {
  developer_id: number;
  developer_name: string;
  period_start: string;
  period_end: string;
  insights: Insight[];
  patterns_detected: string[];
  anomalies: Array<{
    type: string;
    description: string;
    severity: 'high' | 'medium' | 'low';
  }>;
}

export interface Integration {
  id: number;
  organization_id: number;
  type: 'github' | 'jira';
  status: 'active' | 'syncing' | 'error' | 'inactive';
  last_sync_at?: string;
  created_at: string;
  last_error?: string;
}

export interface IntegrationSyncResponse {
  job_id: string;
  message: string;
  estimated_time_minutes: number;
}

export interface SyncStatus {
  integration_id: number;
  status: string;
  last_sync_at?: string;
  last_error?: string;
  next_sync_estimate?: string;
  progress?: Record<string, any>;
}

export type RoleLevel = 'intern' | 'junior' | 'mid' | 'senior' | 'staff' | 'principal';
export type UserRole = 'admin' | 'manager' | 'developer';

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface ReviewNetworkNode {
  id: number;
  name: string;
  role_level: string;
}

export interface ReviewNetworkEdge {
  from_id: number;
  to_id: number;
  count: number;
}

export interface ReviewNetwork {
  team: string;
  nodes: ReviewNetworkNode[];
  edges: ReviewNetworkEdge[];
}

export interface ScoringWeights {
  complexity: number;
  velocity: number;
  quality: number;
  impact: number;
  collaboration: number;
  mentoring: number;
}

export type RegisterMode = 'create_org' | 'join_org';

export interface RegisterData {
  email: string;
  password: string;
  full_name: string;
  mode: RegisterMode;
  organization_name?: string;
  invite_code?: string;
}
