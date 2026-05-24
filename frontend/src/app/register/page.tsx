'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '../../store/auth';
import { RegisterData } from '../../types';

export default function RegisterPage() {
  const router = useRouter();
  const { register, isLoading, error, clearError } = useAuthStore();

  const [formData, setFormData] = useState<RegisterData>({
    email: '', password: '', full_name: '', role: 'developer',
  });
  const [confirmPassword, setConfirmPassword] = useState('');
  const [localError, setLocalError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setLocalError(null);
    clearError();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError(null);
    if (formData.password !== confirmPassword) { setLocalError('Passwords do not match'); return; }
    if (formData.password.length < 8) { setLocalError('Password must be at least 8 characters'); return; }
    try {
      await register(formData);
      router.push('/dashboard');
    } catch (err) {
      console.error('Registration failed:', err);
    }
  };

  const displayError = localError || error;

  return (
    <div
      className="dm-bg-grid"
      style={{ minHeight: '100vh', background: 'var(--surf-0)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24 }}
    >
      <div
        className="fade-up"
        style={{ width: '100%', maxWidth: 380, background: 'var(--surf-1)', border: '1px solid var(--border-1)', borderRadius: 12, padding: '32px 28px' }}
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
          Create account
        </h1>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 13 }}>
          <div>
            <label style={{ display: 'block', fontSize: 11, color: 'var(--txt-3)', marginBottom: 6 }}>Full Name</label>
            <input className="dm-input" type="text" name="full_name" value={formData.full_name} onChange={handleChange} placeholder="Jane Smith" required disabled={isLoading} />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: 11, color: 'var(--txt-3)', marginBottom: 6 }}>Email</label>
            <input className="dm-input" type="email" name="email" value={formData.email} onChange={handleChange} placeholder="you@company.com" required disabled={isLoading} />
          </div>

          {/* Role picker */}
          <div>
            <label style={{ display: 'block', fontSize: 11, color: 'var(--txt-3)', marginBottom: 8 }}>Role</label>
            <div style={{ display: 'flex', gap: 8 }}>
              {(['developer', 'manager'] as const).map(r => (
                <button
                  key={r}
                  type="button"
                  onClick={() => setFormData(p => ({ ...p, role: r }))}
                  disabled={isLoading}
                  style={{
                    flex: 1, padding: '8px 0', borderRadius: 7, cursor: 'pointer',
                    border: formData.role === r ? '1px solid rgba(129,140,248,0.35)' : '1px solid var(--border-1)',
                    background: formData.role === r ? 'rgba(129,140,248,0.08)' : 'transparent',
                    color: formData.role === r ? 'var(--cyan)' : 'var(--txt-3)',
                    fontSize: 12, fontFamily: 'var(--font-body)', fontWeight: formData.role === r ? 500 : 400,
                    transition: 'all 0.12s',
                  }}
                >
                  {r.charAt(0).toUpperCase() + r.slice(1)}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: 11, color: 'var(--txt-3)', marginBottom: 6 }}>Password</label>
            <input className="dm-input" type="password" name="password" value={formData.password} onChange={handleChange} placeholder="At least 8 characters" required disabled={isLoading} />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: 11, color: 'var(--txt-3)', marginBottom: 6 }}>Confirm Password</label>
            <input
              className="dm-input" type="password" name="confirmPassword"
              value={confirmPassword}
              onChange={e => { setConfirmPassword(e.target.value); setLocalError(null); clearError(); }}
              placeholder="Re-enter password" required disabled={isLoading}
            />
          </div>

          {displayError && (
            <div style={{ background: 'var(--red-dim)', border: '1px solid rgba(248,113,113,0.2)', borderRadius: 8, padding: '9px 13px', fontSize: 12, color: 'var(--red)' }}>
              {displayError}
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
            {isLoading ? 'Creating account…' : 'Create account'}
          </button>
        </form>

        <p style={{ textAlign: 'center', marginTop: 16, fontSize: 12, color: 'var(--txt-3)' }}>
          Already have an account?{' '}
          <a href="/login" style={{ color: 'var(--cyan)', textDecoration: 'none' }}>Sign in</a>
        </p>
      </div>
    </div>
  );
}
