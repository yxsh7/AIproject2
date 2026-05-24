'use client';

import { useRouter } from 'next/navigation';
import { useAuthStore } from '../store/auth';
import { motion } from 'framer-motion';
import {
  Brain,
  BarChart3,
  GitBranch,
  Users,
  PieChart,
  Lightbulb,
  ClipboardList,
  Play,
  ArrowRight,
  Shield,
  Server,
  Lock,
  Cpu,
  TrendingUp,
  AlertTriangle,
  Activity,
  GitPullRequest,
  TicketIcon,
  Calendar,
  Check,
} from 'lucide-react';

const fadeIn = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.55, ease: 'easeOut' } },
};

// ── Navbar ───────────────────────────────────────────────────────────────────

function LandingNavbar() {
  const router = useRouter();
  const { token } = useAuthStore();

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 border-b border-white/[0.06] backdrop-blur-md bg-[#07090e]/75">
      <div className="max-w-7xl mx-auto px-6 lg:px-8 h-13 flex items-center justify-between" style={{ height: 52 }}>
        <div className="flex items-center gap-2.5">
          <div className="w-6 h-6 rounded bg-sky-500 flex items-center justify-center">
            <BarChart3 className="w-3.5 h-3.5 text-white" />
          </div>
          <span className="text-[15px] font-semibold text-white">DevMetrics AI</span>
        </div>

        <div className="flex items-center gap-6">
          <a href="#how-it-works" className="hidden sm:block text-sm text-white/40 hover:text-white/80 transition-colors">How it works</a>
          <a href="#demo" className="hidden sm:block text-sm text-white/40 hover:text-white/80 transition-colors">Demo</a>
          {token ? (
            <button
              onClick={() => router.push('/dashboard')}
              className="text-sm px-3.5 py-1.5 rounded bg-sky-500 hover:bg-sky-400 text-white transition-colors font-medium"
            >
              Dashboard
            </button>
          ) : (
            <a href="#contact" className="text-sm px-3.5 py-1.5 rounded bg-sky-500 hover:bg-sky-400 text-white transition-colors font-medium">
              Request Access
            </a>
          )}
        </div>
      </div>
    </nav>
  );
}

// ── Mock Dashboard ────────────────────────────────────────────────────────────

const dimensions = [
  { label: 'Code Quality',    val: 8.7, pct: 87, color: '#22d3ee' },
  { label: 'Business Impact', val: 9.1, pct: 91, color: '#34d399' },
  { label: 'Velocity',        val: 7.3, pct: 73, color: '#f97316' },
  { label: 'Collaboration',   val: 8.9, pct: 89, color: '#818cf8' },
];

const activityStats = [
  { icon: Activity,       label: 'Commits',    val: '24' },
  { icon: GitPullRequest, label: 'PRs Merged', val: '7'  },
  { icon: TicketIcon,     label: 'Tickets',    val: '11' },
  { icon: Calendar,       label: 'Active Days',val: '14' },
];

