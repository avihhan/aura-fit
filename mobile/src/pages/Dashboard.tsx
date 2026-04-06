import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../lib/api';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';

interface NutritionLog {
  id: number;
  calories: number | null;
  protein: number | null;
  carbs: number | null;
  fats: number | null;
  logged_at: string;
}

interface Workout {
  id: number;
  workout_date: string;
}

interface StreakData {
  current_streak: number;
  longest_streak: number;
  total_workouts: number;
  badges: { key: string; label: string; icon: string }[];
  motivation: string;
}

export default function Dashboard() {
  const { user, accessToken } = useAuth();
  const [recentMeals, setRecentMeals] = useState<NutritionLog[]>([]);
  const [workouts, setWorkouts] = useState<Workout[]>([]);
  const [streak, setStreak] = useState<StreakData | null>(null);
  const [loadingN, setLoadingN] = useState(true);
  const [loadingW, setLoadingW] = useState(true);

  useEffect(() => {
    if (!accessToken) return;
    apiFetch('/api/nutrition', accessToken)
      .then((r) => {
        if (!r.ok) return null;
        return r.json();
      })
      .then((d) => { if (d) setRecentMeals(d.nutrition_logs ?? []); })
      .catch(() => {})
      .finally(() => setLoadingN(false));

    apiFetch('/api/workouts', accessToken)
      .then((r) => {
        if (!r.ok) return null;
        return r.json();
      })
      .then((d) => { if (d) setWorkouts(d.workouts ?? []); })
      .catch(() => {})
      .finally(() => setLoadingW(false));

    apiFetch('/api/streaks', accessToken)
      .then((r) => {
        if (!r.ok) return null;
        return r.json();
      })
      .then((d) => { if (d) setStreak(d); })
      .catch(() => {});
  }, [accessToken]);

  const today = new Date().toISOString().slice(0, 10);
  const todayMeals = recentMeals.filter((m) => m.logged_at?.startsWith(today));
  const totalCals = todayMeals.reduce((s, m) => s + (m.calories ?? 0), 0);
  const totalProtein = todayMeals.reduce((s, m) => s + (m.protein ?? 0), 0);

  const last7Days = Array.from({ length: 7 }, (_, i) => {
    const d = new Date();
    d.setDate(d.getDate() - (6 - i));
    const key = d.toISOString().slice(0, 10);
    const dayMeals = recentMeals.filter((m) => m.logged_at?.startsWith(key));
    return {
      day: d.toLocaleDateString('en-US', { weekday: 'short' }),
      cal: dayMeals.reduce((s, m) => s + (m.calories ?? 0), 0),
    };
  });

  const thisWeekWorkouts = workouts.filter((w) => {
    const d = new Date(w.workout_date);
    const now = new Date();
    const diffDays = (now.getTime() - d.getTime()) / 86400000;
    return diffDays >= 0 && diffDays < 7;
  });

  return (
    <div className="page">
      <header className="page-header">
        <h1>
          Hey{user?.email ? `, ${user.email.split('@')[0]}` : ''}
        </h1>
        <p className="text-muted">{new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}</p>
      </header>

      <div className="card-grid">
        <div className="card">
          <span className="card-label">Calories today</span>
          <span className="card-value">{totalCals}</span>
        </div>
        <div className="card">
          <span className="card-label">Protein today</span>
          <span className="card-value">{totalProtein}g</span>
        </div>
        <div className="card">
          <span className="card-label">Workouts (7d)</span>
          <span className="card-value">{loadingW ? '\u2014' : thisWeekWorkouts.length}</span>
        </div>
        <div className="card">
          <span className="card-label">Meals today</span>
          <span className="card-value">{loadingN ? '\u2014' : todayMeals.length}</span>
        </div>
      </div>

      {streak && (
        <section className="section">
          <div className="streak-banner">
            <div className="streak-fire">&#128293;</div>
            <div>
              <span className="streak-count">{streak.current_streak}-day streak</span>
              <span className="streak-msg">{streak.motivation}</span>
            </div>
          </div>
          {streak.badges.length > 0 && (
            <div className="badge-row">
              {streak.badges.map((b) => (
                <span key={b.key} className="badge-chip">{b.label}</span>
              ))}
            </div>
          )}
        </section>
      )}

      {last7Days.some((d) => d.cal > 0) && (
        <section className="section">
          <h2>Calorie Intake (7 days)</h2>
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={last7Days}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis dataKey="day" stroke="#64748b" fontSize={11} />
              <YAxis stroke="#64748b" fontSize={11} />
              <Tooltip
                contentStyle={{ background: '#1a1a2e', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, fontSize: 12 }}
                labelStyle={{ color: '#94a3b8' }}
              />
              <Bar dataKey="cal" fill="#6c63ff" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </section>
      )}
    </div>
  );
}
