'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '../../../store/auth';
import { analyticsAPI, developersAPI } from '../../../lib/api';
import { TeamAnalytics, DeveloperProductivity, DeveloperInsights } from '../../../types';
import { scoreCol } from '../../../lib/utils';

interface DeveloperWithUser {
  id: number;
  user_id: number;
  email: string;
  full_name: string;
  role_level: string;
  team?: string;
  github_username?: string;
  jira_username?: string;
}

interface DevPanel {
  productivity: DeveloperProductivity | null;
  insights: DeveloperInsights | null;
}

// ─── Helpers ──────────────────────────────────────────────────────────────────
function roleBadge(level: string) {
  const l = level?.toLowerCase();
  const color = (l === 'senior' || l === 'staff' || l === 'principal') ? '#7a9cc6'
    : l === 'mid' ? '#f59e0b' : '#52525b';
  return (
    <span style={{
      fontFamily: 'var(--font-mono)', fontSize: 9, padding: '2px 6px', borderRadius: 4,
      background: `${color}15`, color, letterSpacing: '0.06em', textTransform: 'uppercase' as const,
    }}>
      {level || '—'}
    </span>
  );
}

// ─── Mini dimension bar ───────────────────────────────────────────────────────
function SmallDimBar({ label, value }: { label: string; value: number }) {
  const col = scoreCol(value);
  return (
    <div style={{ marginBottom: 9 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 4 }}>
        <span style={{ fontSize: 11, color: 'var(--txt-2)' }}>{label}</span>
        <span className="mono" style={{ fontSize: 11, fontWeight: 600, color: col }}>{value.toFixed(1)}</span>
      </div>
      <div style={{ height: 3, background: 'rgba(255,255,255,0.05)', borderRadius: 2, overflow: 'hidden' }}>
        <div style={{ height: '100%', borderRadius: 2, background: col, opacity: 0.8, width: `${(value / 10) * 100}%`, transition: 'width 0.7s cubic-bezier(0.16,1,0.3,1)' }} />
      </div>
    </div>
  );
}

