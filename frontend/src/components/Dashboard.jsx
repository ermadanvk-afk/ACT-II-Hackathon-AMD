import React, { useState, useContext, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { Code, Database, BrainCircuit, Play } from 'lucide-react';

const roles = [
  { id: 'Software Engineer', title: 'Software Engineer', icon: <Code className="role-icon" />, color: 'var(--accent-swe)' },
  { id: 'Data Analyst', title: 'Data Analyst', icon: <Database className="role-icon" />, color: 'var(--accent-da)' },
  { id: 'Machine Learning Engineer', title: 'Machine Learning Engineer', icon: <BrainCircuit className="role-icon" />, color: 'var(--accent-ml)' }
];

const levels = ['Beginner', 'Intermediate', 'Advanced'];

const Dashboard = () => {
  const { user, api } = useContext(AuthContext);
  const navigate = useNavigate();
  
  const [selectedRole, setSelectedRole] = useState(roles[0].id);
  const [selectedLevel, setSelectedLevel] = useState(levels[0]);
  const [saving, setSaving] = useState(false);

  // Restore state if they have a saved journey for the selected role
  useEffect(() => {
    if (user && user.journeys) {
      const journey = user.journeys.find(j => j.role === selectedRole);
      if (journey) {
        setSelectedLevel(journey.level);
      } else {
        setSelectedLevel(levels[0]); // Default
      }
    }
  }, [selectedRole, user]);

  const handleStartPrep = async () => {
    setSaving(true);
    try {
      // Find current day from existing journey, or start at day 1
      const journey = user.journeys?.find(j => j.role === selectedRole && j.level === selectedLevel);
      const currentDay = journey ? journey.current_day : 1;
      
      await api.post('/api/journey/update', {
        role: selectedRole,
        level: selectedLevel,
        current_day: currentDay
      });
      navigate(`/prep/${encodeURIComponent(selectedRole)}/${encodeURIComponent(selectedLevel)}`);
    } catch (err) {
      console.error(err);
    }
    setSaving(false);
  };

  return (
    <div>
      <div className="text-center">
        <h2>Dashboard Loaded</h2>
        <h1>Choose Your Learning Path</h1>
        <p style={{color: 'var(--text-muted)'}}>Select a role and difficulty level to begin your preparation journey.</p>
      </div>
      
      <div className="role-grid">
        {roles.map((r) => (
          <div 
            key={r.id}
            className={`glass-panel role-card ${selectedRole === r.id ? 'active' : ''}`}
            onClick={() => setSelectedRole(r.id)}
            style={selectedRole === r.id ? { borderColor: r.color, boxShadow: `0 8px 32px ${r.color}33` } : {}}
          >
            <div style={{ color: r.color }}>{r.icon}</div>
            <div className="role-title">{r.title}</div>
            
            {selectedRole === r.id && (
              <div className="level-selector" onClick={(e) => e.stopPropagation()}>
                <div className="form-group mb-4">
                  <label>Select Level</label>
                  <select 
                    value={selectedLevel} 
                    onChange={(e) => setSelectedLevel(e.target.value)}
                  >
                    {levels.map(l => <option key={l} value={l}>{l}</option>)}
                  </select>
                </div>
                <button 
                  className="btn btn-primary" 
                  style={{width: '100%', background: r.color}}
                  onClick={handleStartPrep}
                  disabled={saving}
                >
                  <Play size={18} /> {saving ? 'Saving...' : 'Start Prep'}
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default Dashboard;
