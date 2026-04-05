import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import MobileLayout from './components/MobileLayout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Workouts from './pages/Workouts';
import Nutrition from './pages/Nutrition';
import Profile from './pages/Profile';
import BodyMetrics from './pages/BodyMetrics';
import Goals from './pages/Goals';
import AIPlans from './pages/AIPlans';
import Calendar from './pages/Calendar';
import Notifications from './pages/Notifications';

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />

          <Route
            path="/"
            element={
              <ProtectedRoute>
                <MobileLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="workouts" element={<Workouts />} />
            <Route path="nutrition" element={<Nutrition />} />
            <Route path="body-metrics" element={<BodyMetrics />} />
            <Route path="goals" element={<Goals />} />
            <Route path="ai-plans" element={<AIPlans />} />
            <Route path="calendar" element={<Calendar />} />
            <Route path="notifications" element={<Notifications />} />
            <Route path="profile" element={<Profile />} />
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
