import { useEffect, useState, type FormEvent } from 'react';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../lib/api';

interface Branding {
  id: number;
  name: string;
  logo_url: string | null;
  primary_color: string | null;
  secondary_color: string | null;
  custom_domain: string | null;
}

export default function Settings() {
  const { user, accessToken } = useAuth();
  const [branding, setBranding] = useState<Branding | null>(null);
  const [name, setName] = useState('');
  const [logoUrl, setLogoUrl] = useState('');
  const [primaryColor, setPrimaryColor] = useState('#6c63ff');
  const [secondaryColor, setSecondaryColor] = useState('#1a1a2e');
  const [customDomain, setCustomDomain] = useState('');
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [summaryStatus, setSummaryStatus] = useState('');

  useEffect(() => {
    if (!accessToken) return;
    apiFetch('/api/admin/branding', accessToken)
      .then((r) => r.json())
      .then((d) => {
        const b = d.branding;
        if (b) {
          setBranding(b);
          setName(b.name ?? '');
          setLogoUrl(b.logo_url ?? '');
          setPrimaryColor(b.primary_color ?? '#6c63ff');
          setSecondaryColor(b.secondary_color ?? '#1a1a2e');
          setCustomDomain(b.custom_domain ?? '');
        }
      })
      .catch(() => {});
  }, [accessToken]);

  async function handleSave(e: FormEvent) {
    e.preventDefault();
    if (!accessToken) return;
    setSaving(true);
    setSaved(false);

    await apiFetch('/api/admin/branding', accessToken, {
      method: 'PUT',
      body: JSON.stringify({
        name: name.trim(),
        logo_url: logoUrl.trim() || null,
        primary_color: primaryColor,
        secondary_color: secondaryColor,
        custom_domain: customDomain.trim() || null,
      }),
    });

    setSaving(false);
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  }

  async function handleSendSummaries() {
    if (!accessToken) return;
    setSummaryStatus('Sending...');
    try {
      const res = await apiFetch('/api/admin/weekly-summary', accessToken, {
        method: 'POST',
      });
      const data = await res.json();
      setSummaryStatus(`Sent to ${data.sent}/${data.total_members} members`);
    } catch {
      setSummaryStatus('Failed to send');
    }
    setTimeout(() => setSummaryStatus(''), 5000);
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Settings</h1>
        <p className="dashboard-subtitle">
          {branding?.name ?? 'Organization'} configuration
        </p>
      </header>

      <section className="dashboard-section">
        <h2>Account</h2>
        <div className="settings-row">
          <span className="settings-label">Email</span>
          <span className="settings-value">{user?.email}</span>
        </div>
        <div className="settings-row">
          <span className="settings-label">Role</span>
          <span className="settings-value">{user?.role}</span>
        </div>
        <div className="settings-row">
          <span className="settings-label">Tenant ID</span>
          <span className="settings-value">{user?.tenant_id}</span>
        </div>
      </section>

      <section className="dashboard-section" style={{ marginTop: '1rem' }}>
        <h2>Branding</h2>
        <form onSubmit={handleSave} className="settings-form">
          <div className="form-group">
            <label htmlFor="s-name">Organization Name</label>
            <input id="s-name" value={name} onChange={(e) => setName(e.target.value)} disabled={saving} />
          </div>
          <div className="form-group">
            <label htmlFor="s-logo">Logo URL</label>
            <input id="s-logo" value={logoUrl} onChange={(e) => setLogoUrl(e.target.value)} placeholder="https://..." disabled={saving} />
          </div>
          <div className="form-row" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="form-group">
              <label htmlFor="s-pc">Primary Color</label>
              <div className="color-input-wrap">
                <input id="s-pc" type="color" value={primaryColor} onChange={(e) => setPrimaryColor(e.target.value)} disabled={saving} />
                <span className="color-hex">{primaryColor}</span>
              </div>
            </div>
            <div className="form-group">
              <label htmlFor="s-sc">Secondary Color</label>
              <div className="color-input-wrap">
                <input id="s-sc" type="color" value={secondaryColor} onChange={(e) => setSecondaryColor(e.target.value)} disabled={saving} />
                <span className="color-hex">{secondaryColor}</span>
              </div>
            </div>
          </div>
          <div className="form-group">
            <label htmlFor="s-domain">Custom Domain</label>
            <input id="s-domain" value={customDomain} onChange={(e) => setCustomDomain(e.target.value)} placeholder="app.yourfitness.com" disabled={saving} />
          </div>

          {logoUrl && (
            <div className="logo-preview">
              <img src={logoUrl} alt="Logo preview" onError={(e) => (e.currentTarget.style.display = 'none')} />
            </div>
          )}

          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <button type="submit" className="login-btn" style={{ padding: '0.5rem 1.5rem', fontSize: '0.8125rem' }} disabled={saving}>
              {saving ? 'Saving\u2026' : 'Save Branding'}
            </button>
            {saved && <span className="save-badge">Saved!</span>}
          </div>
        </form>
      </section>

      <section className="dashboard-section" style={{ marginTop: '1rem' }}>
        <h2>Engagement</h2>
        <p style={{ fontSize: '0.875rem', color: '#94a3b8', marginBottom: '0.75rem' }}>
          Send a weekly progress summary email to all your members.
        </p>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <button className="login-btn" style={{ padding: '0.5rem 1rem', fontSize: '0.8125rem' }} onClick={handleSendSummaries} disabled={summaryStatus === 'Sending...'}>
            {summaryStatus === 'Sending...' ? 'Sending\u2026' : 'Send Weekly Summaries'}
          </button>
          {summaryStatus && summaryStatus !== 'Sending...' && (
            <span className="save-badge">{summaryStatus}</span>
          )}
        </div>
      </section>
    </div>
  );
}
