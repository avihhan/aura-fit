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
  exercises: { name: string; sets: number; reps: string; rest_seconds: number; notes: string }[];
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
  const [dietaryPrefs, setDietaryPrefs] = useState('');
  const [mealPlan, setMealPlan] = useState<MealPlan | null>(null);
  const [loadingMeal, setLoadingMeal] = useState(false);
  const [mealError, setMealError] = useState('');
  const [mealWarning, setMealWarning] = useState('');

  const [workoutGoal, setWorkoutGoal] = useState('');
  const [fitnessLevel, setFitnessLevel] = useState('intermediate');
  const [workoutPlan, setWorkoutPlan] = useState<WorkoutPlan | null>(null);
  const [loadingWorkout, setLoadingWorkout] = useState(false);
  const [workoutError, setWorkoutError] = useState('');
  const [workoutWarning, setWorkoutWarning] = useState('');

  async function generateMealPlan() {
    if (!accessToken) return;
    setLoadingMeal(true);
    setMealPlan(null);
    setMealError('');
    setMealWarning('');
    try {
      const res = await apiFetch('/api/ai/meal-plan', accessToken, {
        method: 'POST',
        body: JSON.stringify({
          goal: mealGoal || undefined,
          dietary_prefs: dietaryPrefs || undefined,
        }),
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

  async function generateWorkoutPlan() {
    if (!accessToken) return;
    setLoadingWorkout(true);
    setWorkoutPlan(null);
    setWorkoutError('');
    setWorkoutWarning('');
    try {
      const res = await apiFetch('/api/ai/workout-plan', accessToken, {
        method: 'POST',
        body: JSON.stringify({
          goal: workoutGoal || undefined,
          fitness_level: fitnessLevel || undefined,
        }),
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
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>AI Plan Generator</h1>
        <p className="dashboard-subtitle">
          Generate personalised meal and workout plans powered by AI
        </p>
      </header>

      <div className="login-toggle-group" style={{ marginBottom: '1.5rem' }}>
        <button className={`login-toggle${tab === 'meal' ? ' active' : ''}`} onClick={() => setTab('meal')}>Meal Plan</button>
        <button className={`login-toggle${tab === 'workout' ? ' active' : ''}`} onClick={() => setTab('workout')}>Workout Plan</button>
      </div>

      {tab === 'meal' && (
        <section className="dashboard-section">
          <h2>Generate Meal Plan</h2>
          <div className="ai-form">
            <div className="form-group">
              <label htmlFor="ai-mg">Goal (optional)</label>
              <input id="ai-mg" value={mealGoal} onChange={(e) => setMealGoal(e.target.value)} placeholder="e.g. Lose weight, Build muscle" />
            </div>
            <div className="form-group">
              <label htmlFor="ai-dp">Dietary Preferences</label>
              <input id="ai-dp" value={dietaryPrefs} onChange={(e) => setDietaryPrefs(e.target.value)} placeholder="e.g. Vegetarian, Gluten-free" />
            </div>
            <button className="login-btn" style={{ padding: '0.5rem 1rem', fontSize: '0.8125rem' }} onClick={generateMealPlan} disabled={loadingMeal}>
              {loadingMeal ? 'Generating\u2026' : 'Generate Meal Plan'}
            </button>
          </div>
          {mealError && <p className="ai-demo-badge">{mealError}</p>}
          {mealWarning && <p className="ai-demo-badge">{mealWarning}</p>}

          {mealPlan && (
            <div className="ai-result" style={{ marginTop: '1.5rem' }}>
              <h3>{mealPlan.plan_name}</h3>
              {mealPlan._demo && <p className="ai-demo-badge">Demo plan — add a Gemini API key for real AI generation</p>}

              {mealPlan.meals.map((m, i) => (
                <div key={i} className="ai-card">
                  <strong>{m.meal}</strong>
                  <ul>{m.foods.map((f, j) => <li key={j}>{f}</li>)}</ul>
                  <span className="ai-macros">
                    {m.calories} kcal &middot; P {m.protein_g}g &middot; C {m.carbs_g}g &middot; F {m.fats_g}g
                  </span>
                </div>
              ))}

              {mealPlan.daily_totals && (
                <div className="ai-totals">
                  <strong>Daily Totals:</strong>{' '}
                  {mealPlan.daily_totals.calories} kcal &middot;
                  P {mealPlan.daily_totals.protein_g}g &middot;
                  C {mealPlan.daily_totals.carbs_g}g &middot;
                  F {mealPlan.daily_totals.fats_g}g
                </div>
              )}
            </div>
          )}
        </section>
      )}

      {tab === 'workout' && (
        <section className="dashboard-section">
          <h2>Generate Workout Plan</h2>
          <div className="ai-form">
            <div className="form-group">
              <label htmlFor="ai-wg">Goal (optional)</label>
              <input id="ai-wg" value={workoutGoal} onChange={(e) => setWorkoutGoal(e.target.value)} placeholder="e.g. Hypertrophy, Strength, Weight loss" />
            </div>
            <div className="form-group">
              <label htmlFor="ai-fl">Fitness Level</label>
              <select id="ai-fl" value={fitnessLevel} onChange={(e) => setFitnessLevel(e.target.value)}>
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
            </div>
            <button className="login-btn" style={{ padding: '0.5rem 1rem', fontSize: '0.8125rem' }} onClick={generateWorkoutPlan} disabled={loadingWorkout}>
              {loadingWorkout ? 'Generating\u2026' : 'Generate Workout Plan'}
            </button>
          </div>
          {workoutError && <p className="ai-demo-badge">{workoutError}</p>}
          {workoutWarning && <p className="ai-demo-badge">{workoutWarning}</p>}

          {workoutPlan && (
            <div className="ai-result" style={{ marginTop: '1.5rem' }}>
              <h3>{workoutPlan.plan_name}</h3>
              {workoutPlan._demo && <p className="ai-demo-badge">Demo plan — add a Gemini API key for real AI generation</p>}

              {workoutPlan.days.map((d, i) => (
                <div key={i} className="ai-card">
                  <strong>{d.day} — {d.focus}</strong>
                  <table className="data-table" style={{ marginTop: '0.5rem' }}>
                    <thead>
                      <tr><th>Exercise</th><th>Sets</th><th>Reps</th><th>Rest</th></tr>
                    </thead>
                    <tbody>
                      {d.exercises.map((ex, j) => (
                        <tr key={j}>
                          <td>{ex.name}</td>
                          <td>{ex.sets}</td>
                          <td>{ex.reps}</td>
                          <td>{ex.rest_seconds}s</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ))}
            </div>
          )}
        </section>
      )}
    </div>
  );
}
