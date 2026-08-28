'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '../../../store/auth';
import { developersAPI } from '../../../lib/api';
import { DeveloperProfile } from '../../../types';
import { Field, TextareaField, SelectField } from '../../../components/ui/form-field';

// ─── Role level options ───────────────────────────────────────────────────────
const ROLE_LEVELS = ['intern', 'junior', 'mid', 'senior', 'staff', 'principal'] as const;

// ─── Toast ────────────────────────────────────────────────────────────────────
type Toast = { type: 'success' | 'error'; text: string } | null;

function showToastFn(set: (t: Toast) => void, type: 'success' | 'error', text: string) {
  set({ type, text });
  setTimeout(() => set(null), 4500);
}

// ─── Team Profiles row ────────────────────────────────────────────────────────
function TeamProfileRow({
  dev,
  onSave,
}: {
  dev: DeveloperProfile & { full_name?: string; email?: string };
  onSave: (id: number, data: { github_username: string; jira_username: string }) => Promise<void>;
}) {
  const [github, setGithub] = useState(dev.github_username || '');
  const [jira,   setJira]   = useState(dev.jira_username   || '');
  const [saving, setSaving] = useState(false);
  const [saved,  setSaved]  = useState(false);

  const dirty = github !== (dev.github_username || '') || jira !== (dev.jira_username || '');

  const handleSave = async () => {
    setSaving(true);
    try {
      await onSave(dev.id, { github_username: github, jira_username: jira });
      setSaved(true);
      setTimeout(() => setSaved(false), 2500);
    } finally {
      setSaving(false);
    }
  };

  const displayName = (dev as any).full_name || (dev as any).email || `Developer #${dev.id}`;

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: '1fr 1fr 1fr auto',
      gap: 10,
      alignItems: 'center',
      padding: '10px 0',
      borderBottom: '1px solid var(--border-0)',
    }}>
      {/* Name / team */}
      <div>
        <div style={{ fontSize: 13, color: 'var(--txt-1)', fontWeight: 500 }}>{displayName}</div>
        <div style={{ fontSize: 10, color: 'var(--txt-3)', marginTop: 2, fontFamily: 'var(--font-mono)' }}>
          {dev.team || 'no team'} · {dev.role_level}
        </div>
      </div>

      {/* GitHub username */}
      <input
        className="dm-input"
        value={github}
        onChange={e => setGithub(e.target.value)}
        placeholder="github_user"
        style={{ fontSize: 12 }}
      />

      {/* Jira username */}
      <input
        className="dm-input"
        value={jira}
        onChange={e => setJira(e.target.value)}
        placeholder="jira_user"
        style={{ fontSize: 12 }}
      />

      {/* Save */}
      <button
        className={`dm-btn${dirty || saved ? ' dm-btn-cyan' : ''}`}
        onClick={handleSave}
        disabled={saving || (!dirty && !saved)}
        style={{ fontSize: 11, minWidth: 56 }}
      >
        {saving ? 'Saving…' : saved ? 'Saved' : 'Save'}
      </button>
    </div>
  );
}

