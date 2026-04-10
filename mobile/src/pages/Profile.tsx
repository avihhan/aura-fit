import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../lib/api';

interface UserProfile {
  id: number;
  email: string;
  role: string;
  tenant_id: number;
  is_email_verified: boolean;
  created_at: string;
}

export default function Profile() {
  const navigate = useNavigate();
  const { user, accessToken } = useAuth();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!accessToken) return;
    apiFetch('/api/users/me', accessToken)
      .then((r) => r.json())
      .then((d) => setProfile(d.user ?? null))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [accessToken]);

  return (
    <div className="page">
      <header className="page-header">
        <h1>Profile</h1>
      </header>

      {loading ? (
        <p className="empty-text">Loading&hellip;</p>
      ) : (
        <section className="section">
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
