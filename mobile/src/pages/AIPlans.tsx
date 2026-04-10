import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../lib/api';

interface Meal {
  meal: string;
  foods: string[];
  calories: number;
  protein_g: number;
  carbs_g: number;
  fats_g: number;
}

interface MealPlan {
  plan_name: string;
  meals: Meal[];
  daily_totals: { calories: number; protein_g: number; carbs_g: number; fats_g: number };
  _demo?: boolean;
}

interface WorkoutDay {
  day: string;
  focus: string;
  exercises: { name: string; sets: number; reps: string; rest_seconds: number }[];
}

interface WorkoutPlan {
  plan_name: string;
  goal: string;
  days: WorkoutDay[];
  _demo?: boolean;
}

interface AiMeta {
  provider: string;
  is_demo: boolean;
  warning?: string | null;
}

type Tab = 'meal' | 'workout';

export default function AIPlans() {
  const { accessToken } = useAuth();
  const [tab, setTab] = useState<Tab>('meal');

  const [mealGoal, setMealGoal] = useState('');
  const [mealPlan, setMealPlan] = useState<MealPlan | null>(null);
  const [loadingMeal, setLoadingMeal] = useState(false);
  const [mealError, setMealError] = useState('');
  const [mealWarning, setMealWarning] = useState('');

  const [workoutGoal, setWorkoutGoal] = useState('');
  const [workoutPlan, setWorkoutPlan] = useState<WorkoutPlan | null>(null);
  const [loadingWorkout, setLoadingWorkout] = useState(false);
  const [workoutError, setWorkoutError] = useState('');
  const [workoutWarning, setWorkoutWarning] = useState('');

  async function genMeal() {
    if (!accessToken) return;
    setLoadingMeal(true);
    setMealPlan(null);
    setMealError('');
    setMealWarning('');
    try {
      const res = await apiFetch('/api/ai/meal-plan', accessToken, {
        method: 'POST',
        body: JSON.stringify({ goal: mealGoal || undefined }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(data.error || 'Unable to generate meal plan');
      }
      const meta: AiMeta | undefined = data.ai_meta;
      if (meta?.warning) setMealWarning(meta.warning);
      if (!data.meal_plan) {
        throw new Error('Server returned an invalid meal plan response');
      }
      setMealPlan(data.meal_plan);
    } catch (err) {
      setMealError(err instanceof Error ? err.message : 'Unable to generate meal plan');
    }
    setLoadingMeal(false);
  }

  async function genWorkout() {
    if (!accessToken) return;
    setLoadingWorkout(true);
    setWorkoutPlan(null);
    setWorkoutError('');
    setWorkoutWarning('');
    try {
      const res = await apiFetch('/api/ai/workout-plan', accessToken, {
        method: 'POST',
        body: JSON.stringify({ goal: workoutGoal || undefined }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(data.error || 'Unable to generate workout plan');
      }
      const meta: AiMeta | undefined = data.ai_meta;
      if (meta?.warning) setWorkoutWarning(meta.warning);
      if (!data.workout_plan) {
        throw new Error('Server returned an invalid workout plan response');
      }
      setWorkoutPlan(data.workout_plan);
    } catch (err) {
      setWorkoutError(err instanceof Error ? err.message : 'Unable to generate workout plan');
    }
    setLoadingWorkout(false);
  }

  return (
    <div className="page">
      <header className="page-header">
        <h1>AI Plans</h1>
      </header>

      <div className="tab-group">
        <button className={`tab-btn${tab === 'meal' ? ' tab-btn--active' : ''}`} onClick={() => setTab('meal')}>Meal Plan</button>
        <button className={`tab-btn${tab === 'workout' ? ' tab-btn--active' : ''}`} onClick={() => setTab('workout')}>Workout Plan</button>
      </div>

      {tab === 'meal' && (
        <section className="section">
          <div className="mobile-form">
            <div className="form-group">
              <label htmlFor="ai-mg">Goal (optional)</label>
              <input id="ai-mg" value={mealGoal} onChange={(e) => setMealGoal(e.target.value)} placeholder="e.g. Lose weight" />
            </div>
            <button className="login-btn" onClick={genMeal} disabled={loadingMeal}>
              {loadingMeal ? 'Generating\u2026' : 'Generate'}
            </button>
          </div>
          {mealError && <p className="login-error" style={{ marginTop: '0.75rem' }}>{mealError}</p>}
          {mealWarning && <p className="ai-demo-tag">{mealWarning}</p>}

          {mealPlan && (
            <div style={{ marginTop: '1rem' }}>
              <h3 className="ai-title">{mealPlan.plan_name}</h3>
              {mealPlan._demo && <p className="ai-demo-tag">Demo — add Gemini API key for real plans</p>}

              {mealPlan.meals.map((m, i) => (
                <div key={i} className="ai-mobile-card">
                  <strong>{m.meal}</strong>
                  <ul>{m.foods.map((f, j) => <li key={j}>{f}</li>)}</ul>
                  <span className="ai-micro">{m.calories} kcal &middot; P{m.protein_g} C{m.carbs_g} F{m.fats_g}</span>
                </div>
              ))}

              {mealPlan.daily_totals && (
                <div className="ai-totals-mobile">
                  Daily: {mealPlan.daily_totals.calories} kcal &middot;
                  P{mealPlan.daily_totals.protein_g} C{mealPlan.daily_totals.carbs_g} F{mealPlan.daily_totals.fats_g}
                </div>
              )}
            </div>
          )}
        </section>
      )}

      {tab === 'workout' && (
        <section className="section">
          <div className="mobile-form">
            <div className="form-group">
              <label htmlFor="ai-wg">Goal (optional)</label>
              <input id="ai-wg" value={workoutGoal} onChange={(e) => setWorkoutGoal(e.target.value)} placeholder="e.g. Strength" />
            </div>
            <button className="login-btn" onClick={genWorkout} disabled={loadingWorkout}>
              {loadingWorkout ? 'Generating\u2026' : 'Generate'}
            </button>
          </div>
          {workoutError && <p className="login-error" style={{ marginTop: '0.75rem' }}>{workoutError}</p>}
          {workoutWarning && <p className="ai-demo-tag">{workoutWarning}</p>}

          {workoutPlan && (
            <div style={{ marginTop: '1rem' }}>
              <h3 className="ai-title">{workoutPlan.plan_name}</h3>
              {workoutPlan._demo && <p className="ai-demo-tag">Demo — add Gemini API key for real plans</p>}

              {workoutPlan.days.map((d, i) => (
                <div key={i} className="ai-mobile-card">
                  <strong>{d.day} — {d.focus}</strong>
                  {d.exercises.map((ex, j) => (
                    <div key={j} className="ai-exercise-row">
                      <span>{ex.name}</span>
                      <span className="ai-micro">{ex.sets}×{ex.reps}</span>
                    </div>
                  ))}
                </div>
              ))}
            </div>
          )}
        </section>
      )}
    </div>
  );
}
