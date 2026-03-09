import { useState, type FormEvent } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Login() {
  const { login, signup, user, loading, initialized } = useAuth();

  const [mode, setMode] = useState<'login' | 'signup'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [tenantId, setTenantId] = useState('');
  const [error, setError] = useState('');

  if (!initialized) {
    return (
      <div className="login-page">
        <div className="login-card">
          <p style={{ textAlign: 'center', color: '#94a3b8' }}>
            Loading&hellip;
          </p>
        </div>
      </div>
    );
  }

  if (user) {
    return <Navigate to="/dashboard" replace />;
  }

  function switchMode() {
    setMode((m) => (m === 'login' ? 'signup' : 'login'));
    setError('');
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError('');

    if (!email.trim() || !password) {
      setError('Please enter your email and password.');
      return;
    }

    if (mode === 'signup' && !tenantId.trim()) {
      setError('Please enter your Organization ID.');
      return;
    }

    try {
      if (mode === 'login') {
        await login(email.trim(), password);
      } else {
        await signup(email.trim(), password, tenantId.trim());
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
    }
  }

  const isLogin = mode === 'login';

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-brand">
          <div className="login-logo">A</div>
          <h1>AuraFit</h1>
          <p>Admin Portal</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          {error && <div className="login-error">{error}</div>}

          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@company.com"
              autoComplete="email"
              autoFocus
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder={isLogin ? 'Enter your password' : 'Create a password'}
              autoComplete={isLogin ? 'current-password' : 'new-password'}
              disabled={loading}
            />
          </div>

          {!isLogin && (
            <div className="form-group">
              <label htmlFor="tenantId">Organization ID</label>
              <input
                id="tenantId"
                type="text"
                value={tenantId}
                onChange={(e) => setTenantId(e.target.value)}
                placeholder="Your tenant / org ID"
                disabled={loading}
              />
            </div>
          )}

          <button type="submit" className="login-btn" disabled={loading}>
            {loading
              ? isLogin
                ? 'Signing in\u2026'
                : 'Creating account\u2026'
              : isLogin
                ? 'Sign In'
                : 'Create Account'}
          </button>
        </form>

        <p className="login-toggle">
          {isLogin ? "Don\u2019t have an account? " : 'Already have an account? '}
          <button
            type="button"
            className="toggle-btn"
            onClick={switchMode}
            disabled={loading}
          >
            {isLogin ? 'Sign Up' : 'Sign In'}
          </button>
        </p>
      </div>
    </div>
  );
}
