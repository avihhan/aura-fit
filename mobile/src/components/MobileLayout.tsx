import { Outlet, NavLink } from 'react-router-dom';

export default function MobileLayout() {
  return (
    <div className="mobile-shell">
      <main className="mobile-main">
        <Outlet />
      </main>

      <nav className="mobile-tabs">
        <NavLink
          to="/dashboard"
          className={({ isActive }) => `tab${isActive ? ' tab--active' : ''}`}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
            <polyline points="9 22 9 12 15 12 15 22" />
          </svg>
          <span>Home</span>
        </NavLink>

        <NavLink
          to="/workouts"
          className={({ isActive }) => `tab${isActive ? ' tab--active' : ''}`}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M18 8h1a4 4 0 0 1 0 8h-1" />
            <path d="M6 8H5a4 4 0 0 0 0 8h1" />
            <line x1="6" y1="12" x2="18" y2="12" />
          </svg>
          <span>Workouts</span>
        </NavLink>

        <NavLink
          to="/nutrition"
          className={({ isActive }) => `tab${isActive ? ' tab--active' : ''}`}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 2L2 7l10 5 10-5-10-5z" />
            <path d="M2 17l10 5 10-5" />
            <path d="M2 12l10 5 10-5" />
          </svg>
          <span>Nutrition</span>
        </NavLink>

        <NavLink
          to="/body-metrics"
          className={({ isActive }) => `tab${isActive ? ' tab--active' : ''}`}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
          </svg>
          <span>Metrics</span>
        </NavLink>

        <NavLink
          to="/profile"
          className={({ isActive }) => `tab${isActive ? ' tab--active' : ''}`}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
            <circle cx="12" cy="7" r="4" />
          </svg>
          <span>Profile</span>
        </NavLink>
      </nav>
    </div>
  );
}
