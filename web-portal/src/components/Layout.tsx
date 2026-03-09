import { Outlet, Link } from 'react-router-dom';

export default function Layout() {
  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <aside
        style={{
          width: 220,
          background: '#1a1a2e',
          color: '#eee',
          padding: '1rem',
        }}
      >
        <h2 style={{ margin: '0 0 1rem', fontSize: '1.25rem' }}>Aura Fit Admin</h2>
        <nav>
          <Link to="/dashboard" style={{ color: '#aaa', display: 'block', marginBottom: '0.5rem' }}>
            Dashboard
          </Link>
        </nav>
      </aside>
      <main style={{ flex: 1, padding: '1.5rem' }}>
        <Outlet />
      </main>
    </div>
  );
}
