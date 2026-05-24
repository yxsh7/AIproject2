'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '../../store/auth';
import { analyticsAPI, developersAPI } from '../../lib/api';
import { scoreCol } from '../../lib/utils';
import {
  DeveloperAnalyticsOverview,
  DeveloperProductivity,
  DeveloperInsights,
  DeveloperTrends,
  WorkBreakdown,
} from '../../types';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer,
} from 'recharts';

// ─── Helpers ──────────────────────────────────────────────────────────────────
function fmtPeriod(s: string) {
  try { return new Date(s).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }); }
  catch { return s; }
}

const DIM_OPTIONS = [
  { key: 'overall',  label: 'Overall',   color: '#818cf8' },
  { key: 'quality',  label: 'Quality',   color: '#4ade80' },
  { key: 'impact',   label: 'Impact',    color: '#f59e0b' },
  { key: 'velocity', label: 'Velocity',  color: '#f87171' },
] as const;
type DimKey = typeof DIM_OPTIONS[number]['key'];

const WORK_COLORS = ['#818cf8','#f59e0b','#4ade80','#c084fc','#f87171','#60a5fa','#34d399','#fb923c'];

// ─── Score Ring ───────────────────────────────────────────────────────────────
function ScoreRing({ score }: { score: number }) {
  const [go, setGo] = useState(false);
  useEffect(() => { const t = setTimeout(() => setGo(true), 100); return () => clearTimeout(t); }, []);
  const R    = 56;
  const circ = 2 * Math.PI * R;
  const col  = scoreCol(score, true);
  const off  = circ * (1 - Math.min(score / 100, 1));
  return (
    <div style={{ position: 'relative', width: 168, height: 168, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <svg width="168" height="168" style={{ position: 'absolute', transform: 'rotate(-90deg)' }}>
        <circle cx="84" cy="84" r={R} fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="6" />
        <circle
          cx="84" cy="84" r={R}
          fill="none" stroke={col} strokeWidth="6" strokeLinecap="round"
          strokeDasharray={circ}
          strokeDashoffset={go ? off : circ}
          style={{ transition: 'stroke-dashoffset 1.4s cubic-bezier(0.16,1,0.3,1)' }}
        />
      </svg>
      <div style={{ position: 'relative', textAlign: 'center', userSelect: 'none' }}>
        <div className="mono" style={{ fontSize: 48, fontWeight: 700, lineHeight: 1, color: col }}>
          {score.toFixed(0)}
        </div>
        <div style={{ fontSize: 10, color: 'var(--txt-3)', marginTop: 4 }}>out of 100</div>
      </div>
    </div>
  );
}

// ─── Dimension bar row ────────────────────────────────────────────────────────
function DimRow({ label, value, weight, delay }: { label: string; value: number; weight?: number; delay: number }) {
  const [go, setGo] = useState(false);
  useEffect(() => { const t = setTimeout(() => setGo(true), delay); return () => clearTimeout(t); }, [delay]);
  const col = scoreCol(value);
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '7px 0', borderBottom: '1px solid rgba(255,255,255,0.03)' }}>
      <div style={{ width: 86, fontSize: 11, color: 'var(--txt-2)', flexShrink: 0 }}>{label}</div>
      <div style={{ flex: 1, height: 4, background: 'rgba(255,255,255,0.05)', borderRadius: 2, overflow: 'hidden' }}>
        <div style={{
          height: '100%', borderRadius: 2, backgroundColor: col, opacity: 0.85,
          width: go ? `${(value / 10) * 100}%` : '0%',
          transition: 'width 1s cubic-bezier(0.16,1,0.3,1)',
        }} />
      </div>
      <div className="mono" style={{ width: 32, textAlign: 'right', fontSize: 12, fontWeight: 600, color: col, flexShrink: 0 }}>
        {value.toFixed(1)}
      </div>
      {weight !== undefined && (
        <div className="mono" style={{ width: 28, textAlign: 'right', fontSize: 9, color: 'var(--txt-3)', flexShrink: 0 }}>
          {Math.round(weight * 100)}%
        </div>
      )}
    </div>
  );
}

// ─── Mini stat tile ───────────────────────────────────────────────────────────
function MiniStat({ label, value }: { label: string; value: string | number }) {
  return (
    <div style={{ background: 'rgba(255,255,255,0.025)', borderRadius: 8, padding: '13px 15px' }}>
      <div style={{ fontSize: 10, color: 'var(--txt-3)', marginBottom: 7, textTransform: 'uppercase', letterSpacing: '0.06em', fontFamily: 'var(--font-mono)' }}>
        {label}
      </div>
      <div className="mono" style={{ fontSize: 22, fontWeight: 700, color: 'var(--txt-1)', lineHeight: 1 }}>
        {value}
      </div>
    </div>
  );
}

