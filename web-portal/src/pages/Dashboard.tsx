import { useAuth } from '../context/AuthContext';

export default function Dashboard() {
  const { user, tenant } = useAuth();

  const stats = [
    { label: 'Active Members', value: '\u2014', note: 'Connect data source' },
    { label: 'Workouts This Week', value: '\u2014', note: 'Connect data source' },
    { label: 'Revenue (MTD)', value: '\u2014', note: 'Connect data source' },
    { label: 'New Sign-ups', value: '\u2014', note: 'Connect data source' },
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
            <span className="stat-note">{s.note}</span>
          </div>
        ))}
      </div>

      <section className="dashboard-section">
        <h2>Recent Activity</h2>
        <div className="empty-state">
          <p>
            No activity data yet. Connect your data sources to populate this
            dashboard.
          </p>
        </div>
      </section>
    </div>
  );
}
