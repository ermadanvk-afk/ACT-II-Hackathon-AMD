import React, { useContext, useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { PlayCircle } from 'lucide-react';

const PrepSession = () => {
  const { role, level } = useParams();
  const { user, api } = useContext(AuthContext);
  const navigate = useNavigate();
  const [schedule, setSchedule] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSchedule = async () => {
      try {
        const res = await api.get(
          `/api/schedule/${encodeURIComponent(role)}?level=${encodeURIComponent(level)}`
        );
        setSchedule(res.data.schedule);
      } catch (err) {
        console.error("Failed to fetch schedule", err);
      }
      setLoading(false);
    };
    fetchSchedule();
  }, [role, level, api]);

  // Find the current day for this user's journey
  const journey = user?.journeys?.find(j => j.role === role && j.level === level);
  const currentDay = journey ? journey.current_day : 1;

  if (loading) return <div className="text-center mt-4">Loading prep session...</div>;

  return (
    <div>
      <div className="glass-panel" style={{padding: '2rem', marginBottom: '2rem'}}>
        <h2>{role} - {level} Track</h2>
        <p style={{color: 'var(--text-muted)'}}>You are currently on Day {currentDay} of your preparation journey.</p>
      </div>

      <h3>Your 30-Day Roadmap</h3>
      <div style={{marginTop: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem'}}>
        {schedule.map((dayObj) => {
          const isPast = dayObj.day < currentDay;
          const isCurrent = dayObj.day === currentDay;
          const isFuture = dayObj.day > currentDay;
          
          return (
            <div 
              key={dayObj.day} 
              className="glass-panel"
              style={{
                padding: '1.5rem',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                opacity: isFuture ? 0.5 : 1,
                border: isCurrent ? '1px solid var(--primary)' : '1px solid var(--glass-border)'
              }}
            >
              <div>
                <h4 style={{marginBottom: '0.25rem'}}>Day {dayObj.day}: {dayObj.phase.replace('_', ' ').toUpperCase()}</h4>
                <p style={{color: 'var(--text-muted)', fontSize: '0.9rem'}}>{dayObj.topic} ({dayObj.difficulty})</p>
              </div>
              <div>
                {isPast && <span style={{color: 'var(--accent-da)'}}>Completed</span>}
                {isCurrent && (
                  <button className="btn btn-primary">
                    <PlayCircle size={18} /> Start
                  </button>
                )}
                {isFuture && <span style={{color: 'var(--text-muted)'}}>Locked</span>}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  );
};

export default PrepSession;
