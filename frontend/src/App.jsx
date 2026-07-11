import React, { useContext } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, AuthContext } from './context/AuthContext';
import Navbar from './components/Navbar';
import AuthView from './components/AuthView';
import Dashboard from './components/Dashboard';
import PrepSession from './components/PrepSession';
import './index.css';

const ProtectedRoute = ({ children }) => {
  const { user, loading } = useContext(AuthContext);
  if (loading) return <div className="app-container">Loading session...</div>;
  if (!user) return <Navigate to="/auth" replace />;
  return children;
};

const AppRoutes = () => {
  const { user } = useContext(AuthContext);
  
  return (
    <div className="app-container">
      {user && <Navbar />}
      <Routes>
        <Route path="/auth" element={!user ? <AuthView /> : <Navigate to="/" />} />
        <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/prep/:role/:level" element={<ProtectedRoute><PrepSession /></ProtectedRoute>} />
      </Routes>
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
