import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ROLES } from '../lib/api';

const WEB_PORTAL_URL = import.meta.env.VITE_PORTAL_URL || 'http://localhost:3000';

export default function ProtectedRoute({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, initialized } = useAuth();

  if (!initialized) {
    return (
      <div className="loading-screen">
        <div className="loading-logo">A</div>
        <p>Loading&hellip;</p>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (user.role === ROLES.OWNER || user.role === ROLES.SUPER_ADMIN) {
    return (
      <div className="role-gate">
        <div className="loading-logo">A</div>
        <h2>Admin Account Detected</h2>
        <p>
          This app is for members. Please use the{' '}
          <a href={WEB_PORTAL_URL}>Admin Portal</a> instead.
        </p>
      </div>
    );
  }

  return <>{children}</>;
}
