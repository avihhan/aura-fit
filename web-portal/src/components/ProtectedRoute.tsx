import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function ProtectedRoute({
  children,
}: {
  children: React.ReactNode;
}) {
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

  return <>{children}</>;
}