// ─── Page ─────────────────────────────────────────────────────────────────────
export default function SettingsPage() {
  const router = useRouter();
  const { user, logout, isInitializing } = useAuthStore();

  const [activeTab,    setActiveTab]    = useState<'profile' | 'team'>('profile');
  const [toast,        setToast]        = useState<Toast>(null);
  const [myProfile,    setMyProfile]    = useState<DeveloperProfile | null>(null);
  const [allDevs,      setAllDevs]      = useState<(DeveloperProfile & { full_name?: string; email?: string })[]>([]);
  const [loading,      setLoading]      = useState(true);
  const [saving,       setSaving]       = useState(false);
  const [noProfile,    setNoProfile]    = useState(false);

  // My profile form state
  const [githubUsername,  setGithubUsername]  = useState('');
  const [jiraUsername,    setJiraUsername]    = useState('');
  const [bio,             setBio]             = useState('');
  const [team,            setTeam]            = useState('');
  const [roleLevel,       setRoleLevel]       = useState<typeof ROLE_LEVELS[number]>('mid');

  const isManager = user?.role === 'manager' || user?.role === 'admin';

  const showToast = (type: 'success' | 'error', text: string) =>
    showToastFn(setToast, type, text);

  // ── Fetch data ───────────────────────────────────────────────────────────────
  useEffect(() => {
    if (isInitializing) return;
    if (!user) { router.push('/login'); return; }
    fetchData();
  }, [user, isInitializing]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const devsRes = await developersAPI.list();
      const devs = devsRes.data as (DeveloperProfile & { full_name?: string; email?: string })[];
      const mine = devs.find(d => d.user_id === user?.id);

      if (!mine) {
        setNoProfile(true);
        setLoading(false);
        return;
      }

      setMyProfile(mine);
      setGithubUsername(mine.github_username || '');
      setJiraUsername(mine.jira_username || '');
      setBio(mine.bio || '');
      setTeam(mine.team || '');
      setRoleLevel((mine.role_level as typeof ROLE_LEVELS[number]) || 'mid');

      if (isManager) {
        setAllDevs(devs);
      }
    } catch (e: any) {
      showToast('error', e.response?.data?.detail || 'Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  // ── Save my profile ──────────────────────────────────────────────────────────
  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!myProfile) return;
    setSaving(true);
    try {
      await developersAPI.update(myProfile.id, {
        github_username: githubUsername || null,
        jira_username:   jiraUsername   || null,
        bio:             bio            || null,
        team:            team           || null,
        role_level:      roleLevel,
      });
      showToast('success', 'Profile saved successfully');
      // Refresh local state
      setMyProfile(prev => prev ? {
        ...prev,
        github_username: githubUsername || undefined,
        jira_username:   jiraUsername   || undefined,
        bio:             bio            || undefined,
        team:            team           || undefined,
        role_level:      roleLevel,
      } : prev);
    } catch (e: any) {
      showToast('error', e.response?.data?.detail || 'Failed to save profile');
    } finally {
      setSaving(false);
    }
  };

  // ── Save a team row ──────────────────────────────────────────────────────────
  const handleSaveTeamRow = async (id: number, data: { github_username: string; jira_username: string }) => {
    try {
      await developersAPI.update(id, {
        github_username: data.github_username || null,
        jira_username:   data.jira_username   || null,
      });
      showToast('success', 'Developer profile updated');
      setAllDevs(prev => prev.map(d => d.id === id ? { ...d, ...data } : d));
    } catch (e: any) {
      showToast('error', e.response?.data?.detail || 'Failed to update developer');
      throw e; // let the row know it failed
    }
  };

  const handleLogout = () => { logout(); router.push('/login'); };

  // ── Loading ──────────────────────────────────────────────────────────────────
  if (loading) {
    return (
      <div style={{ minHeight: '100vh', background: 'var(--surf-0)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--txt-3)', letterSpacing: '0.1em' }}>
          Loading…
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', background: 'var(--surf-0)', color: 'var(--txt-1)' }}>

      {/* ── Header ─────────────────────────────────────────────────────────── */}
      <header style={{
        position: 'sticky', top: 0, zIndex: 40,
        background: 'rgba(10,10,10,0.9)', backdropFilter: 'blur(16px)',
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
          <span style={{ fontSize: 14, fontWeight: 600, color: 'var(--txt-1)', letterSpacing: '-0.01em' }}>
            DevMetrics
          </span>
          <div style={{ width: 1, height: 14, background: 'var(--border-1)' }} />
          <span style={{ fontSize: 11, color: 'var(--txt-3)' }}>Settings</span>
        </div>
        <div style={{ display: 'flex', gap: 6 }}>
          {isManager && (
            <button className="dm-btn" onClick={() => router.push('/dashboard/manager')} style={{ fontSize: 11 }}>
              Team
            </button>
          )}
          <button className="dm-btn" onClick={() => router.push('/dashboard/integrations')} style={{ fontSize: 11 }}>
            Integrations
          </button>
          <button className="dm-btn" onClick={() => router.push('/dashboard')} style={{ fontSize: 11 }}>
            Dashboard
          </button>
          <button className="dm-btn" onClick={handleLogout} style={{ fontSize: 11, color: 'var(--txt-3)' }}>
            Sign out
          </button>
        </div>
      </header>

      <main style={{ maxWidth: 800, margin: '0 auto', padding: '32px 24px' }}>

        {/* ── Page title ─────────────────────────────────────────────────── */}
        <div style={{ marginBottom: 28 }}>
          <h1 style={{ fontSize: 18, fontWeight: 600, color: 'var(--txt-1)', letterSpacing: '-0.02em', marginBottom: 6 }}>
            Settings
          </h1>
          <p style={{ fontSize: 13, color: 'var(--txt-3)' }}>
            Manage your developer profile and team settings.
          </p>
        </div>

        {/* ── Toast ──────────────────────────────────────────────────────── */}
        {toast && (
          <div style={{
            marginBottom: 20, padding: '10px 14px', borderRadius: 8, fontSize: 12,
            background: toast.type === 'success' ? 'var(--green-dim)' : 'var(--red-dim)',
            border: `1px solid ${toast.type === 'success' ? 'rgba(74,222,128,0.25)' : 'rgba(248,113,113,0.25)'}`,
            color: toast.type === 'success' ? 'var(--green)' : 'var(--red)',
          }}>
            {toast.text}
          </div>
        )}

        {/* ── Tabs ───────────────────────────────────────────────────────── */}
        <div style={{ display: 'flex', gap: 4, marginBottom: 20, borderBottom: '1px solid var(--border-0)', paddingBottom: 0 }}>
          {([
            { key: 'profile', label: 'My Profile' },
            ...(isManager ? [{ key: 'team', label: 'Team Profiles' }] : []),
          ] as { key: 'profile' | 'team'; label: string }[]).map(tab => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              style={{
                padding: '8px 16px',
                background: 'transparent',
                border: 'none',
                borderBottom: `2px solid ${activeTab === tab.key ? 'var(--cyan)' : 'transparent'}`,
                color: activeTab === tab.key ? 'var(--txt-1)' : 'var(--txt-3)',
                fontSize: 13,
                fontWeight: activeTab === tab.key ? 600 : 400,
                fontFamily: 'var(--font-body)',
                cursor: 'pointer',
                marginBottom: -1,
                transition: 'color 0.12s, border-color 0.12s',
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* ── Tab: My Profile ────────────────────────────────────────────── */}
        {activeTab === 'profile' && (
          <div className="fade-up">
            {noProfile ? (
              <div className="dm-card">
                <h2 style={{ fontSize: 15, fontWeight: 600, marginBottom: 8 }}>No Developer Profile</h2>
                <p style={{ fontSize: 13, color: 'var(--txt-2)', lineHeight: 1.6 }}>
                  Your account doesn&apos;t have a developer profile yet. Contact your administrator to create one.
                </p>
              </div>
            ) : (
              <form onSubmit={handleSaveProfile}>
                <div className="dm-card" style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>

                  {/* Account info (read-only) */}
                  <div style={{ paddingBottom: 16, borderBottom: '1px solid var(--border-0)' }}>
                    <span className="dm-label">Account</span>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                      <Field
                        label="Email"
                        value={user?.email || ''}
                        onChange={() => {}}
                        opts={{ disabled: true, hint: 'Email cannot be changed here' }}
                      />
                      <Field
                        label="Full Name"
                        value={user?.full_name || ''}
                        onChange={() => {}}
                        opts={{ disabled: true }}
                      />
                    </div>
                    <div style={{ marginTop: 10 }}>
                      <label style={{ display: 'block', fontSize: 11, color: 'var(--txt-3)', marginBottom: 6 }}>
                        Role
                      </label>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span
                          className="dm-tag"
                          style={{ background: 'rgba(255,255,255,0.04)', color: 'var(--txt-2)', border: '1px solid var(--border-1)' }}
                        >
                          {user?.role}
                        </span>
                        <span style={{ fontSize: 11, color: 'var(--txt-3)' }}>managed by your administrator</span>
                      </div>
                    </div>
                  </div>

                  {/* Developer profile fields */}
                  <div>
                    <span className="dm-label">Developer Profile</span>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>

                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
                        <Field
                          label="GitHub Username"
                          value={githubUsername}
                          onChange={setGithubUsername}
                          opts={{ placeholder: 'your-github-handle' }}
                        />
                        <Field
                          label="Jira Username"
                          value={jiraUsername}
                          onChange={setJiraUsername}
                          opts={{ placeholder: 'your.jira.username' }}
                        />
                      </div>

                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
                        <Field
                          label="Team"
                          value={team}
                          onChange={setTeam}
                          opts={{ placeholder: 'e.g. Platform, Frontend, Backend' }}
                        />
                        <SelectField
                          label="Role Level"
                          value={roleLevel}
                          onChange={v => setRoleLevel(v as typeof ROLE_LEVELS[number])}
                          options={ROLE_LEVELS}
                        />
                      </div>

                      <TextareaField
                        label="Bio"
                        value={bio}
                        onChange={setBio}
                        placeholder="A short bio about you and your work…"
                      />
                    </div>
                  </div>

                  {/* Save */}
                  <div style={{ display: 'flex', justifyContent: 'flex-end', paddingTop: 4 }}>
                    <button
                      type="submit"
                      disabled={saving}
                      className="dm-btn dm-btn-cyan"
                      style={{ fontSize: 12, padding: '7px 20px' }}
                    >
                      {saving ? 'Saving…' : 'Save Profile'}
                    </button>
                  </div>
                </div>
              </form>
            )}
          </div>
        )}

        {/* ── Tab: Team Profiles ─────────────────────────────────────────── */}
        {activeTab === 'team' && isManager && (
          <div className="fade-up">
            <div className="dm-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                <span className="dm-label" style={{ marginBottom: 0 }}>Team Profiles</span>
                <span style={{ fontSize: 11, color: 'var(--txt-3)' }}>{allDevs.length} developers</span>
              </div>

              {/* Column headers */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: '1fr 1fr 1fr auto',
                gap: 10,
                padding: '0 0 8px',
                borderBottom: '1px solid var(--border-1)',
                marginBottom: 4,
              }}>
                {['Developer', 'GitHub Username', 'Jira Username', ''].map((h, i) => (
                  <div key={i} style={{ fontSize: 9, color: 'var(--txt-3)', textTransform: 'uppercase', letterSpacing: '0.07em', fontFamily: 'var(--font-mono)' }}>
                    {h}
                  </div>
                ))}
              </div>

              {allDevs.length === 0 ? (
                <p style={{ fontSize: 13, color: 'var(--txt-3)', padding: '16px 0' }}>
                  No developer profiles found.
                </p>
              ) : (
                allDevs.map(dev => (
                  <TeamProfileRow
                    key={dev.id}
                    dev={dev}
                    onSave={handleSaveTeamRow}
                  />
                ))
              )}
            </div>
          </div>
        )}

      </main>
    </div>
  );
}
