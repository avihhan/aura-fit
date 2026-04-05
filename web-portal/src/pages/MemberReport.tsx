import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../lib/api';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

interface ReportData {
  member: { id: number; email: string; created_at: string };
  metrics: { weight: number | null; body_fat_percentage: number | null; recorded_at: string }[];
  workouts: { id: number; workout_date: string; notes: string | null }[];
  nutrition: { calories: number | null; protein: number | null; carbs: number | null; fats: number | null; logged_at: string }[];
  goals: { goal_type: string; target_value: number | null; status: string }[];
}

export default function MemberReport() {
  const { memberId } = useParams();
  const { accessToken, tenant } = useAuth();
  const [data, setData] = useState<ReportData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!accessToken || !memberId) return;
    apiFetch(`/api/admin/members/${memberId}/report`, accessToken)
      .then((r) => r.json())
      .then(setData)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [accessToken, memberId]);

  function generatePDF() {
    if (!data) return;
    const doc = new jsPDF();
    const m = data.member;

    doc.setFontSize(20);
    doc.setTextColor(108, 99, 255);
    doc.text(`${tenant?.name ?? 'AuraFit'} — Progress Report`, 14, 20);

    doc.setFontSize(12);
    doc.setTextColor(100);
    doc.text(`Member: ${m.email}`, 14, 30);
    doc.text(`Generated: ${new Date().toLocaleDateString()}`, 14, 37);

    let y = 47;

    if (data.metrics.length > 0) {
      doc.setFontSize(14);
      doc.setTextColor(40);
      doc.text('Body Metrics', 14, y);
      y += 3;
      autoTable(doc, {
        startY: y,
        head: [['Date', 'Weight (lbs)', 'Body Fat %']],
        body: data.metrics.map((r) => [
          r.recorded_at?.slice(0, 10) ?? '',
          r.weight?.toString() ?? '-',
          r.body_fat_percentage?.toString() ?? '-',
        ]),
        theme: 'striped',
        headStyles: { fillColor: [108, 99, 255] },
      });
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      y = ((doc as any).lastAutoTable?.finalY ?? y + 30) + 10;
    }

    if (data.workouts.length > 0) {
      doc.setFontSize(14);
      doc.setTextColor(40);
      doc.text('Recent Workouts', 14, y);
      y += 3;
      autoTable(doc, {
        startY: y,
        head: [['Date', 'Notes']],
        body: data.workouts.map((w) => [w.workout_date, w.notes ?? '']),
        theme: 'striped',
        headStyles: { fillColor: [108, 99, 255] },
      });
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      y = ((doc as any).lastAutoTable?.finalY ?? y + 30) + 10;
    }

    if (data.goals.length > 0) {
      doc.setFontSize(14);
      doc.setTextColor(40);
      doc.text('Goals', 14, y);
      y += 3;
      autoTable(doc, {
        startY: y,
        head: [['Goal', 'Target', 'Status']],
        body: data.goals.map((g) => [
          g.goal_type,
          g.target_value?.toString() ?? '-',
          g.status,
        ]),
        theme: 'striped',
        headStyles: { fillColor: [108, 99, 255] },
      });
    }

    doc.save(`progress-report-${m.email.split('@')[0]}.pdf`);
  }

  if (loading) {
    return <div className="dashboard"><div className="empty-state"><p>Loading report data&hellip;</p></div></div>;
  }

  if (!data) {
    return <div className="dashboard"><div className="empty-state"><p>Member not found.</p></div></div>;
  }

  const m = data.member;

  return (
    <div className="dashboard">
      <header className="dashboard-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1>Progress Report</h1>
          <p className="dashboard-subtitle">{m.email}</p>
        </div>
        <button className="login-btn" style={{ padding: '0.5rem 1rem', fontSize: '0.8125rem' }} onClick={generatePDF}>
          Download PDF
        </button>
      </header>

      <div className="stats-grid">
        <div className="stat-card">
          <span className="stat-value">{data.metrics.length}</span>
          <span className="stat-label">Metric Entries</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{data.workouts.length}</span>
          <span className="stat-label">Workouts</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{data.goals.filter((g) => g.status === 'active').length}</span>
          <span className="stat-label">Active Goals</span>
        </div>
      </div>

      {data.metrics.length > 0 && (
        <section className="dashboard-section">
          <h2>Body Metrics (last 30)</h2>
          <table className="data-table">
            <thead><tr><th>Date</th><th>Weight</th><th>Body Fat %</th></tr></thead>
            <tbody>
              {data.metrics.map((r, i) => (
                <tr key={i}>
                  <td>{r.recorded_at?.slice(0, 10)}</td>
                  <td>{r.weight ?? '\u2014'}</td>
                  <td>{r.body_fat_percentage ?? '\u2014'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}

      {data.workouts.length > 0 && (
        <section className="dashboard-section">
          <h2>Workouts (last 30)</h2>
          <table className="data-table">
            <thead><tr><th>Date</th><th>Notes</th></tr></thead>
            <tbody>
              {data.workouts.map((w) => (
                <tr key={w.id}>
                  <td>{w.workout_date}</td>
                  <td>{w.notes ?? '\u2014'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}

      {data.goals.length > 0 && (
        <section className="dashboard-section">
          <h2>Goals</h2>
          <table className="data-table">
            <thead><tr><th>Goal</th><th>Target</th><th>Status</th></tr></thead>
            <tbody>
              {data.goals.map((g, i) => (
                <tr key={i}>
                  <td>{g.goal_type}</td>
                  <td>{g.target_value ?? '\u2014'}</td>
                  <td>{g.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}
    </div>
  );
}
