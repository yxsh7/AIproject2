'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/auth';
import { analyticsAPI, developersAPI } from '@/lib/api';
import {
  DeveloperAnalyticsOverview,
  DeveloperProductivity,
  DeveloperInsights,
} from '@/types';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

export default function DashboardPage() {
  const router = useRouter();
  const { user, logout } = useAuthStore();

  const [overview, setOverview] = useState<DeveloperAnalyticsOverview | null>(null);
  const [productivity, setProductivity] = useState<DeveloperProductivity | null>(null);
  const [insights, setInsights] = useState<DeveloperInsights | null>(null);
  const [loading, setLoading] = useState(true);
  const [developerId, setDeveloperId] = useState<number | null>(null);
  const [analysisRunning, setAnalysisRunning] = useState(false);

  useEffect(() => {
    if (!user) {
      router.push('/login');
      return;
    }

    fetchData();
  }, [user]);

  const fetchData = async () => {
    try {
      setLoading(true);

      // Get developer profile
      const devsResponse = await developersAPI.list();
      const myProfile = devsResponse.data.find((d: any) => d.user_id === user?.id);

      if (!myProfile) {
        console.error('No developer profile found');
        setLoading(false);
        return;
      }

      setDeveloperId(myProfile.id);

      // Fetch analytics
      const [overviewRes, productivityRes, insightsRes] = await Promise.all([
        analyticsAPI.getOverview(myProfile.id),
        analyticsAPI.getProductivity(myProfile.id, { include_comparison: true }),
        analyticsAPI.getInsights(myProfile.id),
      ]);

      setOverview(overviewRes.data);
      setProductivity(productivityRes.data);
      setInsights(insightsRes.data);
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
      alert('No developer profile found');
      return;
    }

    const confirmed = confirm(
      '⚠️ AI Analysis Cost Warning\n\n' +
      'This will analyze your unanalyzed commits and tickets using AI.\n' +
      'Estimated cost: ~$0.01 per 100 items\n\n' +
      'Continue?'
    );

    if (!confirmed) return;

    try {
      setAnalysisRunning(true);
      const response = await analyticsAPI.triggerAnalysis(developerId, 50);
      alert(
        `✅ AI Analysis Started!\n\n` +
        `${response.data.message}\n` +
        `Estimated cost: $${response.data.estimated_cost_usd}\n\n` +
        `This may take 2-5 minutes. Refresh the page after a few minutes to see updated analytics.`
      );
    } catch (error: any) {
      alert(`Error: ${error.response?.data?.detail || 'Failed to trigger analysis'}`);
    } finally {
      setAnalysisRunning(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading your analytics...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                DevMetrics AI
              </h1>
              <p className="text-sm text-muted-foreground">
                Welcome back, {user?.full_name}
              </p>
            </div>
            <div className="flex gap-2">
              {user?.role === 'manager' || user?.role === 'admin' ? (
                <Button
                  onClick={handleRunAnalysis}
                  disabled={analysisRunning || !developerId}
                  variant="default"
                >
                  {analysisRunning ? 'Running AI Analysis...' : '🤖 Run AI Analysis'}
                </Button>
              ) : null}
              <Button onClick={handleLogout} variant="outline">
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {!productivity ? (
          <Card>
            <CardHeader>
              <CardTitle>No Data Available</CardTitle>
              <CardDescription>
                We haven't collected enough data yet. Please ensure:
                <ul className="list-disc list-inside mt-2 space-y-1">
                  <li>GitHub and Jira integrations are configured</li>
                  <li>Data sync has been run</li>
                  <li>AI analysis tasks have completed</li>
                </ul>
              </CardDescription>
            </CardHeader>
            <CardContent>
              {user?.role === 'manager' || user?.role === 'admin' ? (
                <div className="space-y-4">
                  <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                    <p className="text-sm text-yellow-800 dark:text-yellow-200">
                      ⚠️ <strong>Cost Warning:</strong> AI analysis uses OpenAI API and costs approximately $0.01 per 100 items analyzed.
                      Only click the button below when you have new commits/tickets to analyze.
                    </p>
                  </div>
                  <Button
                    onClick={handleRunAnalysis}
                    disabled={analysisRunning || !developerId}
                    className="w-full"
                  >
                    {analysisRunning ? 'Running AI Analysis...' : '🤖 Run AI Analysis (Manual)'}
                  </Button>
                </div>
              ) : null}
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-6">
            {/* Overall Score */}
            <Card>
              <CardHeader>
                <CardTitle>Productivity Score</CardTitle>
                <CardDescription>
                  {productivity.period_start} to {productivity.period_end}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-center">
                  <div className="text-center">
                    <div className="text-6xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                      {productivity.overall_score.toFixed(1)}
                    </div>
                    <div className="text-sm text-muted-foreground mt-2">
                      out of 100
                    </div>
                  </div>
                </div>

                {productivity.comparison_to_team && (
                  <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                    <div className="text-sm font-medium">Team Comparison</div>
                    <div className="text-2xl font-bold mt-1">
                      {productivity.comparison_to_team.overall.difference > 0 ? '+' : ''}
                      {productivity.comparison_to_team.overall.difference.toFixed(1)}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      vs team average ({productivity.comparison_to_team.overall.team_average.toFixed(1)})
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Score Breakdown */}
            <Card>
              <CardHeader>
                <CardTitle>Score Breakdown</CardTitle>
                <CardDescription>Six dimensions of productivity</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {Object.entries(productivity.score_breakdown).map(([key, value]) => (
                    <div key={key} className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                      <div className="text-sm font-medium capitalize">{key}</div>
                      <div className="text-2xl font-bold mt-1">{value.toFixed(1)}</div>
                      <div className="text-xs text-muted-foreground">out of 10</div>
                      {productivity.evaluation_weights && (
                        <div className="text-xs text-muted-foreground mt-1">
                          Weight: {(productivity.evaluation_weights[key as keyof typeof productivity.evaluation_weights] * 100).toFixed(0)}%
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Work Breakdown */}
            {overview?.work_breakdown && (
              <Card>
                <CardHeader>
                  <CardTitle>Work Distribution</CardTitle>
                  <CardDescription>Breakdown by work type</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {Object.entries(overview.work_breakdown).map(([type, percentage]) => (
                      <div key={type}>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="capitalize">{type.replace('_', ' ')}</span>
                          <span className="font-medium">{percentage.toFixed(1)}%</span>
                        </div>
                        <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-gradient-to-r from-blue-500 to-purple-500"
                            style={{ width: `${percentage}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* AI Insights */}
            {insights && insights.insights.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>AI Insights</CardTitle>
                  <CardDescription>Personalized recommendations</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {insights.insights.slice(0, 3).map((insight, idx) => (
                      <div key={idx} className="p-4 border rounded-lg">
                        <div className="font-medium">{insight.title}</div>
                        <div className="text-sm text-muted-foreground mt-1">
                          {insight.description}
                        </div>
                        {insight.recommendations.length > 0 && (
                          <ul className="mt-3 space-y-1">
                            {insight.recommendations.slice(0, 2).map((rec, ridx) => (
                              <li key={ridx} className="text-sm flex items-start">
                                <span className="mr-2">•</span>
                                <span>{rec}</span>
                              </li>
                            ))}
                          </ul>
                        )}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Activity Summary */}
            {overview?.activity_summary && (
              <Card>
                <CardHeader>
                  <CardTitle>Activity Summary</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div>
                      <div className="text-sm text-muted-foreground">Total Activities</div>
                      <div className="text-2xl font-bold">{overview.activity_summary.total_activities}</div>
                    </div>
                    <div>
                      <div className="text-sm text-muted-foreground">Commits</div>
                      <div className="text-2xl font-bold">{overview.activity_summary.total_commits}</div>
                    </div>
                    <div>
                      <div className="text-sm text-muted-foreground">Tickets</div>
                      <div className="text-2xl font-bold">{overview.activity_summary.total_tickets}</div>
                    </div>
                    <div>
                      <div className="text-sm text-muted-foreground">Active Days</div>
                      <div className="text-2xl font-bold">{overview.activity_summary.days_active}</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
