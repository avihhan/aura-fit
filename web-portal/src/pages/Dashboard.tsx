import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../lib/api';

interface Analytics {
  total_members: number;
  total_workouts: number;
  active_subscriptions: number;
}

export default function Dashboard() {
  const { user, tenant, accessToken } = useAuth();
  const [analytics, setAnalytics] = useState<Analytics | null>(null);

  useEffect(() => {
    if (!accessToken) return;
    apiFetch('/api/admin/analytics', accessToken)
      .then((r) => r.json())
      .then(setAnalytics)
      .catch(() => {});
  }, [accessToken]);

  const stats = [
    { label: 'Active Members', value: analytics?.total_members ?? '\u2014' },
    { label: 'Total Workouts', value: analytics?.total_workouts ?? '\u2014' },
    { label: 'Active Subscriptions', value: analytics?.active_subscriptions ?? '\u2014' },
  ];

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div>
          <h1>
            Welcome back
            {user?.email ? `, ${user.email.split('@')[0]}` : ''}
          </h1>
          <p className="dashboard-subtitle">
            {tenant?.name ?? 'Your Organization'} &middot; Admin Dashboard
          </p>
        </div>
      </header>

      <div className="stats-grid">
        {stats.map((s) => (
          <div key={s.label} className="stat-card">
            <span className="stat-value">{s.value}</span>
            <span className="stat-label">{s.label}</span>
          </div>
        ))}
      </div>

      <section className="dashboard-section">
        <h2>Recent Activity</h2>
        <div className="empty-state">
          <p>
            Activity feed will show recent member signups, workouts, and
            milestones.
          </p>
        </div>
      </section>
    </div>
  );
}
