import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { apiFetch, apiUpdateEmailNotifications } from '../lib/api';

interface UserProfile {
  id: number;
  email: string;
  role: string;
  tenant_id: number;
  is_email_verified: boolean;
  created_at: string;
  email_notifications_enabled: boolean;
}

export default function Profile() {
  const navigate = useNavigate();
  const { user, accessToken } = useAuth();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [savingNotifications, setSavingNotifications] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!accessToken) return;
    apiFetch('/api/users/me', accessToken)
      .then((r) => r.json())
      .then((d) => setProfile(d.user ?? null))
      .catch((err) =>
        setError(err instanceof Error ? err.message : 'Unable to load profile'),
      )
      .finally(() => setLoading(false));
  }, [accessToken]);

  async function toggleEmailNotifications(enabled: boolean) {
    if (!accessToken || !profile) return;
    setSavingNotifications(true);
    setError('');
    try {
      const updated = await apiUpdateEmailNotifications(accessToken, enabled);
      setProfile((prev) => (prev ? { ...prev, email_notifications_enabled: updated } : prev));
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Unable to update notifications setting',
      );
    } finally {
      setSavingNotifications(false);
    }
  }

  return (
    <div className="page">
      <header className="page-header">
        <h1>Profile</h1>
      </header>

      {loading ? (
        <p className="empty-text">Loading&hellip;</p>
      ) : (
        <section className="section">
          {error && <div className="login-error">{error}</div>}
          <div className="profile-card">
            <div className="profile-avatar">
              {(user?.email ?? 'U').charAt(0).toUpperCase()}
            </div>
            <div className="profile-info">
              <span className="profile-name">{profile?.email ?? user?.email ?? 'User'}</span>
              <span className="profile-role">{profile?.role ?? 'member'}</span>
            </div>
          </div>

          <div className="profile-details">
            <div className="profile-row">
              <span className="profile-label">Email</span>
              <span className="profile-value">{profile?.email ?? '\u2014'}</span>
            </div>
            <div className="profile-row">
              <span className="profile-label">Verified</span>
              <span className="profile-value">{profile?.is_email_verified ? 'Yes' : 'No'}</span>
            </div>
            <div className="profile-row">
              <span className="profile-label">Tenant ID</span>
              <span className="profile-value">{profile?.tenant_id ?? '\u2014'}</span>
            </div>
            <div className="profile-row">
              <span className="profile-label">Joined</span>
              <span className="profile-value">{profile?.created_at ? new Date(profile.created_at).toLocaleDateString() : '\u2014'}</span>
            </div>
            <div className="profile-row">
              <span className="profile-label">Email Notifications</span>
              <label style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}>
                <input
                  type="checkbox"
                  checked={Boolean(profile?.email_notifications_enabled)}
                  disabled={savingNotifications}
                  onChange={(e) => void toggleEmailNotifications(e.target.checked)}
                />
                <span className="profile-value">
                  {profile?.email_notifications_enabled ? 'Enabled' : 'Disabled'}
                </span>
              </label>
            </div>
          </div>

          <div className="profile-nav">
            <button className="profile-nav-btn" onClick={() => navigate('/goals')}>Goals</button>
            <button className="profile-nav-btn" onClick={() => navigate('/ai-plans')}>AI Plans</button>
            <button className="profile-nav-btn" onClick={() => navigate('/calendar')}>Calendar</button>
            <button className="profile-nav-btn" onClick={() => navigate('/notifications')}>Notifications</button>
          </div>

        </section>
      )}
    </div>
  );
}
