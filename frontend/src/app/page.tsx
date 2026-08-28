'use client';

import Link from 'next/link';

const SUPPORTING_FEATURES = [
  {
    title: 'Role-aware scoring',
    desc: 'A junior is never measured against a principal — six weighted dimensions, tuned per level.',
    accent: 'var(--cyan)',
  },
  {
    title: 'Your data stays with you',
    desc: 'Self-hosted by design. Real Docker Compose, real migrations, real CI — not a hosted black box.',
    accent: 'var(--red)',
  },
];

const STEPS = [
  { step: '1', title: 'Connect', desc: 'GitHub, Jira, Slack — minutes, not a rollout' },
  { step: '2', title: 'Sync', desc: 'Commits, tickets, and activity, automatically' },
  { step: '3', title: 'Analyze', desc: 'Every item scored by AI, never faked on failure' },
  { step: '4', title: 'See it', desc: 'Managers and developers see the same view' },
];

const ROADMAP = [
  { title: 'Mentoring network view', desc: 'Who reviews whom — how knowledge actually moves' },
  { title: '1:1 talking points', desc: 'Auto-generated from recent insights, before you walk in' },
  { title: 'Custom scoring weights', desc: 'Define what "impact" means for your team' },
];

function MiniBar({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div style={{ marginBottom: 8 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 3 }}>
        <span style={{ fontSize: 10, color: 'var(--txt-3)' }}>{label}</span>
        <span className="mono" style={{ fontSize: 10, color: 'var(--txt-2)' }}>{value.toFixed(1)}</span>
      </div>
      <div style={{ height: 4, borderRadius: 2, background: 'var(--surf-2)', overflow: 'hidden' }}>
        <div style={{ height: '100%', width: `${value * 10}%`, borderRadius: 2, background: color }} />
      </div>
    </div>
  );
}

