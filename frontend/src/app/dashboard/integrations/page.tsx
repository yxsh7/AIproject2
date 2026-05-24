'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '../../../store/auth';
import { integrationsAPI } from '../../../lib/api';
import { Integration } from '../../../types';
import { Field } from '../../../components/ui/form-field';

type IntegrationStatus = 'active' | 'syncing' | 'error' | 'inactive';

function StatusBadge({ status }: { status: string }) {
  const s = (status as IntegrationStatus) || 'inactive';
  const cfg: Record<string, { bg: string; color: string }> = {
    active:   { bg: 'var(--green-dim)',        color: 'var(--green)' },
    syncing:  { bg: 'var(--cyan-dim)',          color: 'var(--cyan)'  },
    error:    { bg: 'var(--red-dim)',           color: 'var(--red)'   },
    inactive: { bg: 'rgba(255,255,255,0.04)',   color: 'var(--txt-3)' },
  };
  const { bg, color } = cfg[s] ?? cfg.inactive;
  return (
    <span style={{ fontFamily: 'var(--font-mono)', fontSize: 9, padding: '3px 8px', borderRadius: 4, background: bg, color, letterSpacing: '0.08em', textTransform: 'uppercase' }}>
      {s}
    </span>
  );
}

export default function IntegrationsPage() {
  const router = useRouter();
  const { user } = useAuthStore();

  const [integrations,  setIntegrations]  = useState<Integration[]>([]);
  const [loading,       setLoading]       = useState(true);
  const [actionLoading, setActionLoading] = useState<Record<string, boolean>>({});
  const [message,       setMessage]       = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [githubForm,    setGithubForm]    = useState({ organization_name: '', access_token: '' });
  const [jiraForm,      setJiraForm]      = useState({ workspace_url: '', username: '', api_token: '', project_keys: '' });
  const [showGithubForm, setShowGithubForm] = useState(false);
  const [showJiraForm,   setShowJiraForm]   = useState(false);

  useEffect(() => {
    if (!user) { router.push('/login'); return; }
    fetchIntegrations();
  }, [user]);

  const fetchIntegrations = async () => {
    try {
      setLoading(true);
      const res = await integrationsAPI.list();
      setIntegrations(res.data);
    } catch (err: any) {
      showMsg('error', err.response?.data?.detail || 'Failed to load integrations');
    } finally {
      setLoading(false);
    }
  };

  const showMsg = (type: 'success' | 'error', text: string) => {
    setMessage({ type, text });
    setTimeout(() => setMessage(null), 5000);
  };

  const setAL = (key: string, val: boolean) => setActionLoading(prev => ({ ...prev, [key]: val }));

  const handleConfigureGitHub = async (e: React.FormEvent) => {
    e.preventDefault(); setAL('github-configure', true);
    try {
      await integrationsAPI.configureGitHub(githubForm);
      showMsg('success', 'GitHub configured'); setShowGithubForm(false);
      setGithubForm({ organization_name: '', access_token: '' });
      await fetchIntegrations();
    } catch (err: any) { showMsg('error', err.response?.data?.detail || 'Failed'); }
    finally { setAL('github-configure', false); }
  };

  const handleConfigureJira = async (e: React.FormEvent) => {
    e.preventDefault(); setAL('jira-configure', true);
    try {
      await integrationsAPI.configureJira({
        workspace_url: jiraForm.workspace_url, username: jiraForm.username,
        api_token: jiraForm.api_token,
        project_keys: jiraForm.project_keys ? jiraForm.project_keys.split(',').map(k => k.trim()).filter(Boolean) : [],
      });
      showMsg('success', 'Jira configured'); setShowJiraForm(false);
      setJiraForm({ workspace_url: '', username: '', api_token: '', project_keys: '' });
      await fetchIntegrations();
    } catch (err: any) { showMsg('error', err.response?.data?.detail || 'Failed'); }
    finally { setAL('jira-configure', false); }
  };

  const handleTest = async (id: number) => {
    setAL(`test-${id}`, true);
    try { const res = await integrationsAPI.test(id); showMsg(res.data.success ? 'success' : 'error', res.data.message); }
    catch (err: any) { showMsg('error', err.response?.data?.detail || 'Test failed'); }
    finally { setAL(`test-${id}`, false); }
  };

  const handleSync = async (id: number) => {
    setAL(`sync-${id}`, true);
    try { const res = await integrationsAPI.sync(id, 30); showMsg('success', `${res.data.message} (est. ${res.data.estimated_time_minutes} min)`); await fetchIntegrations(); }
    catch (err: any) { showMsg('error', err.response?.data?.detail || 'Sync failed'); }
    finally { setAL(`sync-${id}`, false); }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this integration?')) return;
    setAL(`delete-${id}`, true);
    try { await integrationsAPI.delete(id); showMsg('success', 'Deleted'); await fetchIntegrations(); }
    catch (err: any) { showMsg('error', err.response?.data?.detail || 'Delete failed'); }
    finally { setAL(`delete-${id}`, false); }
  };

  const githubIntegration = integrations.find(i => i.type === 'github');
  const jiraIntegration   = integrations.find(i => i.type === 'jira');
  const isAdmin  = user?.role === 'admin';
  const canSync  = user?.role === 'admin' || user?.role === 'manager';

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', background: 'var(--surf-0)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--txt-3)', letterSpacing: '0.1em' }}>Loading…</div>
      </div>
    );
  }

  const ActionBtn = ({ label, onClick, disabled, variant }: { label: string; onClick: () => void; disabled?: boolean; variant?: 'danger' | 'accent' }) => (
    <button
      onClick={onClick}
      disabled={disabled}
      className={variant === 'accent' ? 'dm-btn dm-btn-cyan' : 'dm-btn'}
      style={{
        fontSize: 11,
        ...(variant === 'danger' ? { borderColor: 'rgba(248,113,113,0.25)', color: 'var(--red)', background: 'var(--red-dim)' } : {}),
      }}
    >
      {label}
    </button>
  );

  const renderIntegration = (
    type: 'github' | 'jira',
    integration: Integration | undefined,
    showForm: boolean,
    setShowForm: (v: boolean) => void,
    formJsx: React.ReactNode,
  ) => {
    const title    = type === 'github' ? 'GitHub' : 'Jira';
    const subtitle = type === 'github' ? 'Commits, pull requests, code reviews' : 'Tickets, stories, project data';
    const id       = integration?.id;
    return (
      <div className="dm-card">
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
            <div style={{
              width: 36, height: 36, borderRadius: 8,
              background: 'rgba(255,255,255,0.04)', border: '1px solid var(--border-1)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontFamily: 'var(--font-mono)', fontSize: 10, fontWeight: 700,
              color: type === 'github' ? 'var(--txt-2)' : 'var(--amber)',
            }}>
              {type === 'github' ? 'GH' : 'JR'}
            </div>
            <div>
              <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--txt-1)', marginBottom: 2 }}>{title}</div>
              <div style={{ fontSize: 11, color: 'var(--txt-3)' }}>{subtitle}</div>
            </div>
          </div>
          {integration && <StatusBadge status={integration.status} />}
        </div>

        {integration ? (
          <>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginBottom: 14 }}>
              {[
                { k: 'Status', v: integration.status },
                { k: 'Last Sync', v: integration.last_sync_at ? new Date(integration.last_sync_at).toLocaleString() : 'Never' },
              ].map(({ k, v }) => (
                <div key={k} style={{ padding: '8px 11px', background: 'rgba(255,255,255,0.025)', borderRadius: 7 }}>
                  <div style={{ fontSize: 9, color: 'var(--txt-3)', textTransform: 'uppercase', letterSpacing: '0.07em', fontFamily: 'var(--font-mono)', marginBottom: 3 }}>{k}</div>
                  <div style={{ fontSize: 11, color: 'var(--txt-2)', fontFamily: 'var(--font-mono)' }}>{v}</div>
                </div>
              ))}
            </div>
            <div style={{ display: 'flex', gap: 7, flexWrap: 'wrap' }}>
              {isAdmin && id && (
                <>
                  <ActionBtn label={actionLoading[`test-${id}`] ? 'Testing…' : 'Test'} onClick={() => handleTest(id)} disabled={actionLoading[`test-${id}`]} />
                  <ActionBtn label="Reconfigure" onClick={() => setShowForm(!showForm)} />
                  <ActionBtn label={actionLoading[`delete-${id}`] ? 'Deleting…' : 'Delete'} onClick={() => handleDelete(id)} disabled={actionLoading[`delete-${id}`]} variant="danger" />
                </>
              )}
              {canSync && id && (
                <ActionBtn label={actionLoading[`sync-${id}`] ? 'Syncing…' : 'Sync Now'} onClick={() => handleSync(id)} disabled={actionLoading[`sync-${id}`]} variant="accent" />
              )}
            </div>
          </>
        ) : (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: 12, color: 'var(--txt-3)' }}>
              {isAdmin ? 'Not connected.' : 'Not connected — ask your admin to configure.'}
            </span>
            {isAdmin && (
              <button
                className="dm-btn dm-btn-cyan"
                onClick={() => setShowForm(!showForm)}
                style={{ fontSize: 11, marginLeft: 12, whiteSpace: 'nowrap' }}
              >
                Connect {title}
              </button>
            )}
          </div>
        )}

        {showForm && isAdmin && (
          <div style={{ marginTop: 20, paddingTop: 20, borderTop: '1px solid var(--border-0)' }}>
            {formJsx}
          </div>
        )}
      </div>
    );
  };

  return (
    <div style={{ minHeight: '100vh', background: 'var(--surf-0)', color: 'var(--txt-1)' }}>

      {/* Header */}
      <header style={{
        position: 'sticky', top: 0, zIndex: 40,
        background: 'rgba(10,10,10,0.9)', backdropFilter: 'blur(16px)',
        borderBottom: '1px solid var(--border-0)', padding: '0 24px', height: 52,
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ width: 28, height: 28, background: 'var(--cyan)', borderRadius: 6, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 10, fontWeight: 700, fontFamily: 'var(--font-mono)', color: '#0a0a0a' }}>DM</div>
          <span style={{ fontSize: 14, fontWeight: 600, color: 'var(--txt-1)', letterSpacing: '-0.01em' }}>DevMetrics</span>
          <div style={{ width: 1, height: 14, background: 'var(--border-1)' }} />
          <span style={{ fontSize: 11, color: 'var(--txt-3)' }}>Integrations</span>
        </div>
        <div style={{ display: 'flex', gap: 6 }}>
          {canSync && <button className="dm-btn" onClick={() => router.push('/dashboard/manager')} style={{ fontSize: 11 }}>Team</button>}
          <button className="dm-btn" onClick={() => router.push('/dashboard/settings')} style={{ fontSize: 11 }}>Settings</button>
          <button className="dm-btn" onClick={() => router.push('/dashboard')} style={{ fontSize: 11 }}>Dashboard</button>
        </div>
      </header>

      <main style={{ maxWidth: 760, margin: '0 auto', padding: '32px 24px' }}>
        <div style={{ marginBottom: 28 }}>
          <h1 style={{ fontSize: 18, fontWeight: 600, color: 'var(--txt-1)', letterSpacing: '-0.02em', marginBottom: 6 }}>Data Sources</h1>
          <p style={{ fontSize: 13, color: 'var(--txt-3)' }}>Connect GitHub and Jira to sync your team&apos;s activity data.</p>
        </div>

        {message && (
          <div style={{
            marginBottom: 20, padding: '10px 14px', borderRadius: 8, fontSize: 12,
            background: message.type === 'success' ? 'var(--green-dim)' : 'var(--red-dim)',
            border: `1px solid ${message.type === 'success' ? 'rgba(74,222,128,0.25)' : 'rgba(248,113,113,0.25)'}`,
            color: message.type === 'success' ? 'var(--green)' : 'var(--red)',
          }}>
            {message.text}
          </div>
        )}

        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {renderIntegration(
            'github', githubIntegration, showGithubForm, setShowGithubForm,
            <form onSubmit={handleConfigureGitHub} style={{ display: 'flex', flexDirection: 'column', gap: 13 }}>
              <div style={{ fontSize: 11, color: 'var(--txt-3)', marginBottom: 4 }}>GitHub Configuration</div>
              <Field label="Organization or username" value={githubForm.organization_name} onChange={v => setGithubForm(p => ({ ...p, organization_name: v }))} opts={{ placeholder: 'my-org', required: true }} />
              <Field label="Personal Access Token" value={githubForm.access_token} onChange={v => setGithubForm(p => ({ ...p, access_token: v }))} opts={{ type: 'password', placeholder: 'ghp_…', hint: 'Scopes: repo, read:org, read:user', required: true }} />
              <div style={{ display: 'flex', gap: 8, marginTop: 2 }}>
                <button type="submit" disabled={actionLoading['github-configure']} className="dm-btn dm-btn-cyan" style={{ fontSize: 11 }}>
                  {actionLoading['github-configure'] ? 'Saving…' : 'Save'}
                </button>
                <button type="button" className="dm-btn" onClick={() => setShowGithubForm(false)} style={{ fontSize: 11 }}>Cancel</button>
              </div>
            </form>,
          )}

          {renderIntegration(
            'jira', jiraIntegration, showJiraForm, setShowJiraForm,
            <form onSubmit={handleConfigureJira} style={{ display: 'flex', flexDirection: 'column', gap: 13 }}>
              <div style={{ fontSize: 11, color: 'var(--txt-3)', marginBottom: 4 }}>Jira Configuration</div>
              <Field label="Workspace URL" value={jiraForm.workspace_url} onChange={v => setJiraForm(p => ({ ...p, workspace_url: v }))} opts={{ placeholder: 'https://yourcompany.atlassian.net', required: true }} />
              <Field label="Email / Username" value={jiraForm.username} onChange={v => setJiraForm(p => ({ ...p, username: v }))} opts={{ type: 'email', placeholder: 'you@company.com', required: true }} />
              <Field label="API Token" value={jiraForm.api_token} onChange={v => setJiraForm(p => ({ ...p, api_token: v }))} opts={{ type: 'password', placeholder: 'Jira API token', hint: 'id.atlassian.com → Security → API tokens', required: true }} />
              <Field label="Project Keys (optional)" value={jiraForm.project_keys} onChange={v => setJiraForm(p => ({ ...p, project_keys: v }))} opts={{ placeholder: 'PROJ, DEV, BACKEND' }} />
              <div style={{ display: 'flex', gap: 8, marginTop: 2 }}>
                <button type="submit" disabled={actionLoading['jira-configure']} className="dm-btn dm-btn-cyan" style={{ fontSize: 11 }}>
                  {actionLoading['jira-configure'] ? 'Saving…' : 'Save'}
                </button>
                <button type="button" className="dm-btn" onClick={() => setShowJiraForm(false)} style={{ fontSize: 11 }}>Cancel</button>
              </div>
            </form>,
          )}

          {!isAdmin && (
            <div className="dm-card" style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
              <span className="dm-tag dm-tag-amber" style={{ flexShrink: 0, marginTop: 1 }}>Note</span>
              <p style={{ fontSize: 12, color: 'var(--txt-3)', lineHeight: 1.6 }}>
                Only administrators can configure integrations.{canSync && ' You can trigger syncs on connected integrations above.'}
              </p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
