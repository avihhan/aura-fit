import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../lib/api';

interface PlatformStats {
  total_tenants: number;
  total_users: number;
  total_owners: number;
  total_members: number;
}

export default function PlatformDashboard() {
  const { accessToken } = useAuth();
  const [stats, setStats] = useState<PlatformStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!accessToken) return;
    apiFetch('/api/platform/analytics', accessToken)
      .then((res) => res.json())
      .then(setStats)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [accessToken]);

  const cards = stats
    ? [
        { label: 'Total Tenants', value: stats.total_tenants },
        { label: 'Total Users', value: stats.total_users },
        { label: 'Tenant Owners', value: stats.total_owners },
        { label: 'Members', value: stats.total_members },
      ]
    : [];

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div>
          <h1>Platform Administration</h1>
          <p className="dashboard-subtitle">
            AuraFit Platform &middot; Super Admin
          </p>
        </div>
      </header>

      {loading ? (
        <div className="empty-state">
          <p>Loading platform data&hellip;</p>
        </div>
      ) : (
        <>
          <div className="stats-grid">
            {cards.map((c) => (
              <div key={c.label} className="stat-card">
                <span className="stat-value">{c.value}</span>
                <span className="stat-label">{c.label}</span>
              </div>
            ))}
          </div>

          <section className="dashboard-section">
            <h2>Quick Actions</h2>
            <div className="empty-state">
              <p>
                Manage tenants, view analytics, and configure platform settings
                from the sidebar.
              </p>
            </div>
          </section>
        </>
      )}
    </div>
  );
}
