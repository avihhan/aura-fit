import { useEffect, useState, type FormEvent } from 'react';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../lib/api';

interface Exercise {
  id: number;
  name: string;
  muscle_group: string | null;
  equipment: string | null;
  instructions: string | null;
}

export default function Exercises() {
  const { accessToken } = useAuth();
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState('');
  const [muscleGroup, setMuscleGroup] = useState('');
  const [equipment, setEquipment] = useState('');
  const [instructions, setInstructions] = useState('');
  const [saving, setSaving] = useState(false);

  function fetchExercises() {
    if (!accessToken) return;
    apiFetch('/api/exercises', accessToken)
      .then((r) => r.json())
      .then((d) => setExercises(d.exercises ?? []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }

  useEffect(fetchExercises, [accessToken]);

  async function handleCreate(e: FormEvent) {
    e.preventDefault();
    if (!accessToken || !name.trim()) return;
    setSaving(true);

    const body: Record<string, string> = { name: name.trim() };
    if (muscleGroup.trim()) body.muscle_group = muscleGroup.trim();
    if (equipment.trim()) body.equipment = equipment.trim();
    if (instructions.trim()) body.instructions = instructions.trim();

    await apiFetch('/api/exercises', accessToken, {
      method: 'POST',
      body: JSON.stringify(body),
    });

    setName('');
    setMuscleGroup('');
    setEquipment('');
    setInstructions('');
    setSaving(false);
    setShowForm(false);
    fetchExercises();
  }

  async function handleDelete(id: number) {
    if (!accessToken) return;
    await apiFetch(`/api/exercises/${id}`, accessToken, { method: 'DELETE' });
    setExercises((prev) => prev.filter((ex) => ex.id !== id));
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1>Exercise Library</h1>
          <p className="dashboard-subtitle">{exercises.length} exercises</p>
        </div>
        <button
          className="login-btn"
          style={{ padding: '0.5rem 1rem', fontSize: '0.8125rem' }}
          onClick={() => setShowForm(!showForm)}
        >
          {showForm ? 'Cancel' : '+ Add Exercise'}
        </button>
      </header>

      {showForm && (
        <section className="dashboard-section" style={{ marginBottom: '1rem' }}>
          <h2>New Exercise</h2>
          <form onSubmit={handleCreate} className="exercise-form">
            <div className="form-group">
              <label htmlFor="ex-name">Name</label>
              <input id="ex-name" value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Barbell Squat" disabled={saving} />
            </div>
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="ex-mg">Muscle Group</label>
                <input id="ex-mg" value={muscleGroup} onChange={(e) => setMuscleGroup(e.target.value)} placeholder="e.g. Legs" disabled={saving} />
              </div>
              <div className="form-group">
                <label htmlFor="ex-eq">Equipment</label>
                <input id="ex-eq" value={equipment} onChange={(e) => setEquipment(e.target.value)} placeholder="e.g. Barbell" disabled={saving} />
              </div>
            </div>
            <div className="form-group">
              <label htmlFor="ex-inst">Instructions</label>
              <textarea id="ex-inst" rows={3} value={instructions} onChange={(e) => setInstructions(e.target.value)} placeholder="How to perform the exercise..." disabled={saving} />
            </div>
            <button type="submit" className="login-btn" style={{ padding: '0.5rem 1rem', fontSize: '0.8125rem' }} disabled={saving || !name.trim()}>
              {saving ? 'Saving\u2026' : 'Create Exercise'}
            </button>
          </form>
        </section>
      )}

      {loading ? (
        <div className="empty-state"><p>Loading&hellip;</p></div>
      ) : exercises.length === 0 ? (
        <div className="empty-state">
          <p>No exercises yet. Add exercises to build your library.</p>
        </div>
      ) : (
        <section className="dashboard-section">
          <table className="data-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Muscle Group</th>
                <th>Equipment</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {exercises.map((ex) => (
                <tr key={ex.id}>
                  <td>{ex.name}</td>
                  <td>{ex.muscle_group ?? '\u2014'}</td>
                  <td>{ex.equipment ?? '\u2014'}</td>
                  <td>
                    <button className="delete-btn" onClick={() => handleDelete(ex.id)}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}
    </div>
  );
}