// ─── Insight card ─────────────────────────────────────────────────────────────
function InsightCard({ insight }: { insight: any }) {
  const TYPE_COL: Record<string, string> = {
    recommendation: '#818cf8',
    trend:          '#4ade80',
    anomaly:        '#f59e0b',
    consistency:    '#4ade80',
    individual:     '#c084fc',
    growth_path:    '#818cf8',
    work_preference:'#f59e0b',
    collaboration_gap: '#f87171',
  };
  const col = TYPE_COL[insight.insight_type] || '#818cf8';
  return (
    <div style={{
      borderLeft: `2px solid ${col}`,
      background: `${col}07`,
      borderRadius: '0 8px 8px 0',
      padding: '13px 16px',
      marginBottom: 8,
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 10, marginBottom: 5 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
          <span className="dm-tag" style={{ background: `${col}15`, color: col, fontSize: 9, border: 'none' }}>
            {(insight.insight_type || 'insight').replace(/_/g, ' ')}
          </span>
          <span style={{ fontSize: 13, fontWeight: 500, color: 'var(--txt-1)' }}>{insight.title}</span>
        </div>
        <span className="mono" style={{ fontSize: 9, color: 'var(--txt-3)', flexShrink: 0 }}>
          {Math.round(insight.confidence * 100)}%
        </span>
      </div>
      <p style={{ fontSize: 12, color: 'var(--txt-2)', lineHeight: 1.55, margin: 0 }}>{insight.description}</p>
      {insight.recommendations?.slice(0, 2).map((r: string, i: number) => (
        <div key={i} style={{ display: 'flex', gap: 7, marginTop: 6, alignItems: 'flex-start' }}>
          <span style={{ fontSize: 10, color: col, flexShrink: 0, marginTop: 1 }}>›</span>
          <span style={{ fontSize: 11, color: 'var(--txt-2)', lineHeight: 1.5 }}>{r}</span>
        </div>
      ))}
    </div>
  );
}

// ─── Skeleton ─────────────────────────────────────────────────────────────────
function Skeleton({ h = 200 }: { h?: number }) {
  return <div className="shimmer" style={{ height: h, borderRadius: 10, marginBottom: 12 }} />;
}

// ─── Page ─────────────────────────────────────────────────────────────────────
export default function DashboardPage() {
  const router = useRouter();
  const { user, logout } = useAuthStore();

  const [overview,      setOverview]      = useState<DeveloperAnalyticsOverview | null>(null);
  const [productivity,  setProductivity]  = useState<DeveloperProductivity | null>(null);
  const [insights,      setInsights]      = useState<DeveloperInsights | null>(null);
  const [trends,        setTrends]        = useState<DeveloperTrends | null>(null);
  const [workBreakdown, setWorkBreakdown] = useState<WorkBreakdown | null>(null);
  const [loading,       setLoading]       = useState(true);
  const [developerId,   setDeveloperId]   = useState<number | null>(null);
  const [analysisRunning, setAnalysisRunning] = useState(false);
  const [noProfile,     setNoProfile]     = useState(false);
  const [activeDim,     setActiveDim]     = useState<DimKey>('overall');

  useEffect(() => {
    if (!user) { router.push('/login'); return; }
    fetchData();
  }, [user]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const devsRes = await developersAPI.list();
      const myProfile = devsRes.data.find((d: any) => d.user_id === user?.id);
      if (!myProfile) { setNoProfile(true); setLoading(false); return; }
      setDeveloperId(myProfile.id);
      const [ovRes, prRes, inRes, trRes] = await Promise.allSettled([
        analyticsAPI.getOverview(myProfile.id),
        analyticsAPI.getProductivity(myProfile.id, { include_comparison: true }),
        analyticsAPI.getInsights(myProfile.id),
        analyticsAPI.getTrends(myProfile.id, 12),
      ]);
      if (ovRes.status === 'fulfilled') setOverview(ovRes.value.data);
      if (prRes.status === 'fulfilled') setProductivity(prRes.value.data);
      if (inRes.status === 'fulfilled') setInsights(inRes.value.data);
      if (trRes.status === 'fulfilled') setTrends(trRes.value.data);
      try { const wb = await analyticsAPI.getWorkBreakdown(myProfile.id); setWorkBreakdown(wb.data); } catch {}
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const handleLogout = () => { logout(); router.push('/login'); };

  const handleRunAnalysis = async () => {
    if (!developerId) return;
    if (!confirm('This will analyse your recent commits and tickets using your configured AI model.\n\nEstimated cost: ~$0.01 per 100 items\n\nContinue?')) return;
    try {
      setAnalysisRunning(true);
      const res = await analyticsAPI.triggerAnalysis(developerId, 50);
      alert(`Analysis started.\n\n${res.data.message}\n\nRefresh in 2–5 minutes to see updated scores.`);
    } catch (e: any) {
      alert(`Error: ${e.response?.data?.detail || 'Failed to trigger analysis'}`);
    } finally { setAnalysisRunning(false); }
  };

  // ── Derived data ─────────────────────────────────────────────────────────────
  const chartData = trends?.trends.map(t => ({
    period:   fmtPeriod(t.period_start),
    overall:  t.overall_score,
    quality:  Math.round(t.quality_score * 10),
    impact:   Math.round(t.impact_score  * 10),
    velocity: Math.round(t.velocity_score * 10),
  })) ?? [];

  const workData = (workBreakdown
    ? Object.entries(workBreakdown.work_type_distribution)
    : overview?.work_breakdown
    ? Object.entries(overview.work_breakdown)
    : []
  ).map(([n, v]) => ({ name: n.replace(/_/g, ' '), value: Math.round(v as number) }))
   .sort((a, b) => b.value - a.value);

  const dims = productivity?.score_breakdown
    ? Object.entries(productivity.score_breakdown).map(([k, v]) => ({
        key: k, label: k.charAt(0).toUpperCase() + k.slice(1), value: v,
        weight: productivity.evaluation_weights?.[k as keyof typeof productivity.evaluation_weights],
      }))
    : [];

  const trendDir    = trends?.trend_analysis?.trend_direction;
  const trendChange = trends?.trend_analysis?.change;

  // Period-over-period deltas for trend summary
  const latestPoint = chartData[chartData.length - 1];
  const prevPoint   = chartData[chartData.length - 2];

  const isManager = user?.role === 'manager' || user?.role === 'admin';
  const activeDimConfig = DIM_OPTIONS.find(d => d.key === activeDim)!;

  // ── Header ───────────────────────────────────────────────────────────────────
  const Header = () => (
    <header style={{
      position: 'sticky', top: 0, zIndex: 50, height: 52,
      background: 'rgba(10,10,10,0.9)',
      backdropFilter: 'blur(16px)',
      borderBottom: '1px solid var(--border-0)',
    }}>
      <div style={{ maxWidth: 1160, margin: '0 auto', padding: '0 24px', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{
            width: 28, height: 28, background: 'var(--cyan)', borderRadius: 6,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 10, fontWeight: 700, fontFamily: 'var(--font-mono)', color: '#0a0a0a',
          }}>DM</div>
          <span style={{ fontWeight: 600, fontSize: 14, color: 'var(--txt-1)', letterSpacing: '-0.01em' }}>DevMetrics</span>
          <div style={{ width: 1, height: 14, background: 'var(--border-1)' }} />
          <span style={{ fontSize: 11, color: 'var(--txt-3)' }}>{user?.full_name}</span>
          <span className="dm-tag" style={{ background: 'rgba(255,255,255,0.04)', color: 'var(--txt-3)', border: '1px solid var(--border-1)' }}>
            {user?.role}
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          {isManager && (
            <>
              <button className="dm-btn" onClick={() => router.push('/dashboard/manager')} style={{ fontSize: 11 }}>Team</button>
              <button
                className={`dm-btn ${!analysisRunning ? 'dm-btn-cyan' : ''}`}
                onClick={handleRunAnalysis}
                disabled={analysisRunning || !developerId}
                style={{ fontSize: 11 }}
              >
                {analysisRunning ? 'Analysing…' : 'Run Analysis'}
              </button>
            </>
          )}
          <button className="dm-btn" onClick={() => router.push('/dashboard/integrations')} style={{ fontSize: 11 }}>Integrations</button>
          <button className="dm-btn" onClick={() => router.push('/dashboard/settings')} style={{ fontSize: 11 }}>Settings</button>
          <button className="dm-btn" onClick={handleLogout} style={{ fontSize: 11, color: 'var(--txt-3)' }}>Sign out</button>
        </div>
      </div>
    </header>
  );

  // ── Loading ───────────────────────────────────────────────────────────────────
  if (loading) {
    return (
      <div style={{ minHeight: '100vh', background: 'var(--surf-0)' }}>
        <Header />
        <div style={{ maxWidth: 1160, margin: '0 auto', padding: '24px 24px' }}>
          <div className="dm-hero-grid"><Skeleton h={320} /><Skeleton h={320} /></div>
          <Skeleton h={240} />
          <div className="dm-two-col"><Skeleton h={180} /><Skeleton h={180} /></div>
        </div>
      </div>
    );
  }

  // ── No profile ────────────────────────────────────────────────────────────────
  if (noProfile) {
    return (
      <div style={{ minHeight: '100vh', background: 'var(--surf-0)' }}>
        <Header />
        <div style={{ maxWidth: 480, margin: '80px auto', padding: 24 }}>
          <div className="dm-card fade-up">
            <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 8 }}>No Developer Profile</h2>
            <p style={{ fontSize: 13, color: 'var(--txt-2)', lineHeight: 1.6 }}>Your account doesn&apos;t have a developer profile yet. Contact your administrator to create one.</p>
          </div>
        </div>
      </div>
    );
  }

  // ── No data ───────────────────────────────────────────────────────────────────
  if (!productivity) {
    return (
      <div style={{ minHeight: '100vh', background: 'var(--surf-0)' }}>
        <Header />
        <div style={{ maxWidth: 560, margin: '80px auto', padding: 24 }}>
          <div className="dm-card fade-up">
            <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 8 }}>No Analytics Yet</h2>
            <p style={{ fontSize: 13, color: 'var(--txt-2)', lineHeight: 1.6, marginBottom: 20 }}>
              Connect GitHub and Jira, sync data, then run AI analysis to populate your dashboard.
            </p>
            <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
              <button className="dm-btn dm-btn-cyan" onClick={() => router.push('/dashboard/integrations')} style={{ fontSize: 11 }}>
                Configure Integrations
              </button>
              {isManager && (
                <button className="dm-btn" onClick={handleRunAnalysis} disabled={analysisRunning || !developerId} style={{ fontSize: 11 }}>
                  {analysisRunning ? 'Analysing…' : 'Run Analysis'}
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ── Main ──────────────────────────────────────────────────────────────────────
  return (
    <div style={{ minHeight: '100vh', background: 'var(--surf-0)' }}>
      <Header />
      <main style={{ maxWidth: 1160, margin: '0 auto', padding: '24px 24px' }}>

        {/* ── Hero: Score + Dimensions ──────────────────────────────────────── */}
        <div className="dm-hero-grid">

          {/* Score panel */}
          <div className="dm-card fade-up fade-up-1" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16, justifyContent: 'center' }}>
            <div style={{ alignSelf: 'flex-start', width: '100%' }}>
              <div className="dm-label" style={{ marginBottom: 0 }}>Productivity Score</div>
            </div>

            <ScoreRing score={productivity.overall_score} />

            {/* Trend */}
            {trendDir && (
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={{
                  fontSize: 18, lineHeight: 1,
                  color: trendDir === 'improving' ? '#4ade80' : trendDir === 'declining' ? '#f87171' : 'var(--txt-2)',
                }}>
                  {trendDir === 'improving' ? '↑' : trendDir === 'declining' ? '↓' : '→'}
                </span>
                <div>
                  <div style={{ fontSize: 12, fontWeight: 500, textTransform: 'capitalize', color: trendDir === 'improving' ? '#4ade80' : trendDir === 'declining' ? '#f87171' : 'var(--txt-2)' }}>
                    {trendDir}
                  </div>
                  {trendChange !== undefined && (
                    <div className="mono" style={{ fontSize: 10, color: 'var(--txt-3)', marginTop: 1 }}>
                      {trendChange > 0 ? '+' : ''}{trendChange.toFixed(1)} pts
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* vs team */}
            {productivity.comparison_to_team && (
              <div style={{ width: '100%', background: 'rgba(255,255,255,0.025)', borderRadius: 8, padding: '11px 13px' }}>
                <div style={{ fontSize: 10, color: 'var(--txt-3)', marginBottom: 4, textTransform: 'uppercase', letterSpacing: '0.06em', fontFamily: 'var(--font-mono)' }}>vs Team Avg</div>
                <div className="mono" style={{
                  fontSize: 20, fontWeight: 700, lineHeight: 1,
                  color: productivity.comparison_to_team.overall.difference >= 0 ? '#4ade80' : '#f87171',
                }}>
                  {productivity.comparison_to_team.overall.difference >= 0 ? '+' : ''}
                  {productivity.comparison_to_team.overall.difference.toFixed(1)}
                </div>
                <div style={{ fontSize: 11, color: 'var(--txt-3)', marginTop: 3 }}>
                  Team avg: {productivity.comparison_to_team.overall.team_average.toFixed(1)}
                </div>
              </div>
            )}

            {/* Key drivers — score rationale */}
            {insights && insights.insights.length > 0 && (
              <div style={{ width: '100%', paddingTop: 14, borderTop: '1px solid rgba(255,255,255,0.05)' }}>
                <div style={{ fontSize: 10, color: 'var(--txt-3)', marginBottom: 9, textTransform: 'uppercase', letterSpacing: '0.06em', fontFamily: 'var(--font-mono)' }}>
                  Key Drivers
                </div>
                {insights.insights.slice(0, 3).map((ins, i) => (
                  <div key={i} style={{ display: 'flex', gap: 8, marginBottom: 6, alignItems: 'flex-start' }}>
                    <span style={{ fontSize: 10, color: 'var(--cyan)', flexShrink: 0, marginTop: 2 }}>›</span>
                    <span style={{ fontSize: 11, color: 'var(--txt-2)', lineHeight: 1.45 }}>{ins.title}</span>
                  </div>
                ))}
              </div>
            )}

            <div className="mono" style={{ fontSize: 9, color: 'var(--txt-3)', textAlign: 'center', lineHeight: 1.6 }}>
              {productivity.period_start}<br />→ {productivity.period_end}
            </div>
          </div>

          {/* Dimensions */}
          <div className="dm-card fade-up fade-up-2">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <span className="dm-label" style={{ marginBottom: 0 }}>Score Breakdown</span>
              <span style={{ fontSize: 9, color: 'var(--txt-3)', fontFamily: 'var(--font-mono)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>score / weight</span>
            </div>
            {dims.map((d, i) => (
              <DimRow key={d.key} label={d.label} value={d.value} weight={d.weight} delay={160 + i * 65} />
            ))}
          </div>
        </div>

        {/* ── Trends ───────────────────────────────────────────────────────── */}
        {chartData.length > 0 && (
          <div className="dm-card fade-up fade-up-3" style={{ marginBottom: 12 }}>

            {/* Header row */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 18, flexWrap: 'wrap', gap: 12 }}>
              <div>
                <span className="dm-label" style={{ marginBottom: 4 }}>Score Trend</span>
                <div style={{ fontSize: 13, color: 'var(--txt-2)' }}>
                  {chartData.length} periods
                </div>
              </div>

              {/* Dimension selector pills */}
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                {DIM_OPTIONS.map(d => (
                  <button
                    key={d.key}
                    onClick={() => setActiveDim(d.key)}
                    style={{
                      padding: '4px 12px', borderRadius: 20, cursor: 'pointer',
                      background: activeDim === d.key ? `${d.color}15` : 'transparent',
                      border: `1px solid ${activeDim === d.key ? d.color + '40' : 'rgba(255,255,255,0.07)'}`,
                      color: activeDim === d.key ? d.color : 'var(--txt-3)',
                      fontSize: 11, fontFamily: 'var(--font-body)',
                      transition: 'all 0.12s',
                    }}
                  >
                    {d.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Chart */}
            <ResponsiveContainer width="100%" height={190}>
              <LineChart data={chartData} margin={{ top: 4, right: 4, left: -24, bottom: 0 }}>
                <CartesianGrid strokeDasharray="2 8" stroke="rgba(255,255,255,0.03)" />
                <XAxis dataKey="period" tick={{ fontSize: 10, fill: '#52525b', fontFamily: 'var(--font-mono)' }} axisLine={false} tickLine={false} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: '#52525b', fontFamily: 'var(--font-mono)' }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{ background: '#111', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 8, fontSize: 11, fontFamily: 'var(--font-mono)', color: '#f4f4f5' }}
                  cursor={{ stroke: 'rgba(255,255,255,0.05)' }}
                />
                <Line
                  type="monotone"
                  dataKey={activeDim}
                  stroke={activeDimConfig.color}
                  strokeWidth={2}
                  dot={{ r: 3, fill: activeDimConfig.color, strokeWidth: 0 }}
                  activeDot={{ r: 5, strokeWidth: 0 }}
                  name={activeDimConfig.label}
                />
              </LineChart>
            </ResponsiveContainer>

            {/* Period-over-period delta row */}
            {latestPoint && prevPoint && (
              <div style={{ marginTop: 16, paddingTop: 16, borderTop: '1px solid rgba(255,255,255,0.04)', display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                {DIM_OPTIONS.map(d => {
                  const latest = latestPoint[d.key] as number;
                  const prev   = prevPoint[d.key] as number;
                  const delta  = latest - prev;
                  return (
                    <div key={d.key} style={{
                      flex: 1, minWidth: 80, padding: '8px 12px', borderRadius: 7,
                      background: 'rgba(255,255,255,0.025)', textAlign: 'center',
                    }}>
                      <div style={{ fontSize: 9, color: 'var(--txt-3)', marginBottom: 5, textTransform: 'uppercase', letterSpacing: '0.06em', fontFamily: 'var(--font-mono)' }}>
                        {d.label}
                      </div>
                      <div className="mono" style={{ fontSize: 15, fontWeight: 700, color: d.color }}>{latest}</div>
                      <div className="mono" style={{ fontSize: 9, color: delta >= 0 ? '#4ade80' : '#f87171', marginTop: 2 }}>
                        {delta >= 0 ? '+' : ''}{delta.toFixed(0)}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* ── Work + Activity ───────────────────────────────────────────────── */}
        <div className="dm-two-col">
          {workData.length > 0 && (
            <div className="dm-card fade-up fade-up-4">
              <span className="dm-label">Work Distribution</span>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 9 }}>
                {workData.slice(0, 8).map((item, i) => (
                  <div key={item.name}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                      <span style={{ fontSize: 12, color: 'var(--txt-2)', textTransform: 'capitalize' }}>{item.name}</span>
                      <span className="mono" style={{ fontSize: 12, fontWeight: 600, color: 'var(--txt-1)' }}>{item.value}%</span>
                    </div>
                    <div style={{ height: 3, background: 'rgba(255,255,255,0.04)', borderRadius: 2, overflow: 'hidden' }}>
                      <div style={{
                        height: '100%', borderRadius: 2,
                        background: WORK_COLORS[i % WORK_COLORS.length],
                        opacity: 0.75,
                        width: `${item.value}%`,
                        transition: 'width 1.1s cubic-bezier(0.16,1,0.3,1)',
                      }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {overview?.activity_summary && (
            <div className="dm-card fade-up fade-up-4">
              <span className="dm-label">Activity Summary</span>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 9 }}>
                <MiniStat label="Activities"     value={overview.activity_summary.total_activities} />
                <MiniStat label="Commits"        value={overview.activity_summary.total_commits} />
                <MiniStat label="Tickets"        value={overview.activity_summary.total_tickets} />
                <MiniStat label="Active Days"    value={overview.activity_summary.days_active} />
                <MiniStat label="Avg Complexity" value={overview.activity_summary.avg_complexity.toFixed(1)} />
                <MiniStat label="Avg Impact"     value={overview.activity_summary.avg_impact.toFixed(1)} />
              </div>
            </div>
          )}
        </div>

        {/* ── AI Insights ───────────────────────────────────────────────────── */}
        {insights && insights.insights.length > 0 && (
          <div className="dm-card fade-up" style={{ marginBottom: 12 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <span className="dm-label" style={{ marginBottom: 0 }}>AI Insights</span>
              <span className="dm-tag dm-tag-cyan">{insights.insights.length} generated</span>
            </div>
            {insights.insights.slice(0, 6).map((ins, i) => (
              <InsightCard key={i} insight={ins} />
            ))}

            {insights.anomalies?.length > 0 && (
              <div style={{ marginTop: 16, paddingTop: 16, borderTop: '1px solid var(--border-0)' }}>
                <span className="dm-label" style={{ color: 'var(--amber)', marginBottom: 10 }}>Anomalies</span>
                {insights.anomalies.map((a, i) => (
                  <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 10, padding: '7px 0', borderBottom: '1px solid rgba(255,255,255,0.03)' }}>
                    <span className="dm-tag" style={{
                      background: a.severity === 'high' ? 'var(--red-dim)' : 'var(--amber-dim)',
                      color: a.severity === 'high' ? 'var(--red)' : 'var(--amber)',
                      flexShrink: 0,
                    }}>
                      {a.severity}
                    </span>
                    <span style={{ fontSize: 12, color: 'var(--txt-2)' }}>{a.description}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

      </main>
    </div>
  );
}
