import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import { ToastProvider } from './components/ui/Toast';
import { ProtectedRoute } from './components/layout/ProtectedRoute';

import { Landing } from './pages/Landing';
import { Auth } from './pages/Auth';
import { Dashboard } from './pages/Dashboard';
import { GroupWorkspace } from './pages/GroupWorkspace';
import { Benchmark } from './pages/Benchmark';
import { HowItWorks } from './pages/HowItWorks';

export const App: React.FC = () => {
  return (
    <ThemeProvider>
      <ToastProvider>
        <AuthProvider>
          <BrowserRouter>
            <Routes>
              {/* Landing Page as default index route */}
              <Route path="/" element={<Landing />} />
              <Route path="/login" element={<Auth />} />

              <Route
                path="/dashboard"
                element={
                  <ProtectedRoute>
                    <Dashboard />
                  </ProtectedRoute>
                }
              />

              <Route
                path="/group/:id"
                element={
                  <ProtectedRoute>
                    <GroupWorkspace />
                  </ProtectedRoute>
                }
              />

              <Route
                path="/benchmark"
                element={
                  <ProtectedRoute>
                    <Benchmark />
                  </ProtectedRoute>
                }
              />

              <Route
                path="/how-it-works"
                element={
                  <ProtectedRoute>
                    <HowItWorks />
                  </ProtectedRoute>
                }
              />

              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </BrowserRouter>
        </AuthProvider>
      </ToastProvider>
    </ThemeProvider>
  );
};