function HeroMockup() {
  return (
    <div className="dm-browser-frame fade-up" style={{ maxWidth: 640, margin: '0 auto' }}>
      <div className="dm-browser-frame-bar">
        <span className="dm-browser-frame-dot" />
        <span className="dm-browser-frame-dot" />
        <span className="dm-browser-frame-dot" />
        <span className="mono" style={{ fontSize: 10, color: 'var(--txt-3)', marginLeft: 8 }}>app.devmetrics.ai/team</span>
      </div>
      <div style={{ padding: 22, textAlign: 'left' }}>
        <div className="dm-grid-3" style={{ marginBottom: 18 }}>
          {[
            { label: 'Team Size', value: '6', unit: 'devs' },
            { label: 'Avg Score', value: '74.2', unit: '/100' },
            { label: 'Avg Quality', value: '8.1', unit: '/10' },
          ].map(kpi => (
            <div key={kpi.label} className="dm-card" style={{ padding: '10px 12px' }}>
              <div className="dm-label" style={{ fontSize: 9, marginBottom: 2 }}>{kpi.label}</div>
              <div>
                <span className="mono" style={{ fontSize: 18, fontWeight: 700, color: 'var(--txt-1)' }}>{kpi.value}</span>
                <span className="mono" style={{ fontSize: 9, color: 'var(--txt-3)' }}> {kpi.unit}</span>
              </div>
            </div>
          ))}
        </div>
        <div className="dm-card" style={{ padding: 14, marginBottom: 10 }}>
          <MiniBar label="Complexity" value={8.6} color="var(--cyan)" />
          <MiniBar label="Impact" value={7.9} color="var(--green)" />
          <MiniBar label="Collaboration" value={6.4} color="var(--amber)" />
        </div>
        <div className="dm-card" style={{ padding: '10px 14px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <div style={{ width: 20, height: 20, borderRadius: '50%', background: 'var(--cyan-dim)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <span className="mono" style={{ fontSize: 9, color: 'var(--cyan)' }}>#1</span>
            </div>
            <span style={{ fontSize: 12, fontWeight: 500 }}>Priya Nair</span>
            <span className="dm-tag" style={{ background: 'var(--surf-2)', color: 'var(--txt-3)', fontFamily: 'var(--font-mono)' }}>SENIOR</span>
          </div>
          <span className="mono" style={{ fontSize: 13, fontWeight: 700, color: 'var(--green)' }}>91.4</span>
        </div>
      </div>
    </div>
  );
}

function AlertVisual() {
  const items = [
    { color: 'var(--red)', dim: 'var(--red-dim)', text: 'Collaboration dropped 40% this sprint' },
    { color: 'var(--amber)', dim: 'var(--amber-dim)', text: 'Only 2 active days out of 14' },
  ];
  return (
    <div className="dm-card" style={{ padding: 18 }}>
      {items.map((it, i) => (
        <div key={it.text} style={{
          display: 'flex', alignItems: 'center', gap: 10, padding: '10px 12px',
          borderRadius: 7, background: it.dim, marginBottom: i === items.length - 1 ? 0 : 8,
        }}>
          <div style={{ width: 6, height: 6, borderRadius: '50%', background: it.color, flexShrink: 0 }} />
          <span style={{ fontSize: 12, color: 'var(--txt-1)' }}>{it.text}</span>
        </div>
      ))}
    </div>
  );
}

function TopPerformerVisual() {
  const rows = [
    { name: 'Priya Nair', role: 'SENIOR', score: 91.4 },
    { name: 'Sam Okafor', role: 'MID', score: 84.0 },
  ];
  return (
    <div className="dm-card" style={{ padding: 18 }}>
      {rows.map((r, i) => (
        <div key={r.name} style={{
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          padding: '10px 4px', borderBottom: i === 0 ? '1px solid var(--border-0)' : 'none',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span className="mono" style={{ fontSize: 11, color: 'var(--txt-3)' }}>#{i + 1}</span>
            <span style={{ fontSize: 13, fontWeight: 500 }}>{r.name}</span>
            <span className="dm-tag" style={{ background: 'var(--surf-2)', color: 'var(--txt-3)', fontFamily: 'var(--font-mono)' }}>{r.role}</span>
          </div>
          <span className="mono" style={{ fontSize: 14, fontWeight: 700, color: 'var(--green)' }}>{r.score}</span>
        </div>
      ))}
    </div>
  );
}

export default function Home() {
  return (
    <div className="dm-bg-grid" style={{ minHeight: '100vh', background: 'var(--surf-0)', color: 'var(--txt-1)' }}>
      {/* Nav */}
      <header style={{
        position: 'sticky', top: 0, zIndex: 30,
        background: 'rgba(3,7,17,0.85)', backdropFilter: 'blur(16px)',
        borderBottom: '1px solid var(--border-0)',
        padding: '0 24px', height: 60,
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width: 30, height: 30, background: 'var(--cyan)', borderRadius: 7,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 11, fontWeight: 700, fontFamily: 'var(--font-mono)', color: '#0a0a0a',
          }}>DM</div>
          <span style={{ fontSize: 15, fontWeight: 600, letterSpacing: '-0.01em' }}>DevMetrics AI</span>
        </div>
        <nav style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Link href="/login" className="dm-btn" style={{ fontSize: 12 }}>Sign in</Link>
          <a href="mailto:hello@devmetrics.ai?subject=Custom%20quote" className="dm-btn dm-btn-cyan" style={{ fontSize: 12 }}>Talk to us</a>
        </nav>
      </header>

      <main style={{ maxWidth: 1080, margin: '0 auto', padding: '0 24px' }}>
        {/* Hero */}
        <section style={{ position: 'relative', textAlign: 'center', padding: '88px 0 0' }}>
          <div className="dm-hero-glow" />
          <div style={{ position: 'relative', zIndex: 1 }} className="fade-up">
            <div className="dm-tag" style={{
              background: 'var(--cyan-dim)', color: 'var(--cyan)',
              fontFamily: 'var(--font-mono)', letterSpacing: '0.06em', textTransform: 'uppercase',
              marginBottom: 22, fontSize: 10,
            }}>
              AI-Powered Engineering Intelligence
            </div>
            <h1 className="dm-hero-h1" style={{ fontWeight: 700, lineHeight: 1.05, letterSpacing: '-0.03em', marginBottom: 18 }}>
              Stop flying blind on
              <br />
              who&apos;s driving impact.
            </h1>
            <p style={{ fontSize: 17, color: 'var(--txt-2)', maxWidth: 540, margin: '0 auto 32px', lineHeight: 1.6 }}>
              Role-aware, AI-scored visibility across GitHub, Jira, and Slack —
              built for decisions, not surveillance.
            </p>
            <div style={{ display: 'flex', gap: 10, justifyContent: 'center', flexWrap: 'wrap', marginBottom: 56 }}>
              <a href="mailto:hello@devmetrics.ai?subject=Custom%20quote" className="dm-btn dm-btn-cyan" style={{ fontSize: 14, padding: '12px 22px' }}>
                Get a custom quote
              </a>
              <Link href="/register" className="dm-btn" style={{ fontSize: 14, padding: '12px 22px' }}>
                Try it yourself
              </Link>
            </div>
          </div>
          <div style={{ position: 'relative', zIndex: 1, marginBottom: 64 }}>
            <HeroMockup />
          </div>
        </section>

        {/* Big stats */}
        <section className="dm-grid-3 fade-up" style={{ marginBottom: 64, textAlign: 'center' }}>
          {[
            { num: '6', label: 'scoring dimensions, weighted by role' },
            { num: '3', label: 'integrations — GitHub, Jira, Slack' },
            { num: '100%', label: 'of scores visible to the developer too' },
          ].map(s => (
            <div key={s.label}>
              <div className="dm-stat-num" style={{ color: 'var(--cyan)' }}>{s.num}</div>
              <div style={{ fontSize: 12, color: 'var(--txt-3)', marginTop: 6 }}>{s.label}</div>
            </div>
          ))}
        </section>

        {/* Integration row */}
        <section style={{ marginBottom: 88 }} className="fade-up">
          <div className="dm-label" style={{ textAlign: 'center', marginBottom: 16 }}>Works with the tools you already use</div>
          <div className="dm-integration-row">
            {['GitHub', 'Jira', 'Slack'].map(name => (
              <span key={name} className="mono" style={{ fontSize: 15, fontWeight: 600, color: 'var(--txt-2)' }}>{name}</span>
            ))}
          </div>
        </section>

        {/* Full-width alternating features */}
        <section style={{ marginBottom: 24 }} className="fade-up">
          <div className="dm-two-col" style={{ alignItems: 'center', marginBottom: 56 }}>
            <div>
              <div className="dm-label">For managers</div>
              <h2 style={{ fontSize: 26, fontWeight: 700, letterSpacing: '-0.01em', marginBottom: 10 }}>
                Learn from your top performers
              </h2>
              <p style={{ fontSize: 14, color: 'var(--txt-2)', lineHeight: 1.6 }}>
                Not just a leaderboard — the patterns behind the strongest work,
                surfaced so the rest of the team can pick them up.
              </p>
            </div>
            <TopPerformerVisual />
          </div>

          <div className="dm-two-col" style={{ alignItems: 'center', marginBottom: 56 }}>
            <div style={{ order: 2 }}>
              <div className="dm-label">Before it&apos;s a resignation</div>
              <h2 style={{ fontSize: 26, fontWeight: 700, letterSpacing: '-0.01em', marginBottom: 10 }}>
                Catch bottlenecks and burnout early
              </h2>
              <p style={{ fontSize: 14, color: 'var(--txt-2)', lineHeight: 1.6 }}>
                AI-generated anomaly detection flags unusual drops in activity,
                one-sided workload, and collaboration gaps — automatically.
              </p>
            </div>
            <div style={{ order: 1 }}>
              <AlertVisual />
            </div>
          </div>
        </section>

        {/* Supporting features, compact */}
        <section className="dm-grid-2 fade-up" style={{ marginBottom: 72 }}>
          {SUPPORTING_FEATURES.map(f => (
            <div key={f.title} className="dm-card dm-card-hover" style={{ padding: '20px 22px' }}>
              <div style={{ width: 8, height: 8, borderRadius: 2, background: f.accent, marginBottom: 14 }} />
              <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 6, letterSpacing: '-0.01em' }}>{f.title}</h3>
              <p style={{ fontSize: 12, color: 'var(--txt-3)', lineHeight: 1.55 }}>{f.desc}</p>
            </div>
          ))}
        </section>

        {/* Transparency callout */}
        <section className="dm-card fade-up" style={{ padding: '32px 36px', marginBottom: 72, textAlign: 'center' }}>
          <div className="dm-label" style={{ marginBottom: 10, textAlign: 'center' }}>Built on trust, not surveillance</div>
          <p style={{ fontSize: 19, fontWeight: 600, lineHeight: 1.5, maxWidth: 600, margin: '0 auto', letterSpacing: '-0.01em' }}>
            Developers see the exact same scores their managers do.
            <span style={{ color: 'var(--txt-2)', fontWeight: 400 }}> No hidden dashboards, no backroom scorekeeping.</span>
          </p>
        </section>

        {/* How it works */}
        <section style={{ marginBottom: 72 }} className="fade-up">
          <h2 style={{ fontSize: 22, fontWeight: 700, textAlign: 'center', marginBottom: 24, letterSpacing: '-0.01em' }}>How it works</h2>
          <div className="dm-grid-4">
            {STEPS.map(s => (
              <div key={s.step} className="dm-card dm-card-hover" style={{ padding: '18px 16px' }}>
                <div style={{
                  width: 26, height: 26, borderRadius: 7, background: 'var(--cyan-dim)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 12,
                }}>
                  <span className="mono" style={{ color: 'var(--cyan)', fontWeight: 700, fontSize: 11 }}>{s.step}</span>
                </div>
                <h3 style={{ fontSize: 13, fontWeight: 600, marginBottom: 4 }}>{s.title}</h3>
                <p style={{ fontSize: 11, color: 'var(--txt-3)', lineHeight: 1.5 }}>{s.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Roadmap teaser */}
        <section style={{ marginBottom: 72 }} className="fade-up">
          <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', marginBottom: 16 }}>
            <h2 style={{ fontSize: 18, fontWeight: 700, letterSpacing: '-0.01em' }}>What&apos;s next</h2>
            <span className="dm-label" style={{ marginBottom: 0 }}>Roadmap</span>
          </div>
          <div className="dm-grid-3">
            {ROADMAP.map(r => (
              <div key={r.title} className="dm-card" style={{ padding: '16px 18px', borderStyle: 'dashed' }}>
                <h3 style={{ fontSize: 12, fontWeight: 600, marginBottom: 5, color: 'var(--txt-2)' }}>{r.title}</h3>
                <p style={{ fontSize: 11, color: 'var(--txt-3)', lineHeight: 1.5 }}>{r.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Closing CTA */}
        <section className="dm-card fade-up" style={{
          padding: '44px 36px', marginBottom: 56, textAlign: 'center',
          background: 'linear-gradient(180deg, var(--surf-1), var(--surf-2))',
        }}>
          <h2 style={{ fontSize: 24, fontWeight: 700, marginBottom: 10, letterSpacing: '-0.01em' }}>
            Every org measures engineering differently
          </h2>
          <p style={{ fontSize: 13, color: 'var(--txt-2)', maxWidth: 460, margin: '0 auto 22px', lineHeight: 1.6 }}>
            We deploy inside your own environment and tune it to how your team works.
            Tell us about your setup and we&apos;ll put together a quote.
          </p>
          <a href="mailto:hello@devmetrics.ai?subject=Custom%20quote" className="dm-btn dm-btn-cyan" style={{ fontSize: 14, padding: '12px 24px' }}>
            Request a custom quote
          </a>
        </section>

        <footer style={{ textAlign: 'center', padding: '0 0 48px' }}>
          <p style={{ fontSize: 12, color: 'var(--txt-3)' }}>DevMetrics AI — Engineering Intelligence Platform</p>
        </footer>
      </main>
    </div>
  );
}
