'use client';

import { useEffect, useState, useCallback, useRef } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore } from '../../store/auth';
import { analyticsAPI, developersAPI, integrationsAPI } from '../../lib/api';
import {
  DeveloperAnalyticsOverview,
  DeveloperProductivity,
  DeveloperInsights,
} from '../../types';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { useToast } from '../../components/ui/toast';
import { Onboarding } from '../../components/onboarding';
import { DashboardSkeleton, IntegrationsSkeleton, ProfileSkeleton } from '../../components/ui/skeleton';
import { BarChart, DonutChart, ProgressRing } from '../../components/ui/charts';

export default function DashboardPage() {
  const router = useRouter();
  const { user, logout } = useAuthStore();
  const { addToast } = useToast();

  const [overview, setOverview] = useState<DeveloperAnalyticsOverview | null>(null);
  const [productivity, setProductivity] = useState<DeveloperProductivity | null>(null);
  const [insights, setInsights] = useState<DeveloperInsights | null>(null);
  const [loading, setLoading] = useState(true);
  const [developerId, setDeveloperId] = useState<number | null>(null);
  const [analysisRunning, setAnalysisRunning] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'integrations' | 'profile'>('overview');
  const [integrations, setIntegrations] = useState<any[]>([]);
  const [syncStatus, setSyncStatus] = useState<Record<number, string>>({});

  // Integration setup modal state
  const [showAddModal, setShowAddModal] = useState<'github' | 'jira' | null>(null);
  const [addingIntegration, setAddingIntegration] = useState(false);
  const [integrationError, setIntegrationError] = useState<string | null>(null);

  // GitHub form
  const [githubToken, setGithubToken] = useState('');
  const [githubOrg, setGithubOrg] = useState('');

  // Jira form
  const [jiraUrl, setJiraUrl] = useState('');
  const [jiraUsername, setJiraUsername] = useState('');
  const [jiraToken, setJiraToken] = useState('');
  const [jiraProjects, setJiraProjects] = useState('');

  // Profile state
  const [developerProfile, setDeveloperProfile] = useState<any>(null);
  const [profileGithubUsername, setProfileGithubUsername] = useState('');
  const [profileJiraUsername, setProfileJiraUsername] = useState('');
  const [profileTeam, setProfileTeam] = useState('');
  const [profileRoleLevel, setProfileRoleLevel] = useState('mid');
  const [savingProfile, setSavingProfile] = useState(false);
  const [profileMessage, setProfileMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [onboardingDismissed, setOnboardingDismissed] = useState(false);
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const pollingRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (!user) {
      router.push('/login');
      return;
    }

    fetchData();
  }, [user]);

  // Real-time polling for sync status updates
  useEffect(() => {
    const hasActiveSyncs = Object.values(syncStatus).includes('syncing');

    if (hasActiveSyncs) {
      // Poll every 3 seconds when syncing
      pollingRef.current = setInterval(async () => {
        try {
          const intResponse = await integrationsAPI.list();
          setIntegrations(intResponse.data);

          // Check if any syncs completed
          const stillSyncing = intResponse.data.some((i: any) => i.status === 'syncing');
          if (!stillSyncing && hasActiveSyncs) {
            // Sync completed - refresh analytics
            addToast('Sync completed! Refreshing data...', 'success');
            fetchData();
          }
        } catch (e) {
          console.log('Polling error:', e);
        }
      }, 3000);
    }

    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
      }
    };
  }, [syncStatus]);

  // Auto-refresh analytics every 60 seconds when on overview tab
  useEffect(() => {
    if (!autoRefresh || activeTab !== 'overview' || !developerId) return;

    const refreshInterval = setInterval(() => {
      refreshAnalytics();
    }, 60000);

    return () => clearInterval(refreshInterval);
  }, [autoRefresh, activeTab, developerId]);

  const refreshAnalytics = useCallback(async () => {
    if (!developerId) return;

    try {
      const [overviewRes, productivityRes, insightsRes] = await Promise.all([
        analyticsAPI.getOverview(developerId),
        analyticsAPI.getProductivity(developerId, { include_comparison: true }),
        analyticsAPI.getInsights(developerId),
      ]);

      setOverview(overviewRes.data);
      setProductivity(productivityRes.data);
      setInsights(insightsRes.data);
      setLastRefresh(new Date());
    } catch (e) {
      console.log('Failed to refresh analytics');
    }
  }, [developerId]);

  const fetchData = async () => {
    try {
      setLoading(true);

      // Get developer profile
      const devsResponse = await developersAPI.list();
      const myProfile = devsResponse.data.find((d: any) => d.user_id === user?.id);

      if (myProfile) {
        setDeveloperId(myProfile.id);
        setDeveloperProfile(myProfile);
        setProfileGithubUsername(myProfile.github_username || '');
        setProfileJiraUsername(myProfile.jira_username || '');
        setProfileTeam(myProfile.team || '');
        setProfileRoleLevel(myProfile.role_level || 'mid');

        // Fetch analytics
        try {
          const [overviewRes, productivityRes, insightsRes] = await Promise.all([
            analyticsAPI.getOverview(myProfile.id),
            analyticsAPI.getProductivity(myProfile.id, { include_comparison: true }),
            analyticsAPI.getInsights(myProfile.id),
          ]);

          setOverview(overviewRes.data);
          setProductivity(productivityRes.data);
          setInsights(insightsRes.data);
        } catch (e) {
          console.log('Analytics not available yet');
        }
      }

      // Fetch integrations
      try {
        const intResponse = await integrationsAPI.list();
        setIntegrations(intResponse.data);
      } catch (e) {
        console.log('Could not fetch integrations');
      }

    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  const handleRunAnalysis = async () => {
    if (!developerId) {
      addToast('No developer profile found', 'error');
      return;
    }

    const confirmed = confirm(
      'AI Analysis Cost Warning\n\n' +
      'This will analyze your unanalyzed commits and tickets using AI.\n' +
      'Estimated cost: ~$0.01 per 100 items\n\n' +
      'Continue?'
    );

    if (!confirmed) return;

    try {
      setAnalysisRunning(true);
      const response = await analyticsAPI.triggerAnalysis(developerId, 50);
      addToast('AI Analysis started! This may take 2-5 minutes.', 'success');
    } catch (error: any) {
      addToast(error.response?.data?.detail || 'Failed to trigger analysis', 'error');
    } finally {
      setAnalysisRunning(false);
    }
  };

  const handleSync = async (integrationId: number, type: string) => {
    setSyncStatus(prev => ({ ...prev, [integrationId]: 'syncing' }));
    try {
      await integrationsAPI.sync(integrationId, 30);
      setSyncStatus(prev => ({ ...prev, [integrationId]: 'success' }));
      setTimeout(() => {
        setSyncStatus(prev => ({ ...prev, [integrationId]: '' }));
      }, 3000);
    } catch (error: any) {
      setSyncStatus(prev => ({ ...prev, [integrationId]: 'error' }));
      addToast(error.response?.data?.detail || 'Sync failed', 'error');
    }
  };

  const handleAddGitHub = async (e: React.FormEvent) => {
    e.preventDefault();
    setAddingIntegration(true);
    setIntegrationError(null);

    try {
      await integrationsAPI.configureGitHub({
        organization_name: githubOrg || 'personal',
        access_token: githubToken,
      });
      setShowAddModal(null);
      setGithubToken('');
      setGithubOrg('');
      addToast('GitHub connected successfully!', 'success');
      fetchData();
    } catch (error: any) {
      setIntegrationError(error.response?.data?.detail || 'Failed to add GitHub integration');
    } finally {
      setAddingIntegration(false);
    }
  };

  const handleAddJira = async (e: React.FormEvent) => {
    e.preventDefault();
    setAddingIntegration(true);
    setIntegrationError(null);

    try {
      await integrationsAPI.configureJira({
        workspace_url: jiraUrl,
        username: jiraUsername,
        api_token: jiraToken,
        project_keys: jiraProjects ? jiraProjects.split(',').map(p => p.trim()) : undefined,
      });
      setShowAddModal(null);
      setJiraUrl('');
      setJiraUsername('');
      setJiraToken('');
      setJiraProjects('');
      addToast('Jira connected successfully!', 'success');
      fetchData();
    } catch (error: any) {
      setIntegrationError(error.response?.data?.detail || 'Failed to add Jira integration');
    } finally {
      setAddingIntegration(false);
    }
  };

  const handleTestConnection = async (integrationId: number) => {
    try {
      const response = await integrationsAPI.test(integrationId);
      if (response.data.success) {
        addToast('Connection test successful!', 'success');
      } else {
        addToast(response.data.message || 'Connection test failed', 'error');
      }
    } catch (error: any) {
      addToast(error.response?.data?.detail || 'Connection test failed', 'error');
    }
  };

  const handleDeleteIntegration = async (integrationId: number) => {
    if (!confirm('Are you sure you want to remove this integration?')) return;

    try {
      await integrationsAPI.delete(integrationId);
      fetchData();
    } catch (error: any) {
      addToast(error.response?.data?.detail || 'Failed to delete integration', 'error');
    }
  };

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setSavingProfile(true);
    setProfileMessage(null);

    try {
      if (developerProfile) {
        // Update existing profile
        await developersAPI.update(developerProfile.id, {
          github_username: profileGithubUsername || null,
          jira_username: profileJiraUsername || null,
          team: profileTeam || null,
          role_level: profileRoleLevel,
        });
      } else {
        // Create new profile
        await developersAPI.create({
          github_username: profileGithubUsername || null,
          jira_username: profileJiraUsername || null,
          team: profileTeam || null,
          role_level: profileRoleLevel,
        });
      }
      setProfileMessage({ type: 'success', text: 'Profile saved successfully!' });
      fetchData();
    } catch (error: any) {
      setProfileMessage({
        type: 'error',
        text: error.response?.data?.detail || 'Failed to save profile',
      });
    } finally {
      setSavingProfile(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
        {/* Header Skeleton */}
        <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-sm sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
                    <span className="text-white font-bold text-lg">D</span>
                  </div>
                  <span className="text-xl font-semibold text-white hidden sm:block">DevMetrics AI</span>
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Tab Navigation Skeleton */}
        <div className="border-b border-slate-800 bg-slate-900/30">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <nav className="flex gap-8">
              <div className="py-4 px-1 border-b-2 border-blue-500">
                <div className="h-4 w-16 bg-slate-700/50 rounded animate-pulse" />
              </div>
              <div className="py-4 px-1 border-b-2 border-transparent">
                <div className="h-4 w-20 bg-slate-700/50 rounded animate-pulse" />
              </div>
              <div className="py-4 px-1 border-b-2 border-transparent">
                <div className="h-4 w-14 bg-slate-700/50 rounded animate-pulse" />
              </div>
            </nav>
          </div>
        </div>

        {/* Content Skeleton */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {activeTab === 'profile' ? (
            <ProfileSkeleton />
          ) : activeTab === 'integrations' ? (
            <IntegrationsSkeleton />
          ) : (
            <DashboardSkeleton />
          )}
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-4">
              <Link href="/" className="flex items-center gap-2">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
                  <span className="text-white font-bold text-lg">D</span>
                </div>
                <span className="text-xl font-semibold text-white hidden sm:block">DevMetrics AI</span>
              </Link>
              <div className="h-6 w-px bg-slate-700 hidden sm:block" />
              <div className="hidden sm:block">
                <p className="text-sm text-slate-400">
                  Welcome back, <span className="text-white font-medium">{user?.full_name}</span>
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              {(user?.role === 'manager' || user?.role === 'admin') && (
                <Button
                  onClick={handleRunAnalysis}
                  disabled={analysisRunning || !developerId}
                  className="bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white border-0"
                >
                  {analysisRunning ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      Analyzing...
                    </>
                  ) : (
                    'Run AI Analysis'
                  )}
                </Button>
              )}
              <Button
                onClick={handleLogout}
                variant="outline"
                className="border-slate-700 text-slate-300 hover:bg-slate-800 hover:text-white"
              >
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Tab Navigation */}
      <div className="border-b border-slate-800 bg-slate-900/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex gap-8">
            <button
              onClick={() => setActiveTab('overview')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'overview'
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-slate-400 hover:text-slate-300'
              }`}
            >
              Overview
            </button>
            <button
              onClick={() => setActiveTab('integrations')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'integrations'
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-slate-400 hover:text-slate-300'
              }`}
            >
              Integrations
            </button>
            <button
              onClick={() => setActiveTab('profile')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'profile'
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-slate-400 hover:text-slate-300'
              }`}
            >
              Profile
            </button>
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Onboarding for new users */}
        {!onboardingDismissed && activeTab === 'overview' && (
          <Onboarding
            hasProfile={!!developerProfile}
            hasIntegrations={integrations.length > 0}
            hasSyncedData={!!overview?.activity_summary?.total_activities}
            onGoToProfile={() => setActiveTab('profile')}
            onGoToIntegrations={() => setActiveTab('integrations')}
            onDismiss={() => setOnboardingDismissed(true)}
          />
        )}

        {activeTab === 'profile' ? (
          /* Profile Tab */
          <div className="space-y-6 animate-fade-in">
            <div>
              <h2 className="text-2xl font-bold text-white mb-2">Developer Profile</h2>
              <p className="text-slate-400">Configure your GitHub and Jira usernames to sync your work</p>
            </div>

            <form onSubmit={handleSaveProfile} className="max-w-lg">
              <div className="p-6 rounded-2xl bg-slate-800/30 border border-slate-700/50 space-y-6">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    GitHub Username
                  </label>
                  <Input
                    type="text"
                    value={profileGithubUsername}
                    onChange={(e) => setProfileGithubUsername(e.target.value)}
                    placeholder="your-github-username"
                    className="bg-slate-900/50 border-slate-700 text-white"
                  />
                  <p className="text-xs text-slate-500 mt-1">
                    Your GitHub username for syncing commits and PRs
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Jira Email/Username
                  </label>
                  <Input
                    type="text"
                    value={profileJiraUsername}
                    onChange={(e) => setProfileJiraUsername(e.target.value)}
                    placeholder="you@company.com"
                    className="bg-slate-900/50 border-slate-700 text-white"
                  />
                  <p className="text-xs text-slate-500 mt-1">
                    Your Jira email address for syncing tickets
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Team
                  </label>
                  <Input
                    type="text"
                    value={profileTeam}
                    onChange={(e) => setProfileTeam(e.target.value)}
                    placeholder="Engineering, Platform, etc."
                    className="bg-slate-900/50 border-slate-700 text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Role Level
                  </label>
                  <select
                    value={profileRoleLevel}
                    onChange={(e) => setProfileRoleLevel(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-900/50 border border-slate-700 text-white rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="intern">Intern</option>
                    <option value="junior">Junior</option>
                    <option value="mid">Mid-Level</option>
                    <option value="senior">Senior</option>
                    <option value="staff">Staff</option>
                    <option value="principal">Principal</option>
                  </select>
                  <p className="text-xs text-slate-500 mt-1">
                    Your role level affects how productivity is evaluated
                  </p>
                </div>

                {profileMessage && (
                  <div className={`p-3 rounded-lg text-sm ${
                    profileMessage.type === 'success'
                      ? 'bg-emerald-500/10 border border-emerald-500/20 text-emerald-400'
                      : 'bg-red-500/10 border border-red-500/20 text-red-400'
                  }`}>
                    {profileMessage.text}
                  </div>
                )}

                <Button
                  type="submit"
                  disabled={savingProfile}
                  className="w-full bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white"
                >
                  {savingProfile ? 'Saving...' : developerProfile ? 'Update Profile' : 'Create Profile'}
                </Button>
              </div>
            </form>

            {!developerProfile && (
              <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 max-w-lg">
                <p className="text-sm text-amber-400">
                  You need to create a developer profile to start tracking your work and see analytics.
                </p>
              </div>
            )}
          </div>
        ) : activeTab === 'integrations' ? (
          /* Integrations Tab */
          <div className="space-y-6 animate-fade-in">
            <div>
              <h2 className="text-2xl font-bold text-white mb-2">Integrations</h2>
              <p className="text-slate-400">Manage your GitHub and Jira connections</p>
            </div>

            {/* Add Integration Buttons */}
            {user?.role === 'admin' && (
              <div className="flex gap-4 mb-6">
                <Button
                  onClick={() => setShowAddModal('github')}
                  className="bg-slate-700 hover:bg-slate-600 text-white border-0"
                >
                  <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
                    <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
                  </svg>
                  Connect GitHub
                </Button>
                <Button
                  onClick={() => setShowAddModal('jira')}
                  className="bg-blue-600 hover:bg-blue-500 text-white border-0"
                >
                  <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M11.571 11.513H0a5.218 5.218 0 005.232 5.215h2.13v2.057A5.215 5.215 0 0012.575 24V12.518a1.005 1.005 0 00-1.005-1.005zm5.723-5.756H5.736a5.215 5.215 0 005.215 5.214h2.129v2.058a5.218 5.218 0 005.215 5.214V6.758a1.001 1.001 0 00-1.001-1.001zM23.013 0H11.455a5.215 5.215 0 005.215 5.215h2.129v2.057A5.215 5.215 0 0024 12.483V1.005A1.005 1.005 0 0023.013 0z" />
                  </svg>
                  Connect Jira
                </Button>
              </div>
            )}

            {integrations.length === 0 ? (
              <div className="p-8 rounded-2xl bg-slate-800/30 border border-slate-700/50 text-center">
                <div className="w-16 h-16 rounded-2xl bg-slate-700/50 flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">No Integrations Configured</h3>
                <p className="text-slate-400 mb-6">
                  {user?.role === 'admin'
                    ? 'Click the buttons above to connect your GitHub and Jira accounts.'
                    : 'Ask your administrator to configure integrations.'}
                </p>
              </div>
            ) : (
              <div className="grid gap-6">
                {integrations.map((integration) => (
                  <div key={integration.id} className="p-6 rounded-2xl bg-slate-800/30 border border-slate-700/50">
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-4">
                        <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                          integration.type === 'github'
                            ? 'bg-slate-700'
                            : 'bg-blue-600/20'
                        }`}>
                          {integration.type === 'github' ? (
                            <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                              <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
                            </svg>
                          ) : (
                            <svg className="w-6 h-6 text-blue-400" fill="currentColor" viewBox="0 0 24 24">
                              <path d="M11.571 11.513H0a5.218 5.218 0 005.232 5.215h2.13v2.057A5.215 5.215 0 0012.575 24V12.518a1.005 1.005 0 00-1.005-1.005zm5.723-5.756H5.736a5.215 5.215 0 005.215 5.214h2.129v2.058a5.218 5.218 0 005.215 5.214V6.758a1.001 1.001 0 00-1.001-1.001zM23.013 0H11.455a5.215 5.215 0 005.215 5.215h2.129v2.057A5.215 5.215 0 0024 12.483V1.005A1.005 1.005 0 0023.013 0z" />
                            </svg>
                          )}
                        </div>
                        <div>
                          <h3 className="text-lg font-semibold text-white capitalize">{integration.type}</h3>
                          <p className="text-sm text-slate-400">
                            {integration.config?.organization_name || integration.config?.url || 'Connected'}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                          integration.status === 'active'
                            ? 'bg-emerald-500/20 text-emerald-400'
                            : integration.status === 'syncing'
                            ? 'bg-blue-500/20 text-blue-400'
                            : 'bg-red-500/20 text-red-400'
                        }`}>
                          {integration.status}
                        </span>
                        <Button
                          onClick={() => handleSync(integration.id, integration.type)}
                          disabled={syncStatus[integration.id] === 'syncing'}
                          className="bg-slate-700 hover:bg-slate-600 text-white border-0"
                        >
                          {syncStatus[integration.id] === 'syncing' ? (
                            <>
                              <svg className="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                              </svg>
                              Syncing...
                            </>
                          ) : syncStatus[integration.id] === 'success' ? (
                            <>
                              <svg className="w-4 h-4 mr-2 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                              </svg>
                              Synced!
                            </>
                          ) : (
                            'Sync Data'
                          )}
                        </Button>
                        {user?.role === 'admin' && (
                          <>
                            <Button
                              onClick={() => handleTestConnection(integration.id)}
                              variant="outline"
                              className="border-slate-600 text-slate-300 hover:bg-slate-700"
                            >
                              Test
                            </Button>
                            <Button
                              onClick={() => handleDeleteIntegration(integration.id)}
                              variant="outline"
                              className="border-red-600/50 text-red-400 hover:bg-red-500/10"
                            >
                              Remove
                            </Button>
                          </>
                        )}
                      </div>
                    </div>
                    {integration.last_sync_at && (
                      <p className="mt-4 text-xs text-slate-500">
                        Last synced: {new Date(integration.last_sync_at).toLocaleString()}
                      </p>
                    )}
                    {integration.last_error && (
                      <div className="mt-4 p-3 rounded-lg bg-red-500/10 border border-red-500/20">
                        <p className="text-sm text-red-400">{integration.last_error}</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : (
          /* Overview Tab */
          <div className="space-y-6 animate-fade-in">
            {!productivity ? (
              <div className="p-8 rounded-2xl bg-slate-800/30 border border-slate-700/50">
                <div className="text-center max-w-lg mx-auto">
                  <div className="w-16 h-16 rounded-2xl bg-slate-700/50 flex items-center justify-center mx-auto mb-4">
                    <svg className="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <h2 className="text-2xl font-bold text-white mb-2">No Analytics Data Yet</h2>
                  <p className="text-slate-400 mb-6">
                    We haven't collected enough data to show analytics. Make sure your integrations are configured and synced.
                  </p>

                  <div className="space-y-3 text-left p-4 rounded-xl bg-slate-900/50 mb-6">
                    <p className="text-sm font-medium text-slate-300">To get started:</p>
                    <ol className="text-sm text-slate-400 space-y-2 list-decimal list-inside">
                      <li>Go to the Integrations tab</li>
                      <li>Sync your GitHub and Jira data</li>
                      <li>Run AI Analysis to process your work</li>
                    </ol>
                  </div>

                  {(user?.role === 'manager' || user?.role === 'admin') && (
                    <div className="space-y-4">
                      <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/20">
                        <p className="text-sm text-amber-400">
                          AI analysis uses the OpenAI API (~$0.01 per 100 items)
                        </p>
                      </div>
                      <Button
                        onClick={handleRunAnalysis}
                        disabled={analysisRunning || !developerId}
                        className="w-full bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white"
                      >
                        {analysisRunning ? 'Running Analysis...' : 'Run AI Analysis'}
                      </Button>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <>
                {/* Refresh Status Bar */}
                <div className="flex items-center justify-between p-3 rounded-xl bg-slate-800/30 border border-slate-700/50">
                  <div className="flex items-center gap-3">
                    <div className={`w-2 h-2 rounded-full ${autoRefresh ? 'bg-emerald-400 animate-pulse' : 'bg-slate-500'}`} />
                    <span className="text-sm text-slate-400">
                      {lastRefresh
                        ? `Last updated: ${lastRefresh.toLocaleTimeString()}`
                        : 'Auto-refresh enabled'}
                    </span>
                  </div>
                  <div className="flex items-center gap-3">
                    <button
                      onClick={() => setAutoRefresh(!autoRefresh)}
                      className={`text-xs px-3 py-1 rounded-full transition-colors ${
                        autoRefresh
                          ? 'bg-emerald-500/20 text-emerald-400'
                          : 'bg-slate-700 text-slate-400'
                      }`}
                    >
                      {autoRefresh ? 'Auto-refresh ON' : 'Auto-refresh OFF'}
                    </button>
                    <button
                      onClick={refreshAnalytics}
                      className="text-xs px-3 py-1 rounded-full bg-blue-500/20 text-blue-400 hover:bg-blue-500/30 transition-colors flex items-center gap-1"
                    >
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                      </svg>
                      Refresh
                    </button>
                  </div>
                </div>

                {/* Score Card */}
                <div className="grid md:grid-cols-3 gap-6">
                  <div className="md:col-span-1 p-8 rounded-2xl bg-gradient-to-br from-blue-600/20 to-cyan-600/20 border border-blue-500/20">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-blue-300 mb-2">Overall Score</p>
                        <div className="text-5xl font-bold gradient-text mb-2">
                          {productivity.overall_score.toFixed(0)}
                        </div>
                        <p className="text-slate-400 text-sm">out of 100</p>
                      </div>
                      <ProgressRing value={productivity.overall_score} max={100} size={90} />
                    </div>
                    <p className="text-slate-500 text-xs mt-4">
                      {productivity.period_start} to {productivity.period_end}
                    </p>
                  </div>

                  {/* Score Breakdown with Chart */}
                  <div className="md:col-span-2 p-6 rounded-2xl bg-slate-800/30 border border-slate-700/50">
                    <h3 className="text-lg font-semibold text-white mb-4">Score Breakdown</h3>
                    <div className="mb-6">
                      <BarChart
                        data={Object.entries(productivity.score_breakdown).map(([key, value]) => ({
                          label: key.charAt(0).toUpperCase() + key.slice(1),
                          value: Number(value),
                        }))}
                        maxValue={10}
                        height={160}
                      />
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                      {Object.entries(productivity.score_breakdown).map(([key, value]) => (
                        <div key={key} className="p-3 rounded-lg bg-slate-900/50 text-center">
                          <p className="text-xs text-slate-400 capitalize">{key}</p>
                          <p className="text-xl font-bold text-white">{Number(value).toFixed(1)}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Work Distribution */}
                {overview?.work_breakdown && Object.keys(overview.work_breakdown).length > 0 && (
                  <div className="p-6 rounded-2xl bg-slate-800/30 border border-slate-700/50">
                    <h3 className="text-lg font-semibold text-white mb-4">Work Distribution</h3>
                    <div className="flex flex-col md:flex-row items-center gap-8">
                      {/* Donut Chart */}
                      <div className="flex-shrink-0">
                        <DonutChart
                          data={Object.entries(overview.work_breakdown).map(([type, percentage], idx) => ({
                            label: type.replace('_', ' '),
                            value: Number(percentage),
                            color: ['#3b82f6', '#06b6d4', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981'][idx % 6],
                          }))}
                          size={140}
                          thickness={24}
                        />
                      </div>
                      {/* Legend & Bars */}
                      <div className="flex-1 w-full space-y-3">
                        {Object.entries(overview.work_breakdown).map(([type, percentage], idx) => {
                          const colors = ['#3b82f6', '#06b6d4', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981'];
                          return (
                            <div key={type}>
                              <div className="flex justify-between text-sm mb-1">
                                <div className="flex items-center gap-2">
                                  <div
                                    className="w-3 h-3 rounded-full"
                                    style={{ backgroundColor: colors[idx % 6] }}
                                  />
                                  <span className="text-slate-300 capitalize">{type.replace('_', ' ')}</span>
                                </div>
                                <span className="text-white font-medium">{Number(percentage).toFixed(1)}%</span>
                              </div>
                              <div className="h-1.5 bg-slate-700 rounded-full overflow-hidden">
                                <div
                                  className="h-full rounded-full transition-all duration-500"
                                  style={{ width: `${percentage}%`, backgroundColor: colors[idx % 6] }}
                                />
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  </div>
                )}

                {/* Activity Summary */}
                {overview?.activity_summary && (
                  <div className="p-6 rounded-2xl bg-slate-800/30 border border-slate-700/50">
                    <h3 className="text-lg font-semibold text-white mb-4">Activity Summary</h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      {[
                        { label: 'Total Activities', value: overview.activity_summary.total_activities },
                        { label: 'Commits', value: overview.activity_summary.total_commits },
                        { label: 'Tickets', value: overview.activity_summary.total_tickets },
                        { label: 'Active Days', value: overview.activity_summary.days_active },
                      ].map((item) => (
                        <div key={item.label} className="p-4 rounded-xl bg-slate-900/50 text-center">
                          <p className="text-3xl font-bold text-white">{item.value}</p>
                          <p className="text-xs text-slate-400 mt-1">{item.label}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* AI Insights */}
                {insights && insights.insights && insights.insights.length > 0 && (
                  <div className="p-6 rounded-2xl bg-slate-800/30 border border-slate-700/50">
                    <h3 className="text-lg font-semibold text-white mb-4">AI Insights</h3>
                    <div className="space-y-4">
                      {insights.insights.slice(0, 3).map((insight, idx) => (
                        <div key={idx} className="p-4 rounded-xl bg-slate-900/50 border border-slate-700/30">
                          <h4 className="font-medium text-white">{insight.title}</h4>
                          <p className="text-sm text-slate-400 mt-1">{insight.description}</p>
                          {insight.recommendations && insight.recommendations.length > 0 && (
                            <ul className="mt-3 space-y-1">
                              {insight.recommendations.slice(0, 2).map((rec: string, ridx: number) => (
                                <li key={ridx} className="text-sm text-slate-300 flex items-start gap-2">
                                  <span className="text-blue-400">•</span>
                                  {rec}
                                </li>
                              ))}
                            </ul>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </main>

      {/* GitHub Integration Modal */}
      {showAddModal === 'github' && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-slate-800 rounded-2xl border border-slate-700 w-full max-w-md p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-lg bg-slate-700 flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white">Connect GitHub</h3>
                <p className="text-sm text-slate-400">Add your GitHub personal access token</p>
              </div>
            </div>

            <form onSubmit={handleAddGitHub} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Personal Access Token <span className="text-red-400">*</span>
                </label>
                <Input
                  type="password"
                  value={githubToken}
                  onChange={(e) => setGithubToken(e.target.value)}
                  placeholder="ghp_xxxxxxxxxxxx"
                  required
                  className="bg-slate-900/50 border-slate-700 text-white"
                />
                <p className="text-xs text-slate-500 mt-1">
                  Create at GitHub Settings → Developer settings → Personal access tokens
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Organization Name (optional)
                </label>
                <Input
                  type="text"
                  value={githubOrg}
                  onChange={(e) => setGithubOrg(e.target.value)}
                  placeholder="Leave empty for personal account"
                  className="bg-slate-900/50 border-slate-700 text-white"
                />
              </div>

              {integrationError && (
                <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
                  {integrationError}
                </div>
              )}

              <div className="flex gap-3 pt-2">
                <Button
                  type="button"
                  onClick={() => {
                    setShowAddModal(null);
                    setIntegrationError(null);
                  }}
                  variant="outline"
                  className="flex-1 border-slate-600 text-slate-300"
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={addingIntegration || !githubToken}
                  className="flex-1 bg-gradient-to-r from-blue-600 to-cyan-600 text-white"
                >
                  {addingIntegration ? 'Connecting...' : 'Connect'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Jira Integration Modal */}
      {showAddModal === 'jira' && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-slate-800 rounded-2xl border border-slate-700 w-full max-w-md p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-lg bg-blue-600/20 flex items-center justify-center">
                <svg className="w-6 h-6 text-blue-400" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M11.571 11.513H0a5.218 5.218 0 005.232 5.215h2.13v2.057A5.215 5.215 0 0012.575 24V12.518a1.005 1.005 0 00-1.005-1.005zm5.723-5.756H5.736a5.215 5.215 0 005.215 5.214h2.129v2.058a5.218 5.218 0 005.215 5.214V6.758a1.001 1.001 0 00-1.001-1.001zM23.013 0H11.455a5.215 5.215 0 005.215 5.215h2.129v2.057A5.215 5.215 0 0024 12.483V1.005A1.005 1.005 0 0023.013 0z" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white">Connect Jira</h3>
                <p className="text-sm text-slate-400">Add your Jira Cloud credentials</p>
              </div>
            </div>

            <form onSubmit={handleAddJira} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Jira URL <span className="text-red-400">*</span>
                </label>
                <Input
                  type="url"
                  value={jiraUrl}
                  onChange={(e) => setJiraUrl(e.target.value)}
                  placeholder="https://yourcompany.atlassian.net"
                  required
                  className="bg-slate-900/50 border-slate-700 text-white"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Email Address <span className="text-red-400">*</span>
                </label>
                <Input
                  type="email"
                  value={jiraUsername}
                  onChange={(e) => setJiraUsername(e.target.value)}
                  placeholder="you@company.com"
                  required
                  className="bg-slate-900/50 border-slate-700 text-white"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  API Token <span className="text-red-400">*</span>
                </label>
                <Input
                  type="password"
                  value={jiraToken}
                  onChange={(e) => setJiraToken(e.target.value)}
                  placeholder="Your Jira API token"
                  required
                  className="bg-slate-900/50 border-slate-700 text-white"
                />
                <p className="text-xs text-slate-500 mt-1">
                  Create at id.atlassian.com → Security → API tokens
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Project Keys (optional)
                </label>
                <Input
                  type="text"
                  value={jiraProjects}
                  onChange={(e) => setJiraProjects(e.target.value)}
                  placeholder="PROJ, TEAM (comma-separated)"
                  className="bg-slate-900/50 border-slate-700 text-white"
                />
              </div>

              {integrationError && (
                <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
                  {integrationError}
                </div>
              )}

              <div className="flex gap-3 pt-2">
                <Button
                  type="button"
                  onClick={() => {
                    setShowAddModal(null);
                    setIntegrationError(null);
                  }}
                  variant="outline"
                  className="flex-1 border-slate-600 text-slate-300"
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={addingIntegration || !jiraUrl || !jiraUsername || !jiraToken}
                  className="flex-1 bg-gradient-to-r from-blue-600 to-cyan-600 text-white"
                >
                  {addingIntegration ? 'Connecting...' : 'Connect'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
