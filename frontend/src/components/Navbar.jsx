import React, { useContext } from 'react';
import { useLocation, useNavigate, useParams, matchPath } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { LogOut, RotateCcw, User } from 'lucide-react';

const Navbar = () => {
  const { user, logout, api, checkAuth } = useContext(AuthContext);
  const location = useLocation();
  const navigate = useNavigate();

  // Check if we are inside a prep session to show the Reset button
  const prepMatch = matchPath("/prep/:role/:level", location.pathname);
  
  const handleReset = async () => {
    if (!prepMatch) return;
    const { role, level } = prepMatch.params;
    
    if (window.confirm(`Are you sure you want to reset your progress for ${role} (${level})? This cannot be undone.`)) {
      try {
        await api.delete(`/api/journey/reset?role=${encodeURIComponent(role)}&level=${encodeURIComponent(level)}`);
        await checkAuth(); // refresh user data
        navigate('/'); // take them back to dashboard
      } catch (err) {
        console.error("Failed to reset journey", err);
      }
    }
  };

  return (
    <nav className="navbar glass-panel">
      <div className="nav-brand" style={{cursor: 'pointer'}} onClick={() => navigate('/')}>
        PrepAI
      </div>
      
      <div className="nav-actions">
        {prepMatch && (
          <button className="btn btn-danger" onClick={handleReset} title="Reset this specific journey">
            <RotateCcw size={18} /> Restart Journey
          </button>
        )}
        
        <div style={{display: 'flex', alignItems: 'center', gap: '0.5rem', marginLeft: '1rem'}}>
          <User size={20} color="var(--text-muted)" />
          <span style={{fontWeight: 600}}>{user?.username}</span>
        </div>
        
        <button className="btn btn-outline" onClick={logout} style={{marginLeft: '1rem'}}>
          <LogOut size={18} /> Logout
        </button>
      </div>
    </nav>
  );
};

export default Navbar;
