'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '../../../store/auth';
import { adminAPI } from '../../../lib/api';
import { useToast } from '../../../components/ui/toast';
import { AdminOrganization, AdminUser } from '../../../types';

function StatusTag({ active }: { active: boolean }) {
  return (
    <span
      className="dm-tag"
      style={{
        fontFamily: 'var(--font-mono)', fontSize: 9, padding: '2px 6px', borderRadius: 4,
        background: active ? 'rgba(74,222,128,0.1)' : 'rgba(248,113,113,0.1)',
        color: active ? '#4ade80' : 'var(--red)',
        letterSpacing: '0.06em', textTransform: 'uppercase' as const,
      }}
    >
      {active ? 'Active' : 'Suspended'}
    </span>
  );
}

export default function SuperadminDashboardPage() {
  const router = useRouter();
  const { user, isInitializing } = useAuthStore();
  const { addToast } = useToast();

  const [orgs, setOrgs] = useState<AdminOrganization[]>([]);
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterOrgId, setFilterOrgId] = useState<number | null>(null);

  useEffect(() => {
    if (isInitializing) return;
    if (!user) { router.push('/login'); return; }
    if (!user.is_superadmin) { router.push('/dashboard'); return; }
    fetchAll();
  }, [user, isInitializing]);

  const fetchAll = async () => {
    try {
      setLoading(true);
      const [orgsRes, usersRes] = await Promise.all([
        adminAPI.listOrganizations(),
        adminAPI.listUsers(),
      ]);
      setOrgs(orgsRes.data);
      setUsers(usersRes.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load platform data');
    } finally {
      setLoading(false);
    }
  };

  const toggleOrg = async (org: AdminOrganization) => {
    try {
      const res = await adminAPI.updateOrganization(org.id, { is_active: !org.is_active });
      setOrgs(prev => prev.map(o => (o.id === org.id ? res.data : o)));
      addToast(`${org.name} ${res.data.is_active ? 'reactivated' : 'suspended'}`, 'success');
    } catch (err: any) {
      addToast(err.response?.data?.detail || 'Failed to update organization', 'error');
    }
  };

  const toggleUser = async (u: AdminUser) => {
    try {
      const res = await adminAPI.updateUser(u.id, { is_active: !u.is_active });
      setUsers(prev => prev.map(x => (x.id === u.id ? res.data : x)));
      addToast(`${u.email} ${res.data.is_active ? 'reactivated' : 'deactivated'}`, 'success');
    } catch (err: any) {
      addToast(err.response?.data?.detail || 'Failed to update user', 'error');
    }
  };

  const visibleUsers = filterOrgId ? users.filter(u => u.organization_id === filterOrgId) : users;

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', background: 'var(--surf-0)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--txt-3)', letterSpacing: '0.1em' }}>Loading…</div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', background: 'var(--surf-0)', color: 'var(--txt-1)' }}>
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
          <span style={{ fontSize: 11, color: 'var(--txt-3)' }}>Platform Admin</span>
        </div>
        <div style={{ display: 'flex', gap: 6 }}>
          <button className="dm-btn" onClick={() => router.push('/dashboard')} style={{ fontSize: 11 }}>My Dashboard</button>
        </div>
      </header>

      <main style={{ maxWidth: 1100, margin: '0 auto', padding: '24px 24px' }}>
        {error && (
          <div style={{ background: 'var(--red-dim)', border: '1px solid rgba(248,113,113,0.2)', borderRadius: 8, padding: '10px 14px', fontSize: 12, color: 'var(--red)', marginBottom: 20 }}>
            {error}
          </div>
        )}

        {/* Organizations */}
        <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', marginBottom: 12 }}>
          <h2 style={{ fontSize: 13, fontWeight: 600, color: 'var(--txt-1)' }}>Organizations</h2>
          <span style={{ fontSize: 11, color: 'var(--txt-3)' }}>{orgs.length} total</span>
        </div>
        <div className="dm-card" style={{ marginBottom: 28, overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-1)' }}>
                {['Name', 'Slug', 'Users', 'Developers', 'Status', ''].map(h => (
                  <th key={h} style={{ textAlign: 'left', padding: '10px 14px', color: 'var(--txt-3)', fontWeight: 500, fontSize: 11 }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {orgs.map(org => (
                <tr key={org.id} style={{ borderBottom: '1px solid var(--border-0)' }}>
                  <td style={{ padding: '10px 14px', color: 'var(--txt-1)' }}>{org.name}</td>
                  <td style={{ padding: '10px 14px', color: 'var(--txt-3)', fontFamily: 'var(--font-mono)', fontSize: 11 }}>{org.slug}</td>
                  <td style={{ padding: '10px 14px' }}>
                    <button
                      onClick={() => setFilterOrgId(filterOrgId === org.id ? null : org.id)}
                      style={{ background: 'none', border: 'none', color: 'var(--cyan)', cursor: 'pointer', fontSize: 12, padding: 0 }}
                    >
                      {org.user_count}
                    </button>
                  </td>
                  <td style={{ padding: '10px 14px', color: 'var(--txt-2)' }}>{org.developer_count}</td>
                  <td style={{ padding: '10px 14px' }}><StatusTag active={org.is_active} /></td>
                  <td style={{ padding: '10px 14px', textAlign: 'right' }}>
                    <button className="dm-btn" onClick={() => toggleOrg(org)} style={{ fontSize: 11 }}>
                      {org.is_active ? 'Suspend' : 'Reactivate'}
                    </button>
                  </td>
                </tr>
              ))}
              {orgs.length === 0 && (
                <tr><td colSpan={6} style={{ padding: 20, textAlign: 'center', color: 'var(--txt-3)' }}>No organizations yet</td></tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Users */}
        <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', marginBottom: 12 }}>
          <h2 style={{ fontSize: 13, fontWeight: 600, color: 'var(--txt-1)' }}>
            Users {filterOrgId && <span style={{ color: 'var(--txt-3)', fontWeight: 400 }}>· filtered to {orgs.find(o => o.id === filterOrgId)?.name}</span>}
          </h2>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{ fontSize: 11, color: 'var(--txt-3)' }}>{visibleUsers.length} shown</span>
            {filterOrgId && (
              <button className="dm-btn" onClick={() => setFilterOrgId(null)} style={{ fontSize: 11 }}>Clear filter</button>
            )}
          </div>
        </div>
        <div className="dm-card" style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-1)' }}>
                {['Name', 'Email', 'Organization', 'Role', 'Status', ''].map(h => (
                  <th key={h} style={{ textAlign: 'left', padding: '10px 14px', color: 'var(--txt-3)', fontWeight: 500, fontSize: 11 }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {visibleUsers.map(u => (
                <tr key={u.id} style={{ borderBottom: '1px solid var(--border-0)' }}>
                  <td style={{ padding: '10px 14px', color: 'var(--txt-1)' }}>
                    {u.full_name}
                    {u.is_superadmin && (
                      <span style={{ marginLeft: 6, fontFamily: 'var(--font-mono)', fontSize: 9, color: 'var(--cyan)' }}>SUPERADMIN</span>
                    )}
                  </td>
                  <td style={{ padding: '10px 14px', color: 'var(--txt-3)' }}>{u.email}</td>
                  <td style={{ padding: '10px 14px', color: 'var(--txt-2)' }}>{u.organization_name}</td>
                  <td style={{ padding: '10px 14px', color: 'var(--txt-2)', textTransform: 'capitalize' as const }}>{u.role}</td>
                  <td style={{ padding: '10px 14px' }}><StatusTag active={u.is_active} /></td>
                  <td style={{ padding: '10px 14px', textAlign: 'right' }}>
                    <button className="dm-btn" onClick={() => toggleUser(u)} style={{ fontSize: 11 }}>
                      {u.is_active ? 'Deactivate' : 'Reactivate'}
                    </button>
                  </td>
                </tr>
              ))}
              {visibleUsers.length === 0 && (
                <tr><td colSpan={6} style={{ padding: 20, textAlign: 'center', color: 'var(--txt-3)' }}>No users found</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </main>
    </div>
  );
}
