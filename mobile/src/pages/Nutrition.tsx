import { useEffect, useState, type FormEvent } from 'react';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../lib/api';

interface NutritionLog {
  id: number;
  meal_type: string | null;
  calories: number | null;
  protein: number | null;
  carbs: number | null;
  fats: number | null;
  logged_at: string;
}

const MEAL_TYPES = ['Breakfast', 'Lunch', 'Dinner', 'Snack'];

export default function Nutrition() {
  const { accessToken } = useAuth();
  const [logs, setLogs] = useState<NutritionLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [mealType, setMealType] = useState('Lunch');
  const [calories, setCalories] = useState('');
  const [protein, setProtein] = useState('');
  const [carbs, setCarbs] = useState('');
  const [fats, setFats] = useState('');
  const [saving, setSaving] = useState(false);

  function fetchLogs() {
    if (!accessToken) return;
    apiFetch('/api/nutrition', accessToken)
      .then((r) => r.json())
      .then((d) => setLogs(d.nutrition_logs ?? []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }

  useEffect(fetchLogs, [accessToken]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!accessToken) return;
    setSaving(true);

    await apiFetch('/api/nutrition', accessToken, {
      method: 'POST',
      body: JSON.stringify({
        logged_at: new Date().toISOString(),
        meal_type: mealType,
        calories: calories ? Number(calories) : undefined,
        protein: protein ? Number(protein) : undefined,
        carbs: carbs ? Number(carbs) : undefined,
        fats: fats ? Number(fats) : undefined,
      }),
    });

    setCalories('');
    setProtein('');
    setCarbs('');
    setFats('');
    setSaving(false);
    setShowForm(false);
    fetchLogs();
  }

  const todayLogs = logs.filter(
    (l) => l.logged_at?.startsWith(new Date().toISOString().slice(0, 10)),
  );
  const todayCals = todayLogs.reduce((s, l) => s + (l.calories ?? 0), 0);
  const todayProtein = todayLogs.reduce((s, l) => s + (l.protein ?? 0), 0);
  const todayCarbs = todayLogs.reduce((s, l) => s + (l.carbs ?? 0), 0);
  const todayFats = todayLogs.reduce((s, l) => s + (l.fats ?? 0), 0);

  return (
    <div className="page">
      <header className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>Nutrition</h1>
        <button className="action-btn" onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : '+ Log'}
        </button>
      </header>

      <div className="card-grid">
        <div className="card"><span className="card-label">Calories</span><span className="card-value">{todayCals}</span></div>
        <div className="card"><span className="card-label">Protein</span><span className="card-value">{todayProtein}g</span></div>
        <div className="card"><span className="card-label">Carbs</span><span className="card-value">{todayCarbs}g</span></div>
        <div className="card"><span className="card-label">Fats</span><span className="card-value">{todayFats}g</span></div>
      </div>

      {showForm && (
        <section className="section">
          <form onSubmit={handleSubmit} className="mobile-form">
            <div className="form-group">
              <label htmlFor="n-meal">Meal</label>
              <select id="n-meal" value={mealType} onChange={(e) => setMealType(e.target.value)} disabled={saving} className="form-select">
                {MEAL_TYPES.map((m) => <option key={m}>{m}</option>)}
              </select>
            </div>
            <div className="form-row-2">
              <div className="form-group">
                <label htmlFor="n-cal">Calories</label>
                <input id="n-cal" type="number" value={calories} onChange={(e) => setCalories(e.target.value)} disabled={saving} />
              </div>
              <div className="form-group">
                <label htmlFor="n-pro">Protein (g)</label>
                <input id="n-pro" type="number" value={protein} onChange={(e) => setProtein(e.target.value)} disabled={saving} />
              </div>
            </div>
            <div className="form-row-2">
              <div className="form-group">
                <label htmlFor="n-car">Carbs (g)</label>
                <input id="n-car" type="number" value={carbs} onChange={(e) => setCarbs(e.target.value)} disabled={saving} />
              </div>
              <div className="form-group">
                <label htmlFor="n-fat">Fats (g)</label>
                <input id="n-fat" type="number" value={fats} onChange={(e) => setFats(e.target.value)} disabled={saving} />
              </div>
            </div>
            <button type="submit" className="login-btn" disabled={saving}>
              {saving ? 'Saving\u2026' : 'Log Meal'}
            </button>
          </form>
        </section>
      )}

      {loading ? (
        <p className="empty-text">Loading&hellip;</p>
      ) : logs.length === 0 ? (
        <section className="section"><p className="empty-text">No meals logged yet.</p></section>
      ) : (
        <section className="section">
          <h2>Recent Meals</h2>
          {logs.slice(0, 20).map((l) => (
            <div key={l.id} className="log-row">
              <div>
                <span className="log-primary">{l.meal_type ?? 'Meal'}</span>
                <span className="log-secondary">{l.logged_at?.slice(0, 10)}</span>
              </div>
              <span className="log-value">{l.calories ?? 0} kcal</span>
            </div>
          ))}
        </section>
      )}
    </div>
  );
}