function MockDashboard() {
  return (
    <div className="pointer-events-none select-none w-full">
      <div className="rounded-xl overflow-hidden border border-white/[0.09] shadow-[0_40px_100px_rgba(0,0,0,0.85)]">

        {/* Browser chrome */}
        <div className="bg-[#0d1017] px-4 py-2.5 flex items-center gap-3 border-b border-white/[0.06]">
          <div className="flex gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-[#ff5f57]" />
            <div className="w-2.5 h-2.5 rounded-full bg-[#febc2e]" />
            <div className="w-2.5 h-2.5 rounded-full bg-[#28c840]" />
          </div>
          <div className="flex-1 bg-white/[0.04] rounded px-3 py-0.5 text-[11px] text-white/20 font-mono">
            app.devmetrics.ai/dashboard
          </div>
        </div>

        {/* Content */}
        <div className="bg-[#080b11] px-5 py-4 space-y-3">

          {/* Header */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded bg-sky-500 flex items-center justify-center">
                <BarChart3 className="w-3 h-3 text-white" />
              </div>
              <div>
                <div className="text-[12px] font-semibold text-white leading-tight">DevMetrics AI</div>
                <div className="text-[10px] text-white/30">Alex Chen · Software Engineer</div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] text-white/25 border border-white/[0.08] rounded px-2 py-0.5">Last 30 days</span>
              <span className="text-[10px] text-sky-400 bg-sky-500/10 border border-sky-500/25 rounded px-2 py-0.5">▶ Run Analysis</span>
            </div>
          </div>

          {/* Score + breakdown */}
          <div className="grid grid-cols-5 gap-3">

            {/* Big score */}
            <div className="col-span-2 p-4 rounded-lg bg-white/[0.03] border border-white/[0.06]">
              <div className="text-[10px] text-white/30 uppercase tracking-wider mb-2">Overall Score</div>
              <div className="text-[44px] font-bold leading-none text-white tabular-nums">78.4</div>
              <div className="text-[10px] text-white/25 mt-0.5">out of 100</div>
              <div className="mt-4 space-y-1.5">
                <div className="flex items-center gap-1.5 text-[10px] font-semibold text-emerald-400">
                  <TrendingUp className="w-3 h-3" /> Improving
                </div>
                <div className="text-[10px] text-white/30">+4.2 pts vs last period</div>
                <div className="text-[10px] text-sky-400 mt-2">Top 18% of team</div>
              </div>
            </div>

            {/* Dimension bars */}
            <div className="col-span-3 p-4 rounded-lg bg-white/[0.03] border border-white/[0.06]">
              <div className="text-[10px] text-white/30 uppercase tracking-wider mb-3">Score Breakdown</div>
              <div className="space-y-3">
                {dimensions.map((d) => (
                  <div key={d.label}>
                    <div className="flex justify-between mb-1">
                      <span className="text-[10px] text-white/45">{d.label}</span>
                      <span className="text-[10px] font-semibold text-white tabular-nums">{d.val}</span>
                    </div>
                    <div className="h-1.5 bg-white/[0.06] rounded-full overflow-hidden">
                      <div className="h-full rounded-full" style={{ width: `${d.pct}%`, background: d.color, opacity: 0.8 }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* AI Insights */}
          <div className="grid grid-cols-2 gap-3">
            <div className="p-3.5 rounded-lg bg-emerald-500/[0.04] border border-emerald-500/20">
              <div className="flex items-center gap-1.5 mb-2">
                <div className="w-4.5 h-4.5 flex items-center justify-center" style={{ width: 18, height: 18 }}>
                  <Brain className="w-3.5 h-3.5 text-emerald-400" />
                </div>
                <span className="text-[9px] font-bold tracking-widest text-emerald-400 uppercase">Strength</span>
                <span className="ml-auto text-[9px] text-white/20">94% conf.</span>
              </div>
              <div className="text-[11px] font-semibold text-white/85 mb-1">PR Review Quality</div>
              <div className="text-[10px] text-white/35 leading-relaxed">
                Substantive feedback on complex PRs — 94% approval rate, up 22% this month.
              </div>
            </div>

            <div className="p-3.5 rounded-lg bg-amber-500/[0.04] border border-amber-500/20">
              <div className="flex items-center gap-1.5 mb-2">
                <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                <span className="text-[9px] font-bold tracking-widest text-amber-400 uppercase">Watch</span>
                <span className="ml-auto text-[9px] text-white/20">88% conf.</span>
              </div>
              <div className="text-[11px] font-semibold text-white/85 mb-1">Commit Size Trend</div>
              <div className="text-[10px] text-white/35 leading-relaxed">
                Avg diff size +180% vs baseline — atomic commits will improve review velocity.
              </div>
            </div>
          </div>

          {/* Activity strip */}
          <div className="grid grid-cols-4 gap-2">
            {activityStats.map((s) => (
              <div key={s.label} className="p-2.5 rounded-lg bg-white/[0.02] border border-white/[0.05] text-center">
                <s.icon className="w-3 h-3 text-white/20 mx-auto mb-1" />
                <div className="text-[16px] font-bold text-white leading-tight">{s.val}</div>
                <div className="text-[9px] text-white/25 mt-0.5">{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// ── Hero ─────────────────────────────────────────────────────────────────────

function HeroSection() {
  const router = useRouter();
  const { token } = useAuthStore();

  return (
    <section className="pt-28 pb-20 px-6 lg:px-8">
      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">

        {/* Left: copy */}
        <motion.div initial="hidden" animate="visible" variants={{ hidden: {}, visible: { transition: { staggerChildren: 0.1 } } }}>
          <motion.p variants={fadeIn} className="text-sm text-sky-400 font-medium mb-5 tracking-wide">
            Engineering Intelligence Platform
          </motion.p>

          <motion.h1 variants={fadeIn} className="text-[2.6rem] sm:text-5xl font-bold text-white leading-[1.1] tracking-tight mb-6">
            Understand what your<br />
            engineers <span className="text-sky-300">actually do</span>
          </motion.h1>

          <motion.p variants={fadeIn} className="text-[17px] text-white/45 leading-relaxed mb-10 max-w-md">
            Connect your repositories and issue tracker. Our AI pipeline analyzes every commit and
            ticket to produce multi-dimensional productivity scores — running entirely on your
            own infrastructure.
          </motion.p>

          <motion.div variants={fadeIn} className="flex items-center gap-3 flex-wrap">
            {token ? (
              <button
                onClick={() => router.push('/dashboard')}
                className="flex items-center gap-2 px-5 py-2.5 rounded bg-sky-500 hover:bg-sky-400 text-white font-medium text-sm transition-colors"
              >
                Go to Dashboard <ArrowRight className="w-4 h-4" />
              </button>
            ) : (
              <>
                <a href="#contact" className="flex items-center gap-2 px-5 py-2.5 rounded bg-sky-500 hover:bg-sky-400 text-white font-medium text-sm transition-colors">
                  Request Access <ArrowRight className="w-4 h-4" />
                </a>
                <button
                  onClick={() => router.push('/login')}
                  className="px-5 py-2.5 rounded border border-white/[0.12] hover:border-white/25 text-white/60 hover:text-white text-sm transition-all"
                >
                  Sign In
                </button>
              </>
            )}
            <a href="#demo" className="flex items-center gap-2 text-sm text-white/30 hover:text-white/60 transition-colors ml-1">
              <Play className="w-3.5 h-3.5" /> Watch Demo
            </a>
          </motion.div>
        </motion.div>

        {/* Right: dashboard */}
        <motion.div
          initial={{ opacity: 0, y: 32 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.3, ease: 'easeOut' }}
        >
          <MockDashboard />
        </motion.div>
      </div>
    </section>
  );
}

// ── Features ─────────────────────────────────────────────────────────────────

const features = [
  { icon: Brain,     title: 'Deep AI Analysis',        description: 'A multi-stage AI pipeline examines every commit and ticket for nuanced productivity signals — far beyond commit counts or story points.' },
  { icon: BarChart3, title: 'Multi-Dimensional Scores', description: 'Six axes — quality, impact, velocity, collaboration, reliability, growth — weighted by role and seniority. Every number has reasoning behind it.' },
  { icon: GitBranch, title: 'Source Control Integration', description: 'Connect any Git repository. Commits, pull requests, and diffs are ingested automatically via secure OAuth. No manual uploads.' },
  { icon: Users,     title: 'Team Manager View',       description: 'Compare developers side-by-side with trend lines, percentile ranks, and anomaly detection. Designed for 1:1s and performance reviews.' },
  { icon: PieChart,  title: 'Work Distribution',       description: 'See the split between features, bug fixes, tech debt, and documentation — at the individual or team level, per sprint or quarter.' },
  { icon: Lightbulb, title: 'Actionable Insights',     description: 'Every score surfaces AI-generated recommendations with a confidence rating. Not just what changed, but what to do about it.' },
];

function FeaturesSection() {
  return (
    <section className="py-24 px-6 lg:px-8 border-t border-white/[0.05]">
      <div className="max-w-7xl mx-auto">
        <motion.div initial="hidden" whileInView="visible" viewport={{ once: true, margin: '-60px' }} variants={fadeIn}>
          <div className="flex items-baseline justify-between mb-12">
            <h2 className="text-2xl sm:text-3xl font-bold text-white">What DevMetrics measures</h2>
            <span className="text-sm text-white/25 hidden sm:block">6 dimensions</span>
          </div>

          <div className="divide-y divide-white/[0.05]">
            {features.map((f, i) => (
              <motion.div
                key={f.title}
                initial={{ opacity: 0 }}
                whileInView={{ opacity: 1 }}
                viewport={{ once: true, margin: '-40px' }}
                transition={{ duration: 0.4, delay: i * 0.04 }}
                className="grid grid-cols-1 md:grid-cols-3 gap-3 md:gap-8 py-7 group"
              >
                <div className="flex items-start gap-4">
                  <span className="text-[11px] font-mono text-white/20 mt-1 w-5 flex-shrink-0 tabular-nums">
                    {String(i + 1).padStart(2, '0')}
                  </span>
                  <f.icon className="w-4 h-4 text-white/35 mt-0.5 flex-shrink-0" />
                  <span className="text-[15px] font-semibold text-white">{f.title}</span>
                </div>
                <div className="md:col-span-2 pl-9 md:pl-0">
                  <p className="text-sm text-white/40 leading-relaxed">{f.description}</p>
                </div>
              </motion.div>
            ))}
          </div>
          <div className="border-t border-white/[0.05]" />
        </motion.div>
      </div>
    </section>
  );
}

// ── How It Works ──────────────────────────────────────────────────────────────

function HowItWorksSection() {
  const steps = [
    { n: '01', title: 'Connect', body: 'Link your source control and issue tracker via secure OAuth. Credentials stay on your servers — nothing touches our infrastructure.' },
    { n: '02', title: 'Analyze', body: 'An asynchronous AI pipeline processes your activity data on your own machines, using whatever AI model you choose — cloud or fully local.' },
    { n: '03', title: 'Insights', body: 'Multi-dimensional scores, trend charts, and typed recommendations appear on the dashboard. Drill into any score to see the underlying evidence.' },
  ];

  return (
    <section id="how-it-works" className="py-24 px-6 lg:px-8 border-t border-white/[0.05]">
      <div className="max-w-7xl mx-auto">
        <motion.div initial="hidden" whileInView="visible" viewport={{ once: true, margin: '-60px' }} variants={fadeIn}>
          <h2 className="text-2xl sm:text-3xl font-bold text-white mb-16">Three steps to production insights</h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
            {steps.map((s) => (
              <div key={s.n}>
                <div className="text-[48px] font-bold text-white/[0.18] font-mono leading-none mb-5 tabular-nums">{s.n}</div>
                <h3 className="text-lg font-semibold text-white mb-3">{s.title}</h3>
                <p className="text-sm text-white/40 leading-relaxed">{s.body}</p>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
}

// ── Data Sovereignty ──────────────────────────────────────────────────────────

const sovereigntyPoints = [
  { icon: Server, title: 'Runs on your infrastructure', body: 'Self-hosted by design. DevMetrics runs on servers you control — your cloud account, your hardware, your rules.' },
  { icon: Lock,   title: 'Source code never transmitted', body: 'Commit diffs and ticket contents are analyzed locally. Nothing is forwarded to a third-party service.' },
  { icon: Cpu,    title: 'Model-agnostic AI', body: 'Plug in any AI model — a local instance, an open-source model, or a cloud provider of your choice. Swap at any time.' },
  { icon: Shield, title: 'Full air-gap option', body: 'Run with a locally-hosted model for a completely offline deployment. Sensitive codebases never leave the building.' },
];

function DataSovereigntySection() {
  return (
    <section className="py-24 px-6 lg:px-8 border-t border-white/[0.05]">
      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-16">

        {/* Statement */}
        <motion.div initial="hidden" whileInView="visible" viewport={{ once: true, margin: '-60px' }} variants={fadeIn}>
          <div className="text-xs text-emerald-400 font-semibold tracking-widest uppercase mb-6">Data Sovereignty</div>
          <h2 className="text-3xl sm:text-4xl font-bold text-white leading-tight mb-6">
            Your source code<br />never leaves<br />your servers.
          </h2>
          <p className="text-[17px] text-white/40 leading-relaxed">
            Most analytics tools ship your data to their cloud for processing. DevMetrics runs
            on infrastructure you own, with a model you choose. You keep complete control.
          </p>
        </motion.div>

        {/* Points */}
        <motion.div
          className="space-y-8"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-60px' }}
          variants={{ hidden: {}, visible: { transition: { staggerChildren: 0.08 } } }}
        >
          {sovereigntyPoints.map((p) => (
            <motion.div key={p.title} variants={fadeIn} className="flex gap-4">
              <p.icon className="w-4.5 h-4.5 text-emerald-400 mt-0.5 flex-shrink-0" style={{ width: 18, height: 18 }} />
              <div>
                <div className="text-[15px] font-semibold text-white mb-1">{p.title}</div>
                <div className="text-sm text-white/40 leading-relaxed">{p.body}</div>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}

// ── AI Pipeline ───────────────────────────────────────────────────────────────

const agentNodes = [
  { icon: Brain,         label: 'Intent Classifier',  color: '#0ea5e9' },
  { icon: GitBranch,     label: 'Commit Analyzer',    color: '#06b6d4' },
  { icon: ClipboardList, label: 'Ticket Parser',      color: '#14b8a6' },
  { icon: BarChart3,     label: 'Score Engine',       color: '#10b981' },
  { icon: Lightbulb,     label: 'Insight Generator',  color: '#34d399' },
];

const pipelinePoints = [
  'Multi-agent architecture: intent classification → code analysis → scoring → insights',
  'Processes full commit diffs with surrounding context, not just commit messages',
  'Structured output with typed confidence scores — no black-box results',
  'Asynchronous workers keep the UI responsive during analysis',
  'Deterministic scoring: same input always produces the same output',
];

function AIShowcaseSection() {
  return (
    <section className="py-24 px-6 lg:px-8 border-t border-white/[0.05]">
      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-16 items-start">

        <motion.div initial="hidden" whileInView="visible" viewport={{ once: true, margin: '-60px' }} variants={fadeIn}>
          <div className="text-xs text-sky-400 font-semibold tracking-widest uppercase mb-6">AI Pipeline</div>
          <h2 className="text-3xl font-bold text-white mb-8">
            A structured pipeline — not a prompt and a prayer
          </h2>
          <ul className="space-y-5">
            {pipelinePoints.map((item) => (
              <li key={item} className="flex items-start gap-3">
                <Check className="w-4 h-4 text-sky-400 mt-0.5 flex-shrink-0" />
                <span className="text-sm text-white/50 leading-relaxed">{item}</span>
              </li>
            ))}
          </ul>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 16 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true, margin: '-60px' }}
          transition={{ duration: 0.5 }}
          className="space-y-2"
        >
          {agentNodes.map((node, i) => (
            <div key={node.label}>
              <div className="flex items-center gap-3.5 px-4 py-3.5 rounded-lg border border-white/[0.06] bg-white/[0.02] hover:bg-white/[0.04] transition-colors">
                <div className="w-7 h-7 rounded flex items-center justify-center flex-shrink-0" style={{ background: node.color + '1a', border: `1px solid ${node.color}30` }}>
                  <node.icon className="w-3.5 h-3.5" style={{ color: node.color }} />
                </div>
                <span className="text-sm text-white/65 font-medium">{node.label}</span>
                <motion.div
                  className="ml-auto w-1.5 h-1.5 rounded-full"
                  style={{ background: node.color }}
                  animate={{ opacity: [0.2, 1, 0.2] }}
                  transition={{ repeat: Infinity, duration: 2.4, delay: i * 0.45 }}
                />
              </div>
              {i < agentNodes.length - 1 && (
                <div className="relative h-2.5 flex justify-start ml-[30px] pl-3">
                  <div className="w-px bg-white/[0.06] h-full" />
                </div>
              )}
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}

// ── Demo ──────────────────────────────────────────────────────────────────────

function DemoSection() {
  return (
    <section id="demo" className="py-24 px-6 lg:px-8 border-t border-white/[0.05]">
      <div className="max-w-5xl mx-auto">
        <motion.div initial="hidden" whileInView="visible" viewport={{ once: true, margin: '-60px' }} variants={fadeIn}>
          <h2 className="text-2xl sm:text-3xl font-bold text-white mb-2">See it in action</h2>
          <p className="text-white/35 mb-10 text-sm">A full walkthrough from setup to insights.</p>

          <div className="relative aspect-video rounded-xl overflow-hidden border border-white/[0.07] bg-[#080b11]">
            <div className="absolute inset-0" style={{ background: 'radial-gradient(ellipse at 30% 40%, rgba(14,165,233,0.06) 0%, transparent 60%)' }} />
            <div
              className="absolute inset-0 opacity-[0.04]"
              style={{
                backgroundImage: 'linear-gradient(rgba(255,255,255,1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,1) 1px, transparent 1px)',
                backgroundSize: '48px 48px',
              }}
            />
            <div className="absolute inset-0 flex flex-col items-center justify-center gap-4">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.97 }}
                className="w-16 h-16 rounded-full border border-white/15 bg-white/[0.06] flex items-center justify-center hover:bg-white/10 transition-colors"
              >
                <Play className="w-6 h-6 text-white ml-0.5" fill="white" />
              </motion.button>
              <span className="text-sm text-white/30">Demo coming soon</span>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

// ── CTA ───────────────────────────────────────────────────────────────────────

function CTASection() {
  return (
    <section id="contact" className="py-32 px-6 lg:px-8 border-t border-white/[0.05]">
      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
        <motion.div initial="hidden" whileInView="visible" viewport={{ once: true, margin: '-60px' }} variants={fadeIn}>
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4 leading-tight">
            Interested in DevMetrics<br />for your team?
          </h2>
          <p className="text-white/40 leading-relaxed max-w-md">
            This is a portfolio project, but I'm open to discussing it, licensing it, or building
            something similar for your organisation.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-60px' }}
          transition={{ duration: 0.5 }}
          className="flex flex-col sm:flex-row gap-3 lg:justify-end"
        >
          <a
            href="mailto:hello@devmetrics.ai"
            className="inline-flex items-center justify-center gap-2 px-6 py-3 rounded bg-sky-500 hover:bg-sky-400 text-white font-semibold text-sm transition-colors"
          >
            Get in touch <ArrowRight className="w-4 h-4" />
          </a>
        </motion.div>
      </div>
    </section>
  );
}

// ── Footer ────────────────────────────────────────────────────────────────────

function Footer() {
  return (
    <footer className="py-7 px-6 lg:px-8 border-t border-white/[0.05]">
      <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <div className="w-5 h-5 rounded bg-sky-500/80 flex items-center justify-center">
            <BarChart3 className="w-3 h-3 text-white" />
          </div>
          <span className="text-sm text-white/30">DevMetrics AI</span>
        </div>
        <div className="flex items-center gap-6 text-xs text-white/20">
          <span>Private — not open source</span>
          <span>Built by Yash Kamthe</span>
          <span>© {new Date().getFullYear()}</span>
        </div>
      </div>
    </footer>
  );
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function Home() {
  return (
    <div className="min-h-screen bg-[#07090e]">
      <LandingNavbar />
      <HeroSection />
      <FeaturesSection />
      <HowItWorksSection />
      <DataSovereigntySection />
      <AIShowcaseSection />
      <DemoSection />
      <CTASection />
      <Footer />
    </div>
  );
}