// ─── Developer detail panel ───────────────────────────────────────────────────
function DevDetailPanel({
  dev, panel, loading, onClose,
}: {
  dev: DeveloperWithUser;
  panel: DevPanel | null;
  loading: boolean;
  onClose: () => void;
}) {
  const prod = panel?.productivity;
  const ins  = panel?.insights;

  return (
    <>
      {/* Backdrop */}
      <div
        onClick={onClose}
        style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.55)', zIndex: 40 }}
      />

      {/* Panel */}
      <div
        className="panel-slide"
        style={{
          position: 'fixed', top: 0, right: 0, bottom: 0,
          width: 420, background: '#111',
          borderLeft: '1px solid rgba(255,255,255,0.07)',
          zIndex: 50, overflowY: 'auto',
          padding: '24px 24px 40px',
        }}
      >
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 24 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{
              width: 40, height: 40, borderRadius: 8,
              background: 'rgba(122,156,198,0.1)', border: '1px solid rgba(122,156,198,0.2)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 14, fontWeight: 700, color: 'var(--cyan)',
              fontFamily: 'var(--font-body)', flexShrink: 0,
            }}>
              {dev.full_name.charAt(0).toUpperCase()}
            </div>
            <div>
              <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--txt-1)', lineHeight: 1.2 }}>{dev.full_name}</div>
              <div style={{ fontSize: 11, color: 'var(--txt-3)', marginTop: 3 }}>{dev.email}</div>
              <div style={{ marginTop: 5 }}>{roleBadge(dev.role_level)}</div>
            </div>
          </div>
          <button
            onClick={onClose}
            style={{
              width: 28, height: 28, borderRadius: 6,
              background: 'transparent', border: '1px solid var(--border-1)',
              color: 'var(--txt-3)', cursor: 'pointer', fontSize: 13,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              flexShrink: 0,
            }}
          >
            ✕
          </button>
        </div>

        {/* Divider */}
        <div style={{ height: 1, background: 'rgba(255,255,255,0.05)', marginBottom: 20 }} />

        {/* Meta */}
        <div style={{ display: 'flex', gap: 8, marginBottom: 20, flexWrap: 'wrap' }}>
          {dev.team && (
            <span style={{ fontSize: 11, color: 'var(--txt-3)' }}>Team: <span style={{ color: 'var(--txt-2)' }}>{dev.team}</span></span>
          )}
          {dev.github_username && (
            <a
              href={`https://github.com/${dev.github_username}`}
              target="_blank" rel="noopener noreferrer"
              style={{ fontSize: 11, color: 'var(--cyan)', textDecoration: 'none', fontFamily: 'var(--font-mono)' }}
            >
              @{dev.github_username}
            </a>
          )}
        </div>

        {loading && (
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--txt-3)', letterSpacing: '0.1em', textAlign: 'center', padding: '40px 0' }}>
            Loading analytics…
          </div>
        )}

        {!loading && !prod && (
          <div style={{ padding: '32px 0', textAlign: 'center' }}>
            <div style={{ fontSize: 13, color: 'var(--txt-3)', marginBottom: 6 }}>No analytics data yet</div>
            <div style={{ fontSize: 11, color: 'var(--txt-3)' }}>Run analysis after syncing integrations</div>
          </div>
        )}

        {!loading && prod && (
          <>
            {/* Overall score */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 20, padding: '14px 16px', background: 'rgba(255,255,255,0.025)', borderRadius: 8 }}>
              <div>
                <div style={{ fontSize: 9, color: 'var(--txt-3)', textTransform: 'uppercase', letterSpacing: '0.08em', fontFamily: 'var(--font-mono)', marginBottom: 4 }}>Overall Score</div>
                <div className="mono" style={{ fontSize: 38, fontWeight: 700, color: scoreCol(prod.overall_score, true), lineHeight: 1 }}>
                  {prod.overall_score.toFixed(1)}
                </div>
                <div style={{ fontSize: 10, color: 'var(--txt-3)', marginTop: 3 }}>out of 100</div>
              </div>
              {prod.comparison_to_team && (
                <div style={{ marginLeft: 'auto', textAlign: 'right' }}>
                  <div style={{ fontSize: 9, color: 'var(--txt-3)', textTransform: 'uppercase', letterSpacing: '0.08em', fontFamily: 'var(--font-mono)', marginBottom: 4 }}>vs Team</div>
                  <div className="mono" style={{
                    fontSize: 20, fontWeight: 700,
                    color: prod.comparison_to_team.overall.difference >= 0 ? '#4ade80' : '#f87171',
                  }}>
                    {prod.comparison_to_team.overall.difference >= 0 ? '+' : ''}
                    {prod.comparison_to_team.overall.difference.toFixed(1)}
                  </div>
                  <div style={{ fontSize: 10, color: 'var(--txt-3)', marginTop: 3 }}>
                    avg {prod.comparison_to_team.overall.team_average.toFixed(1)}
                  </div>
                </div>
              )}
            </div>

            {/* Score breakdown */}
            <div style={{ marginBottom: 20 }}>
              <div style={{ fontSize: 10, color: 'var(--txt-3)', textTransform: 'uppercase', letterSpacing: '0.08em', fontFamily: 'var(--font-mono)', marginBottom: 12 }}>
                Score Breakdown
              </div>
              {Object.entries(prod.score_breakdown).map(([k, v]) => (
                <SmallDimBar
                  key={k}
                  label={k.charAt(0).toUpperCase() + k.slice(1)}
                  value={v}
                />
              ))}
            </div>

            {/* Period */}
            <div style={{ fontSize: 10, color: 'var(--txt-3)', fontFamily: 'var(--font-mono)', marginBottom: 20 }}>
              Period: {prod.period_start} → {prod.period_end}
            </div>

            {/* Insights */}
            {ins && ins.insights.length > 0 && (
              <>
                <div style={{ height: 1, background: 'rgba(255,255,255,0.05)', marginBottom: 16 }} />
                <div style={{ fontSize: 10, color: 'var(--txt-3)', textTransform: 'uppercase', letterSpacing: '0.08em', fontFamily: 'var(--font-mono)', marginBottom: 12 }}>
                  AI Insights
                </div>
                {ins.insights.slice(0, 4).map((insight, i) => (
                  <div key={i} style={{
                    borderLeft: '2px solid rgba(122,156,198,0.4)',
                    padding: '10px 14px', marginBottom: 8,
                    background: 'rgba(122,156,198,0.04)',
                    borderRadius: '0 7px 7px 0',
                  }}>
                    <div style={{ fontSize: 12, fontWeight: 500, color: 'var(--txt-1)', marginBottom: 4 }}>{insight.title}</div>
                    <div style={{ fontSize: 11, color: 'var(--txt-2)', lineHeight: 1.5 }}>{insight.description}</div>
                    <div className="mono" style={{ fontSize: 9, color: 'var(--txt-3)', marginTop: 5 }}>
                      {Math.round(insight.confidence * 100)}% confidence
                    </div>
                  </div>
                ))}
              </>
            )}

            {/* Anomalies */}
            {ins && ins.anomalies?.length > 0 && (
              <>
                <div style={{ height: 1, background: 'rgba(255,255,255,0.05)', marginBottom: 16, marginTop: 8 }} />
                <div style={{ fontSize: 10, color: 'var(--txt-3)', textTransform: 'uppercase', letterSpacing: '0.08em', fontFamily: 'var(--font-mono)', marginBottom: 12 }}>
                  Anomalies
                </div>
                {ins.anomalies.map((a, i) => (
                  <div key={i} style={{ display: 'flex', gap: 10, padding: '7px 0', borderBottom: '1px solid rgba(255,255,255,0.03)', alignItems: 'flex-start' }}>
                    <span style={{
                      fontFamily: 'var(--font-mono)', fontSize: 9, padding: '2px 6px', borderRadius: 4,
                      background: a.severity === 'high' ? 'var(--red-dim)' : 'var(--amber-dim)',
                      color: a.severity === 'high' ? 'var(--red)' : 'var(--amber)',
                      flexShrink: 0,
                    }}>
                      {a.severity}
                    </span>
                    <span style={{ fontSize: 11, color: 'var(--txt-2)' }}>{a.description}</span>
                  </div>
                ))}
              </>
            )}
          </>
        )}
      </div>
    </>
  );
}

