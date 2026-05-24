'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '../../store/auth';

export default function LoginPage() {
  const router = useRouter();
  const { login, isLoading, error } = useAuthStore();

  const [email,    setEmail]    = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login({ email, password });
      router.push('/dashboard');
    } catch {
      /* handled by store */
    }
  };

  const fillDemo = (role: 'manager' | 'dev') => {
    if (role === 'manager') { setEmail('manager@devmetrics.ai'); setPassword('Manager123!'); }
    else                    { setEmail('dev@devmetrics.ai');     setPassword('Dev123!');     }
  };

  return (
    <div
      className="dm-bg-grid"
      style={{
        minHeight: '100vh',
        background: 'var(--surf-0)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 24,
      }}
    >
      <div
        className="fade-up"
        style={{
          width: '100%',
          maxWidth: 380,
          background: 'var(--surf-1)',
          border: '1px solid var(--border-1)',
          borderRadius: 12,
          padding: '32px 28px',
        }}
      >
        {/* Logo */}
        <div style={{ marginBottom: 28 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 9, marginBottom: 6 }}>
            <div style={{
              width: 30, height: 30, background: 'var(--cyan)', borderRadius: 7,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 10, fontWeight: 700, fontFamily: 'var(--font-mono)', color: '#0a0a0a',
            }}>DM</div>
            <span style={{ fontSize: 15, fontWeight: 600, color: 'var(--txt-1)', letterSpacing: '-0.02em' }}>DevMetrics</span>
          </div>
          <p style={{ fontSize: 12, color: 'var(--txt-3)', marginTop: 2 }}>Engineering Intelligence Platform</p>
        </div>

        <h1 style={{ fontSize: 16, fontWeight: 600, color: 'var(--txt-1)', marginBottom: 22, letterSpacing: '-0.01em' }}>
          Sign in
        </h1>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <div>
            <label style={{ display: 'block', fontSize: 11, color: 'var(--txt-3)', marginBottom: 6 }}>Email</label>
            <input
              className="dm-input"
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="you@company.com"
              required
              disabled={isLoading}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: 11, color: 'var(--txt-3)', marginBottom: 6 }}>Password</label>
            <input
              className="dm-input"
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              disabled={isLoading}
            />
          </div>

          {error && (
            <div style={{ background: 'var(--red-dim)', border: '1px solid rgba(248,113,113,0.2)', borderRadius: 8, padding: '9px 13px', fontSize: 12, color: 'var(--red)' }}>
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            style={{
              width: '100%',
              background: isLoading ? 'rgba(129,140,248,0.06)' : 'var(--cyan)',
              color: isLoading ? 'var(--txt-3)' : '#0a0a0a',
              border: 'none', borderRadius: 8,
              padding: '11px 0', fontSize: 13, fontWeight: 600,
              fontFamily: 'var(--font-body)',
              cursor: isLoading ? 'default' : 'pointer',
              transition: 'all 0.15s', marginTop: 2,
            }}
          >
            {isLoading ? 'Signing in…' : 'Sign in'}
          </button>
        </form>

        <p style={{ textAlign: 'center', marginTop: 16, fontSize: 12, color: 'var(--txt-3)' }}>
          No account?{' '}
          <a href="/register" style={{ color: 'var(--cyan)', textDecoration: 'none' }}>Register</a>
        </p>

        {/* Demo accounts */}
        <div style={{ marginTop: 24, paddingTop: 20, borderTop: '1px solid var(--border-0)' }}>
          <p style={{ fontSize: 10, color: 'var(--txt-3)', textAlign: 'center', marginBottom: 10 }}>Demo accounts</p>
          <div style={{ display: 'flex', gap: 8 }}>
            {(['manager', 'dev'] as const).map(role => (
              <button
                key={role}
                onClick={() => fillDemo(role)}
                className="dm-btn"
                style={{ flex: 1, fontSize: 11 }}
              >
                {role === 'manager' ? 'Manager' : 'Developer'}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
