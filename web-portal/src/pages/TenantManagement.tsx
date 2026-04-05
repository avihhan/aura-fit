import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../lib/api';

interface TenantRow {
  id: string;
  name: string;
  email: string;
  ai_enabled: boolean;
  logo_url: string | null;
  primary_color: string | null;
  secondary_color: string | null;
  custom_domain: string | null;
  created_at: string;
}

export default function TenantManagement() {
  const { accessToken } = useAuth();
  const [tenants, setTenants] = useState<TenantRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!accessToken) return;
    apiFetch('/api/platform/tenants', accessToken)
      .then((res) => res.json())
      .then((data) => setTenants(data.tenants ?? []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [accessToken]);

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div>
          <h1>Tenant Management</h1>
          <p className="dashboard-subtitle">
            {tenants.length} organization{tenants.length !== 1 ? 's' : ''}{' '}
            registered
          </p>
        </div>
      </header>

      {loading ? (
        <div className="empty-state">
          <p>Loading tenants&hellip;</p>
        </div>
      ) : tenants.length === 0 ? (
        <div className="empty-state">
          <p>No tenants found.</p>
        </div>
      ) : (
        <section className="dashboard-section">
          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>AI</th>
              </tr>
            </thead>
            <tbody>
              {tenants.map((t) => (
                <tr key={t.id}>
                  <td>{t.id}</td>
                  <td>{t.name}</td>
                  <td>{t.email}</td>
                  <td>{t.ai_enabled ? 'On' : 'Off'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}
    </div>
  );
}