// ─── Page ─────────────────────────────────────────────────────────────────────
export default function ManagerDashboardPage() {
  const router = useRouter();
  const { user, isInitializing } = useAuthStore();

  const [developers,   setDevelopers]   = useState<DeveloperWithUser[]>([]);
  const [teamData,     setTeamData]     = useState<TeamAnalytics | null>(null);
  const [selectedTeam, setSelectedTeam] = useState<string>('');
  const [teams,        setTeams]        = useState<string[]>([]);
  const [loading,      setLoading]      = useState(true);
  const [teamLoading,  setTeamLoading]  = useState(false);
  const [error,        setError]        = useState<string | null>(null);

  // Developer detail panel
  const [selectedDev,  setSelectedDev]  = useState<DeveloperWithUser | null>(null);
  const [devPanel,     setDevPanel]     = useState<DevPanel | null>(null);
  const [panelLoading, setPanelLoading] = useState(false);

  useEffect(() => {
    if (isInitializing) return;
    if (!user) { router.push('/login'); return; }
    if (user.role !== 'manager' && user.role !== 'admin') { router.push('/dashboard'); return; }
    fetchDevelopers();
  }, [user, isInitializing]);

  const fetchDevelopers = async () => {
    try {
      setLoading(true);
      const res = await developersAPI.list();
      const devs: DeveloperWithUser[] = res.data;
      setDevelopers(devs);
      const uniqueTeams = Array.from(new Set(devs.map((d) => d.team).filter((t): t is string => !!t)));
      setTeams(uniqueTeams);
      if (uniqueTeams.length > 0) {
        setSelectedTeam(uniqueTeams[0]);
        await fetchTeamData(uniqueTeams[0]);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load developer data');
    } finally {
      setLoading(false);
    }
  };

  const fetchTeamData = async (team: string) => {
    if (!team) return;
    try {
      setTeamLoading(true);
      const res = await analyticsAPI.getTeamOverview(team);
      setTeamData(res.data);
    } catch {
      setTeamData(null);
    } finally {
      setTeamLoading(false);
    }
  };

  const handleTeamChange = async (team: string) => {
    setSelectedTeam(team);
    await fetchTeamData(team);
  };

  const openDevPanel = async (dev: DeveloperWithUser) => {
    setSelectedDev(dev);
    setDevPanel(null);
    setPanelLoading(true);
    const [prRes, inRes] = await Promise.allSettled([
      analyticsAPI.getProductivity(dev.id),
      analyticsAPI.getInsights(dev.id),
    ]);
    setDevPanel({
      productivity: prRes.status === 'fulfilled' ? prRes.value.data : null,
      insights:     inRes.status === 'fulfilled' ? inRes.value.data : null,
    });
    setPanelLoading(false);
  };

  const closePanel = () => { setSelectedDev(null); setDevPanel(null); };

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', background: 'var(--surf-0)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--txt-3)', letterSpacing: '0.1em' }}>Loading…</div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', background: 'var(--surf-0)', color: 'var(--txt-1)' }}>

      {/* Detail panel */}
      {selectedDev && (
        <DevDetailPanel
          dev={selectedDev}
          panel={devPanel}
          loading={panelLoading}
          onClose={closePanel}
        />
      )}

      {/* Header */}
      <header style={{
        position: 'sticky', top: 0, zIndex: 30,
        background: 'rgba(10,10,10,0.9)',
        backdropFilter: 'blur(16px)',
        borderBottom: '1px solid var(--border-0)',
        padding: '0 24px', height: 52,
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{
            width: 28, height: 28, background: 'var(--cyan)', borderRadius: 6,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 10, fontWeight: 700, fontFamily: 'var(--font-mono)', color: '#0a0a0a',
          }}>DM</div>
          <span style={{ fontSize: 14, fontWeight: 600, color: 'var(--txt-1)', letterSpacing: '-0.01em' }}>DevMetrics</span>
          <div style={{ width: 1, height: 14, background: 'var(--border-1)' }} />
          <span style={{ fontSize: 11, color: 'var(--txt-3)' }}>Team Overview</span>
        </div>
        <div style={{ display: 'flex', gap: 6 }}>
          {user?.is_superadmin && (
            <button className="dm-btn" onClick={() => router.push('/dashboard/superadmin')} style={{ fontSize: 11 }}>Platform Admin</button>
          )}
          <button className="dm-btn" onClick={() => router.push('/dashboard/integrations')} style={{ fontSize: 11 }}>Integrations</button>
          <button className="dm-btn" onClick={() => router.push('/dashboard/settings')} style={{ fontSize: 11 }}>Settings</button>
          <button className="dm-btn" onClick={() => router.push('/dashboard')} style={{ fontSize: 11 }}>My Dashboard</button>
        </div>
      </header>

      <main style={{ maxWidth: 1100, margin: '0 auto', padding: '24px 24px' }}>

        {error && (
          <div style={{ background: 'var(--red-dim)', border: '1px solid rgba(248,113,113,0.2)', borderRadius: 8, padding: '10px 14px', fontSize: 12, color: 'var(--red)', marginBottom: 20 }}>
            {error}
          </div>
        )}

        {/* Team selector */}
        {teams.length > 1 && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
            <span style={{ fontSize: 11, color: 'var(--txt-3)' }}>Team</span>
            <div style={{ display: 'flex', gap: 6 }}>
              {teams.map((team) => (
                <button
                  key={team}
                  onClick={() => handleTeamChange(team)}
                  className={selectedTeam === team ? 'dm-btn dm-btn-cyan' : 'dm-btn'}
                  style={{ fontSize: 11 }}
                >
                  {team}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Team analytics */}
        {teamLoading ? (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 10, marginBottom: 12 }}>
            {[...Array(4)].map((_, i) => (
              <div key={i} className="shimmer" style={{ height: 80, borderRadius: 10 }} />
            ))}
          </div>
        ) : teamData ? (
          <>
            {/* KPI row */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 10, marginBottom: 12 }}>
              {[
                { label: 'Team Size',   value: String(teamData.team_size), unit: 'devs',  color: 'var(--txt-1)' },
                { label: 'Avg Score',   value: teamData.average_overall_score.toFixed(1), unit: '/100', color: scoreCol(teamData.average_overall_score, true) },
                { label: 'Avg Quality', value: teamData.average_quality_score.toFixed(1), unit: '/10',  color: scoreCol(teamData.average_quality_score) },
                { label: 'Avg Collab',  value: teamData.average_collaboration_score.toFixed(1), unit: '/10', color: scoreCol(teamData.average_collaboration_score) },
              ].map((kpi) => (
                <div key={kpi.label} className="dm-card fade-up" style={{ padding: '16px 18px' }}>
                  <div className="dm-label">{kpi.label}</div>
                  <div style={{ display: 'flex', alignItems: 'baseline', gap: 3 }}>
                    <span className="mono" style={{ fontSize: 26, fontWeight: 700, color: kpi.color, lineHeight: 1 }}>{kpi.value}</span>
                    <span className="mono" style={{ fontSize: 10, color: 'var(--txt-3)' }}>{kpi.unit}</span>
                  </div>
                </div>
              ))}
            </div>

            {/* Breakdown + top performers */}
            <div className="dm-two-col" style={{ marginBottom: 12 }}>
              <div className="dm-card">
                <div className="dm-label">Team Score Breakdown</div>
                {[
                  { label: 'Overall',       value: teamData.average_overall_score,       max10: false },
                  { label: 'Complexity',    value: teamData.average_complexity_score,    max10: true  },
                  { label: 'Velocity',      value: teamData.average_velocity_score,      max10: true  },
                  { label: 'Quality',       value: teamData.average_quality_score,       max10: true  },
                  { label: 'Impact',        value: teamData.average_impact_score,        max10: true  },
                  { label: 'Collaboration', value: teamData.average_collaboration_score, max10: true  },
                  { label: 'Mentoring',     value: teamData.average_mentoring_score,     max10: true  },
                ].map(({ label, value, max10 }) => {
                  const pct   = max10 ? (value / 10) * 100 : value;
                  const col   = scoreCol(value, !max10);
                  return (
                    <div key={label} style={{ marginBottom: 10 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 4 }}>
                        <span style={{ fontSize: 11, color: 'var(--txt-2)' }}>{label}</span>
                        <span className="mono" style={{ fontSize: 11, fontWeight: 600, color: col }}>
                          {value.toFixed(1)}{max10 ? '/10' : '/100'}
                        </span>
                      </div>
                      <div style={{ height: 3, background: 'rgba(255,255,255,0.05)', borderRadius: 2, overflow: 'hidden' }}>
                        <div style={{ height: '100%', borderRadius: 2, background: col, opacity: 0.8, width: `${pct}%` }} />
                      </div>
                    </div>
                  );
                })}
              </div>

              <div className="dm-card">
                <div className="dm-label">Top Performers</div>
                {teamData.top_performers.length === 0 ? (
                  <p style={{ fontSize: 12, color: 'var(--txt-3)' }}>No data yet</p>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    {teamData.top_performers.map((dev, idx) => (
                      <div
                        key={dev.developer_id}
                        onClick={() => {
                          const d = developers.find(d => d.id === dev.developer_id);
                          if (d) openDevPanel(d);
                        }}
                        style={{
                          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                          padding: '10px 14px', background: 'var(--surf-2)',
                          border: '1px solid var(--border-0)', borderRadius: 8,
                          cursor: 'pointer', transition: 'border-color 0.12s',
                        }}
                        onMouseEnter={e => (e.currentTarget.style.borderColor = 'rgba(255,255,255,0.1)')}
                        onMouseLeave={e => (e.currentTarget.style.borderColor = 'var(--border-0)')}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                          <span className="mono" style={{ fontSize: 10, color: 'var(--txt-3)', width: 20 }}>#{idx + 1}</span>
                          <div>
                            <div style={{ fontSize: 12, fontWeight: 500, color: 'var(--txt-1)' }}>{dev.developer_name}</div>
                            <div style={{ marginTop: 3 }}>{roleBadge(dev.role_level)}</div>
                          </div>
                        </div>
                        <div style={{ textAlign: 'right' }}>
                          <div className="mono" style={{ fontSize: 18, fontWeight: 700, color: scoreCol(dev.overall_score, true), lineHeight: 1 }}>
                            {dev.overall_score.toFixed(1)}
                          </div>
                          <div style={{ fontSize: 9, color: 'var(--txt-3)', marginTop: 2 }}>overall</div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* All members table */}
            <div className="dm-card" style={{ marginBottom: 12 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                <span className="dm-label" style={{ marginBottom: 0 }}>Individual Scores</span>
                <span style={{ fontSize: 10, color: 'var(--txt-3)', fontFamily: 'var(--font-mono)' }}>Click a row to review</span>
              </div>
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid var(--border-1)' }}>
                      {['Developer', 'Role', 'Overall', 'Complexity', 'Velocity', 'Quality', 'Impact'].map((h) => (
                        <th key={h} style={{
                          padding: '0 14px 10px 0', textAlign: h === 'Developer' || h === 'Role' ? 'left' : 'right',
                          fontFamily: 'var(--font-mono)', fontSize: 9, fontWeight: 600,
                          color: 'var(--txt-3)', letterSpacing: '0.08em', textTransform: 'uppercase',
                        }}>{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {teamData.individual_scores.map((dev) => (
                      <tr
                        key={dev.developer_id}
                        onClick={() => {
                          const d = developers.find(d => d.id === dev.developer_id);
                          if (d) openDevPanel(d);
                        }}
                        style={{ borderBottom: '1px solid var(--border-0)', cursor: 'pointer', transition: 'background 0.1s' }}
                        onMouseEnter={e => (e.currentTarget.style.background = 'rgba(255,255,255,0.025)')}
                        onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}
                      >
                        <td style={{ padding: '10px 14px 10px 0', fontWeight: 500, color: 'var(--txt-1)' }}>{dev.developer_name}</td>
                        <td style={{ padding: '10px 14px 10px 0' }}>{roleBadge(dev.role_level)}</td>
                        <td style={{ padding: '10px 14px 10px 0', textAlign: 'right' }}>
                          <span className="mono" style={{ fontWeight: 700, color: scoreCol(dev.overall_score, true) }}>
                            {dev.overall_score.toFixed(1)}
                          </span>
                        </td>
                        <td style={{ padding: '10px 14px 10px 0', textAlign: 'right' }}>
                          <span className="mono" style={{ color: 'var(--txt-2)' }}>{dev.complexity_score.toFixed(1)}</span>
                        </td>
                        <td style={{ padding: '10px 14px 10px 0', textAlign: 'right' }}>
                          <span className="mono" style={{ color: 'var(--txt-2)' }}>{dev.velocity_score.toFixed(1)}</span>
                        </td>
                        <td style={{ padding: '10px 14px 10px 0', textAlign: 'right' }}>
                          <span className="mono" style={{ color: 'var(--txt-2)' }}>{dev.quality_score.toFixed(1)}</span>
                        </td>
                        <td style={{ padding: '10px 14px 10px 0', textAlign: 'right' }}>
                          <span className="mono" style={{ color: 'var(--txt-2)' }}>{dev.impact_score.toFixed(1)}</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        ) : (
          <div className="dm-card" style={{ padding: '40px', textAlign: 'center', marginBottom: 12 }}>
            <p style={{ fontSize: 14, fontWeight: 500, marginBottom: 8 }}>No Team Analytics</p>
            <p style={{ fontSize: 13, color: 'var(--txt-2)', marginBottom: 20 }}>
              {selectedTeam
                ? `No data for team "${selectedTeam}". Configure integrations and sync first.`
                : 'No teams found. Assign developers to teams to enable analytics.'}
            </p>
            <button className="dm-btn dm-btn-cyan" onClick={() => router.push('/dashboard/integrations')} style={{ fontSize: 11 }}>
              Configure Integrations
            </button>
          </div>
        )}

        {/* All developers */}
        <div className="dm-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <span className="dm-label" style={{ marginBottom: 0 }}>All Developers</span>
            <span style={{ fontSize: 10, color: 'var(--txt-3)', fontFamily: 'var(--font-mono)' }}>{developers.length} registered · click to review</span>
          </div>
          {developers.length === 0 ? (
            <p style={{ fontSize: 12, color: 'var(--txt-3)' }}>No profiles found</p>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-1)' }}>
                    {['Name', 'Email', 'Role', 'Team', 'GitHub'].map((h) => (
                      <th key={h} style={{
                        padding: '0 14px 10px 0', textAlign: 'left',
                        fontFamily: 'var(--font-mono)', fontSize: 9, fontWeight: 600,
                        color: 'var(--txt-3)', letterSpacing: '0.08em', textTransform: 'uppercase',
                      }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {developers.map((dev) => (
                    <tr
                      key={dev.id}
                      onClick={() => openDevPanel(dev)}
                      style={{ borderBottom: '1px solid var(--border-0)', cursor: 'pointer', transition: 'background 0.1s' }}
                      onMouseEnter={e => (e.currentTarget.style.background = 'rgba(255,255,255,0.025)')}
                      onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}
                    >
                      <td style={{ padding: '10px 14px 10px 0', fontWeight: 500, color: 'var(--txt-1)' }}>{dev.full_name}</td>
                      <td style={{ padding: '10px 14px 10px 0', color: 'var(--txt-3)', fontFamily: 'var(--font-mono)', fontSize: 11 }}>{dev.email}</td>
                      <td style={{ padding: '10px 14px 10px 0' }}>{roleBadge(dev.role_level)}</td>
                      <td style={{ padding: '10px 14px 10px 0', color: 'var(--txt-3)' }}>{dev.team || '—'}</td>
                      <td style={{ padding: '10px 14px 10px 0' }}>
                        {dev.github_username ? (
                          <a
                            href={`https://github.com/${dev.github_username}`}
                            target="_blank" rel="noopener noreferrer"
                            onClick={e => e.stopPropagation()}
                            style={{ color: 'var(--cyan)', textDecoration: 'none', fontFamily: 'var(--font-mono)', fontSize: 11 }}
                          >
                            @{dev.github_username}
                          </a>
                        ) : <span style={{ color: 'var(--txt-3)' }}>—</span>}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
