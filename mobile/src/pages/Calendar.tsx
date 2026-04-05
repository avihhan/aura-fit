import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../lib/api';

interface Workout {
  id: number;
  workout_date: string;
  notes: string | null;
}

interface NutritionLog {
  id: number;
  meal_type: string | null;
  calories: number | null;
  logged_at: string;
}

function daysInMonth(year: number, month: number) {
  return new Date(year, month + 1, 0).getDate();
}

function startDayOfWeek(year: number, month: number) {
  return new Date(year, month, 1).getDay();
}

export default function Calendar() {
  const { accessToken } = useAuth();
  const now = new Date();
  const [year, setYear] = useState(now.getFullYear());
  const [month, setMonth] = useState(now.getMonth());
  const [workouts, setWorkouts] = useState<Workout[]>([]);
  const [nutrition, setNutrition] = useState<NutritionLog[]>([]);
  const [selectedDate, setSelectedDate] = useState<string | null>(null);

  useEffect(() => {
    if (!accessToken) return;
    apiFetch('/api/workouts', accessToken)
      .then((r) => r.json())
      .then((d) => setWorkouts(d.workouts ?? []))
      .catch(() => {});
    apiFetch('/api/nutrition', accessToken)
      .then((r) => r.json())
      .then((d) => setNutrition(d.nutrition_logs ?? []))
      .catch(() => {});
  }, [accessToken]);

  const workoutDates = new Set(workouts.map((w) => w.workout_date));
  const nutritionDates = new Set(nutrition.map((n) => n.logged_at?.slice(0, 10)));

  const total = daysInMonth(year, month);
  const offset = startDayOfWeek(year, month);

  function prevMonth() {
    if (month === 0) { setYear(year - 1); setMonth(11); }
    else setMonth(month - 1);
  }

  function nextMonth() {
    if (month === 11) { setYear(year + 1); setMonth(0); }
    else setMonth(month + 1);
  }

  const dayEvents = selectedDate
    ? {
        workouts: workouts.filter((w) => w.workout_date === selectedDate),
        meals: nutrition.filter((n) => n.logged_at?.startsWith(selectedDate)),
      }
    : null;

  const monthLabel = new Date(year, month).toLocaleDateString('en-US', {
    month: 'long',
    year: 'numeric',
  });

  return (
    <div className="page">
      <header className="page-header">
        <h1>Calendar</h1>
      </header>

      <div className="cal-nav">
        <button className="cal-nav-btn" onClick={prevMonth}>&larr;</button>
        <span className="cal-month-label">{monthLabel}</span>
        <button className="cal-nav-btn" onClick={nextMonth}>&rarr;</button>
      </div>

      <div className="cal-weekdays">
        {['S', 'M', 'T', 'W', 'T', 'F', 'S'].map((d, i) => (
          <span key={i} className="cal-wd">{d}</span>
        ))}
      </div>

      <div className="cal-grid">
        {Array.from({ length: offset }).map((_, i) => (
          <span key={`e-${i}`} className="cal-cell cal-cell--empty" />
        ))}
        {Array.from({ length: total }).map((_, i) => {
          const day = i + 1;
          const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
          const hasW = workoutDates.has(dateStr);
          const hasN = nutritionDates.has(dateStr);
          const isSelected = dateStr === selectedDate;
          const isToday = dateStr === now.toISOString().slice(0, 10);

          return (
            <button
              key={day}
              className={`cal-cell${isSelected ? ' cal-cell--selected' : ''}${isToday ? ' cal-cell--today' : ''}`}
              onClick={() => setSelectedDate(isSelected ? null : dateStr)}
            >
              <span className="cal-day">{day}</span>
              <div className="cal-dots">
                {hasW && <span className="cal-dot cal-dot--workout" />}
                {hasN && <span className="cal-dot cal-dot--nutrition" />}
              </div>
            </button>
          );
        })}
      </div>

      {selectedDate && dayEvents && (
        <section className="section" style={{ marginTop: '1rem' }}>
          <h2>{selectedDate}</h2>
          {dayEvents.workouts.length > 0 ? (
            dayEvents.workouts.map((w) => (
              <div key={w.id} className="log-row">
                <span className="log-primary">Workout</span>
                <span className="log-secondary">{w.notes ?? 'No notes'}</span>
              </div>
            ))
          ) : (
            <p className="empty-text" style={{ padding: '0.5rem 0' }}>No workouts</p>
          )}
          {dayEvents.meals.length > 0 ? (
            dayEvents.meals.map((n) => (
              <div key={n.id} className="log-row">
                <span className="log-primary">{n.meal_type ?? 'Meal'}</span>
                <span className="log-value">{n.calories ?? 0} kcal</span>
              </div>
            ))
          ) : (
            <p className="empty-text" style={{ padding: '0.5rem 0' }}>No meals logged</p>
          )}
        </section>
      )}
    </div>
  );
}
