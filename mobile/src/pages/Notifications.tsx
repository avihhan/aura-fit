import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../lib/api';

interface Notification {
  id: number;
  title: string | null;
  message: string | null;
  is_read: boolean;
  created_at: string;
}

export default function Notifications() {
  const { accessToken } = useAuth();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);

  function fetchNotifications() {
    if (!accessToken) return;
    apiFetch('/api/notifications', accessToken)
      .then((r) => r.json())
      .then((d) => setNotifications(d.notifications ?? []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }

  useEffect(fetchNotifications, [accessToken]);

  async function markRead(id: number) {
    if (!accessToken) return;
    await apiFetch(`/api/notifications/${id}/read`, accessToken, {
      method: 'PUT',
    });
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, is_read: true } : n)),
    );
  }

  const unread = notifications.filter((n) => !n.is_read);
  const read = notifications.filter((n) => n.is_read);

  return (
    <div className="page">
      <header className="page-header">
        <h1>Notifications</h1>
        {unread.length > 0 && (
          <span className="notif-badge">{unread.length} new</span>
        )}
      </header>

      {loading ? (
        <p className="empty-text">Loading&hellip;</p>
      ) : notifications.length === 0 ? (
        <section className="section">
          <p className="empty-text">No notifications yet.</p>
        </section>
      ) : (
        <>
          {unread.length > 0 && (
            <section className="section">
              <h2>New</h2>
              {unread.map((n) => (
                <button
                  key={n.id}
                  className="notif-card notif-card--unread"
                  onClick={() => markRead(n.id)}
                >
                  <div className="notif-header">
                    <span className="notif-title">{n.title ?? 'Notification'}</span>
                    <span className="notif-time">
                      {new Date(n.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  {n.message && <p className="notif-body">{n.message}</p>}
                </button>
              ))}
            </section>
          )}

          {read.length > 0 && (
            <section className="section">
              <h2>Earlier</h2>
              {read.map((n) => (
                <div key={n.id} className="notif-card">
                  <div className="notif-header">
                    <span className="notif-title">{n.title ?? 'Notification'}</span>
                    <span className="notif-time">
                      {new Date(n.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  {n.message && <p className="notif-body">{n.message}</p>}
                </div>
              ))}
            </section>
          )}
        </>
      )}
    </div>
  );
}
