import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import type { Role } from '../lib/api';
import { ROLES } from '../lib/api';

const MOBILE_APP_URL = import.meta.env.VITE_MOBILE_URL || 'http://localhost:3001';

interface Props {
  children: React.ReactNode;
  allowedRoles?: Role[];
}

export default function ProtectedRoute({ children, allowedRoles }: Props) {
  const { user, initialized } = useAuth();

  if (!initialized) {
    return (
      <div className="loading-screen">
        <div className="login-logo">A</div>
        <p>Loading&hellip;</p>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (user.role === ROLES.MEMBER) {
    window.location.href = MOBILE_APP_URL;
    return null;
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
}
