import { useEffect, useState, type FormEvent } from 'react';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../lib/api';

interface Goal {
  id: number;
  goal_type: string;
  target_value: number | null;
  start_date: string | null;
  end_date: string | null;
  status: string;
}

export default function Goals() {
  const { accessToken } = useAuth();
  const [goals, setGoals] = useState<Goal[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [goalType, setGoalType] = useState('');
  const [target, setTarget] = useState('');
  const [saving, setSaving] = useState(false);

  function fetchGoals() {
    if (!accessToken) return;
    apiFetch('/api/goals', accessToken)
      .then((r) => r.json())
      .then((d) => setGoals(d.goals ?? []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }

  useEffect(fetchGoals, [accessToken]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!accessToken || !goalType.trim()) return;
    setSaving(true);

    await apiFetch('/api/goals', accessToken, {
      method: 'POST',
      body: JSON.stringify({
        goal_type: goalType.trim(),
        target_value: target ? Number(target) : undefined,
        start_date: new Date().toISOString().slice(0, 10),
        status: 'active',
      }),
    });

    setGoalType('');
    setTarget('');
    setSaving(false);
    setShowForm(false);
    fetchGoals();
  }

  async function markComplete(id: number) {
    if (!accessToken) return;
    await apiFetch(`/api/goals/${id}`, accessToken, {
      method: 'PUT',
      body: JSON.stringify({ status: 'completed' }),
    });
    fetchGoals();
  }

  const active = goals.filter((g) => g.status === 'active');
  const completed = goals.filter((g) => g.status === 'completed');

  return (
    <div className="page">
      <header className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>Goals</h1>
        <button className="action-btn" onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : '+ New'}
        </button>
      </header>

      {showForm && (
        <section className="section">
          <form onSubmit={handleSubmit} className="mobile-form">
            <div className="form-group">
              <label htmlFor="g-type">Goal Type</label>
              <input id="g-type" value={goalType} onChange={(e) => setGoalType(e.target.value)} placeholder="e.g. Lose weight, Run 5k" disabled={saving} />
            </div>
            <div className="form-group">
              <label htmlFor="g-target">Target Value (optional)</label>
              <input id="g-target" type="number" value={target} onChange={(e) => setTarget(e.target.value)} placeholder="e.g. 150" disabled={saving} />
            </div>
            <button type="submit" className="login-btn" disabled={saving || !goalType.trim()}>
              {saving ? 'Saving\u2026' : 'Create Goal'}
            </button>
          </form>
        </section>
      )}

      {loading ? (
        <p className="empty-text">Loading&hellip;</p>
      ) : goals.length === 0 ? (
        <section className="section"><p className="empty-text">No goals set yet.</p></section>
      ) : (
        <>
          {active.length > 0 && (
            <section className="section">
              <h2>Active ({active.length})</h2>
              {active.map((goal) => (
                <div key={goal.id} className="goal-row">
                  <div>
                    <span className="log-primary">{goal.goal_type}</span>
                    {goal.target_value != null && (
                      <span className="log-secondary"> Target: {goal.target_value}</span>
                    )}
                  </div>
                  <button className="action-btn action-btn--sm" onClick={() => markComplete(goal.id)}>
                    Done
                  </button>
                </div>
              ))}
            </section>
          )}
          {completed.length > 0 && (
            <section className="section">
              <h2>Completed ({completed.length})</h2>
              {completed.map((goal) => (
                <div key={goal.id} className="goal-row goal-row--done">
                  <span className="log-primary">{goal.goal_type}</span>
                </div>
              ))}
            </section>
          )}
        </>
      )}
    </div>
  );
}
