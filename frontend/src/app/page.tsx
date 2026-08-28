'use client';

import Link from 'next/link';

const FEATURES = [
  {
    title: 'See who\'s actually moving the needle',
    desc: 'Multi-dimensional AI scoring — complexity, velocity, quality, impact, collaboration, mentoring — weighted by role, so a junior is never measured against a principal.',
    accent: 'var(--cyan)',
  },
  {
    title: 'Learn from your top performers',
    desc: 'Surface the patterns behind your strongest work — not just a leaderboard, but what specifically is working, so the rest of the team can pick it up.',
    accent: 'var(--green)',
  },
  {
    title: 'Catch bottlenecks and burnout early',
    desc: 'AI-generated anomaly detection flags unusual drops in activity, one-sided workload, and collaboration gaps before they become a resignation.',
    accent: 'var(--amber)',
  },
  {
    title: 'Your data never leaves your environment',
    desc: 'Self-hosted by design — real Docker Compose, real migrations, real CI. Deploy inside your own infrastructure instead of pooling your codebase into someone else\'s SaaS.',
    accent: 'var(--red)',
  },
];

const STEPS = [
  { step: '1', title: 'Connect your tools', desc: 'Link GitHub, Jira, and Slack — takes minutes, not a rollout project' },
  { step: '2', title: 'Sync your data', desc: 'Commits, PRs, reviews, tickets, and team activity pulled automatically' },
  { step: '3', title: 'AI analysis', desc: 'Every item is scored by AI — never a hardcoded fallback masquerading as insight' },
  { step: '4', title: 'Everyone sees it', desc: 'Managers get visibility, developers see the same view — not a surveillance tool' },
];

const ROADMAP = [
  { title: 'Mentoring network view', desc: 'Who reviews whom — a relationship graph of how knowledge actually moves through your team' },
  { title: '1:1 talking points', desc: 'Auto-generated from recent AI insights, ready before you walk into the room' },
  { title: 'Custom scoring weights', desc: 'Define what "impact" means for your team — every org measures engineering differently' },
];

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
        <section style={{ textAlign: 'center', padding: '96px 0 72px' }} className="fade-up">
          <div className="dm-tag" style={{
            background: 'var(--cyan-dim)', color: 'var(--cyan)',
            fontFamily: 'var(--font-mono)', letterSpacing: '0.06em', textTransform: 'uppercase',
            marginBottom: 24, fontSize: 10,
          }}>
            AI-Powered Engineering Intelligence
          </div>
          <h1 className="dm-hero-h1" style={{ fontWeight: 700, lineHeight: 1.1, letterSpacing: '-0.02em', marginBottom: 20 }}>
            Stop flying blind on
            <br />
            who&apos;s actually driving impact.
          </h1>
          <p style={{ fontSize: 18, color: 'var(--txt-2)', maxWidth: 620, margin: '0 auto 36px', lineHeight: 1.6 }}>
            DevMetrics AI turns GitHub, Jira, and Slack activity into role-aware, AI-scored
            visibility — so managers can make decisions with real signal, and teams can learn
            from what&apos;s actually working.
          </p>
          <div style={{ display: 'flex', gap: 10, justifyContent: 'center', flexWrap: 'wrap' }}>
            <a href="mailto:hello@devmetrics.ai?subject=Custom%20quote" className="dm-btn dm-btn-cyan" style={{ fontSize: 14, padding: '12px 22px' }}>
              Get a custom quote
            </a>
            <Link href="/register" className="dm-btn" style={{ fontSize: 14, padding: '12px 22px' }}>
              Try it yourself
            </Link>
          </div>
        </section>

        {/* Features */}
        <section className="dm-grid-2 fade-up" style={{ marginBottom: 72 }}>
          {FEATURES.map(f => (
            <div key={f.title} className="dm-card" style={{ padding: '24px 26px' }}>
              <div style={{ width: 8, height: 8, borderRadius: 2, background: f.accent, marginBottom: 16 }} />
              <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 8, letterSpacing: '-0.01em' }}>{f.title}</h3>
              <p style={{ fontSize: 13, color: 'var(--txt-2)', lineHeight: 1.6 }}>{f.desc}</p>
            </div>
          ))}
        </section>

        {/* Transparency callout */}
        <section className="dm-card fade-up" style={{ padding: '32px 36px', marginBottom: 72, textAlign: 'center' }}>
          <div className="dm-label" style={{ marginBottom: 10 }}>Built on trust, not surveillance</div>
          <p style={{ fontSize: 20, fontWeight: 600, lineHeight: 1.5, maxWidth: 640, margin: '0 auto', letterSpacing: '-0.01em' }}>
            Developers see the exact same scores and insights their managers do.
            <span style={{ color: 'var(--txt-2)', fontWeight: 400 }}> No hidden dashboards, no backroom scorekeeping — visibility that runs in both directions.</span>
          </p>
        </section>

        {/* How it works */}
        <section style={{ marginBottom: 72 }} className="fade-up">
          <h2 style={{ fontSize: 24, fontWeight: 700, textAlign: 'center', marginBottom: 28, letterSpacing: '-0.01em' }}>How it works</h2>
          <div className="dm-grid-4">
            {STEPS.map(s => (
              <div key={s.step} className="dm-card" style={{ padding: '20px 18px' }}>
                <div style={{
                  width: 28, height: 28, borderRadius: 7, background: 'var(--cyan-dim)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 14,
                }}>
                  <span className="mono" style={{ color: 'var(--cyan)', fontWeight: 700, fontSize: 12 }}>{s.step}</span>
                </div>
                <h3 style={{ fontSize: 13, fontWeight: 600, marginBottom: 6 }}>{s.title}</h3>
                <p style={{ fontSize: 12, color: 'var(--txt-3)', lineHeight: 1.5 }}>{s.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Roadmap teaser */}
        <section style={{ marginBottom: 72 }} className="fade-up">
          <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', marginBottom: 16 }}>
            <h2 style={{ fontSize: 20, fontWeight: 700, letterSpacing: '-0.01em' }}>What&apos;s next</h2>
            <span className="dm-label" style={{ marginBottom: 0 }}>Roadmap</span>
          </div>
          <div className="dm-grid-3">
            {ROADMAP.map(r => (
              <div key={r.title} className="dm-card" style={{ padding: '18px 20px', borderStyle: 'dashed' }}>
                <h3 style={{ fontSize: 13, fontWeight: 600, marginBottom: 6, color: 'var(--txt-2)' }}>{r.title}</h3>
                <p style={{ fontSize: 12, color: 'var(--txt-3)', lineHeight: 1.5 }}>{r.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Closing CTA */}
        <section className="dm-card fade-up" style={{
          padding: '44px 36px', marginBottom: 56, textAlign: 'center',
          background: 'linear-gradient(180deg, var(--surf-1), var(--surf-2))',
        }}>
          <h2 style={{ fontSize: 26, fontWeight: 700, marginBottom: 10, letterSpacing: '-0.01em' }}>
            Every org measures engineering differently
          </h2>
          <p style={{ fontSize: 14, color: 'var(--txt-2)', maxWidth: 480, margin: '0 auto 24px', lineHeight: 1.6 }}>
            We deploy DevMetrics AI inside your own environment and tune it to how your
            team actually works. Tell us about your setup and we&apos;ll put together a quote.
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
