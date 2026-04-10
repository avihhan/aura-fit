import { lazy, Suspense, useEffect, useState, type FormEvent } from 'react';
import { useAuth } from '../context/AuthContext';
import {
  apiFetch,
  apiFetchJson,
  getApiCache,
  invalidateApiCache,
} from '../lib/api';

const BodyMetricsChart = lazy(() => import('../components/charts/BodyMetricsChart'));

interface Metric {
  id: number;
  weight: number | null;
  height: number | null;
  height_feet: number | null;
  height_inches: number | null;
  body_fat_percentage: number | null;
  recorded_at: string;
}

export default function BodyMetrics() {
  const { accessToken } = useAuth();
  const [metrics, setMetrics] = useState<Metric[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [weight, setWeight] = useState('');
  const [heightFeet, setHeightFeet] = useState('');
  const [heightInches, setHeightInches] = useState('');
  const [bodyFat, setBodyFat] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  function fetchMetrics() {
    if (!accessToken) return;
    const cached = getApiCache<{ body_metrics?: Metric[] }>(
      '/api/body-metrics',
      accessToken,
      45000,
    );
    if (cached) {
      setMetrics(cached.data.body_metrics ?? []);
      setLoading(false);
    }

    apiFetchJson<{ body_metrics?: Metric[] }>('/api/body-metrics', accessToken, {
      forceRefresh: true,
      retries: 1,
    })
      .then((d) => setMetrics(d.body_metrics ?? []))
      .catch((err) => {
        setError(err instanceof Error ? err.message : 'Unable to load body metrics');
      })
      .finally(() => setLoading(false));
  }

  useEffect(fetchMetrics, [accessToken]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!accessToken) return;
    setSaving(true);
    setError('');

    try {
      await apiFetch('/api/body-metrics', accessToken, {
        method: 'POST',
        body: JSON.stringify({
          recorded_at: new Date().toISOString(),
          weight: weight ? Number(weight) : undefined,
          height_feet: heightFeet ? Number(heightFeet) : undefined,
          height_inches: heightInches ? Number(heightInches) : undefined,
          body_fat_percentage: bodyFat ? Number(bodyFat) : undefined,
        }),
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to save body metric');
    }

    setWeight('');
    setHeightFeet('');
    setHeightInches('');
    setBodyFat('');
    setSaving(false);
    setShowForm(false);
    invalidateApiCache('/api/body-metrics', accessToken);
    fetchMetrics();
  }

  const chartData = [...metrics]
    .reverse()
    .map((m) => ({
      date: m.recorded_at?.slice(5, 10),
      weight: m.weight,
      bf: m.body_fat_percentage,
    }));

  function formatHeight(metric: Metric) {
    if (metric.height_feet != null || metric.height_inches != null) {
      return `${metric.height_feet ?? 0} ft ${metric.height_inches ?? 0} in`;
    }
    if (metric.height != null) {
      return `${metric.height} in`;
    }
    return '--';
  }

  return (
    <div className="page">
      <header className="page-header page-header-row">
        <h1>Body Metrics</h1>
        <button className="action-btn" onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : '+ Log'}
        </button>
      </header>

      {error && (
        <section className="section">
          <p className="empty-text" style={{ color: '#fca5a5' }}>{error}</p>
        </section>
      )}

      {showForm && (
        <section className="section">
          <form onSubmit={handleSubmit} className="mobile-form">
            <div className="form-row-3">
              <div className="form-group">
                <label htmlFor="bm-wt">Weight</label>
                <input id="bm-wt" type="number" step="0.1" value={weight} onChange={(e) => setWeight(e.target.value)} disabled={saving} />
              </div>
              <div className="form-group">
                <label htmlFor="bm-ft">Height (ft)</label>
                <input id="bm-ft" type="number" min="0" max="9" value={heightFeet} onChange={(e) => setHeightFeet(e.target.value)} disabled={saving} />
              </div>
              <div className="form-group">
                <label htmlFor="bm-in">Height (in)</label>
                <input id="bm-in" type="number" min="0" max="11" value={heightInches} onChange={(e) => setHeightInches(e.target.value)} disabled={saving} />
              </div>
            </div>
            <div className="form-row-2">
              <div className="form-group">
                <label htmlFor="bm-bf">Body Fat %</label>
                <input id="bm-bf" type="number" step="0.1" value={bodyFat} onChange={(e) => setBodyFat(e.target.value)} disabled={saving} />
              </div>
            </div>
            <button type="submit" className="login-btn" disabled={saving}>
              {saving ? 'Saving\u2026' : 'Save'}
            </button>
          </form>
        </section>
      )}

      {chartData.length > 1 && (
        <section className="section">
          <h2>Weight Trend</h2>
          <Suspense fallback={<div className="skeleton-chart" />}>
            <BodyMetricsChart data={chartData} />
          </Suspense>
        </section>
      )}

      {loading ? (
        <section className="section">
          <div className="skeleton-line skeleton-line--lg" />
          <div className="skeleton-line" />
          <div className="skeleton-line" />
        </section>
      ) : metrics.length === 0 ? (
        <section className="section"><p className="empty-text">No metrics logged yet.</p></section>
      ) : (
        <section className="section">
          <h2>History</h2>
          {metrics.slice(0, 20).map((m) => (
            <div key={m.id} className="card" style={{ marginBottom: '0.6rem' }}>
              <div>
                <span className="log-primary">{new Date(m.recorded_at).toLocaleString()}</span>
              </div>
              <div className="metric-row-grid">
                <span className="log-secondary">Weight</span>
                <span className="log-value">{m.weight != null ? `${m.weight} lbs` : '--'}</span>
                <span className="log-secondary">Height</span>
                <span className="log-value">{formatHeight(m)}</span>
                <span className="log-secondary">Body Fat</span>
                <span className="log-value">{m.body_fat_percentage != null ? `${m.body_fat_percentage}%` : '--'}</span>
              </div>
            </div>
          ))}
        </section>
      )}
    </div>
  );
}
