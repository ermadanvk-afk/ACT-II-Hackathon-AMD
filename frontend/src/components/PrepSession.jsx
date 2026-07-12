import React, { useContext, useEffect, useState, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { PlayCircle, Loader2, CheckCircle2, Database } from 'lucide-react';
import MCQView from './MCQView';
import TechResultView from './TechResultView';

const PrepSession = () => {
  const { role, level } = useParams();
  const { user, api } = useContext(AuthContext);

  const [schedule, setSchedule] = useState([]);
  const [loadingSchedule, setLoadingSchedule] = useState(true);
  const [currentDay, setCurrentDay] = useState(1);

  // Session state machine
  const [sessionState, setSessionState] = useState('idle'); // idle | loading | mcq | tech | error
  const [activeDay, setActiveDay] = useState(null);
  const [mcqData, setMcqData] = useState(null);
  const [techData, setTechData] = useState(null);
  const [isFromCache, setIsFromCache] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [completing, setCompleting] = useState(false);

  const fetchSchedule = useCallback(async () => {
    try {
      const res = await api.get(
        `/api/schedule/${encodeURIComponent(role)}?level=${encodeURIComponent(level)}`
      );
      setSchedule(res.data.schedule);
    } catch (err) {
      console.error('Failed to fetch schedule', err);
    }
    setLoadingSchedule(false);
  }, [role, level, api]);

  useEffect(() => {
    fetchSchedule();
    // currentDay from user journey
    const journey = user?.journeys?.find(j => j.role === role && j.level === level);
    setCurrentDay(journey ? journey.current_day : 1);
  }, [fetchSchedule, user, role, level]);

  const handleStart = async (dayObj) => {
    setActiveDay(dayObj);
    setSessionState('loading');
    setMcqData(null);
    setTechData(null);
    setIsFromCache(false);
    setErrorMsg('');

    try {
      // Step 1: ask orchestrator which action to take
      const orchestratorPayload = {
        user_id: user.username,
        target_role: role,
        current_phase: dayObj.phase.toLowerCase(),
        topic_name: dayObj.topic,
        difficulty: dayObj.difficulty,
      };

      const res = await api.post('/api/next-action', orchestratorPayload);
      const { action, endpoint } = res.data;

      if (action === 'RUN_APTITUDE_PRACTICE') {
        const aptRes = await api.post(endpoint, {
          user_id: user.username,
          target_role: role,
          topic_name: dayObj.topic,
          difficulty: dayObj.difficulty,
          day: dayObj.day,
        });
        setMcqData(aptRes.data.mcq_data);
        setIsFromCache(aptRes.data.cached === true);
        setSessionState('mcq');

      } else if (action === 'RUN_TECH_PRACTICE') {
        const techRes = await api.post(endpoint, {
          user_id: user.username,
          target_role: role,
          topic_name: dayObj.topic,
          difficulty: dayObj.difficulty,
          day: dayObj.day,
        });
        setTechData(techRes.data.tech_data);
        setIsFromCache(techRes.data.cached === true);
        setSessionState('tech');

      } else if (action === 'START_MOCK_INTERVIEW') {
        setErrorMsg('Mock interview coming soon! WebSocket UI is in progress.');
        setSessionState('error');
      }
    } catch (err) {
      console.error('Session error', err);
      const detail = err?.response?.data?.detail || err?.message || 'Unknown error';
      setErrorMsg(detail);
      setSessionState('error');
    }
  };

  const handleMarkComplete = async () => {
    if (!activeDay || completing) return;
    setCompleting(true);
    try {
      const res = await api.post('/api/complete-day', {
        role,
        level,
        completed_day: activeDay.day,
      });
      setCurrentDay(res.data.next_day);
      // Reset back to roadmap so user sees next day unlocked
      setSessionState('idle');
      setActiveDay(null);
      setMcqData(null);
      setTechData(null);
    } catch (err) {
      console.error('Failed to mark complete', err);
      alert('Could not mark day as complete: ' + (err?.response?.data?.detail || err.message));
    }
    setCompleting(false);
  };

  const handleReset = () => {
    setSessionState('idle');
    setActiveDay(null);
    setMcqData(null);
    setTechData(null);
    setErrorMsg('');
  };

  if (loadingSchedule) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '40vh' }}>
        <Loader2 size={32} className="spin" />
        <span style={{ marginLeft: '1rem', color: 'var(--text-muted)' }}>Loading your roadmap...</span>
      </div>
    );
  }

  // ── LOADING ─────────────────────────────────────────────────────
  if (sessionState === 'loading') {
    return (
      <div className="session-loading-overlay">
        <div className="glass-panel session-loading-card">
          <div className="loading-spinner" />
          <h2>AI Agent Working…</h2>
          <p style={{ color: 'var(--text-muted)', marginTop: '0.5rem' }}>
            Generating {activeDay?.phase === 'aptitude' ? 'your MCQ question' : 'study material'} for{' '}
            <strong>{activeDay?.topic}</strong>
          </p>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '1rem' }}>
            This may take 20–60 seconds on first load. Subsequent visits are instant (cached).
          </p>
        </div>
      </div>
    );
  }

  // ── MCQ VIEW ────────────────────────────────────────────────────
  if (sessionState === 'mcq' && mcqData) {
    return (
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
          <button className="btn btn-outline back-btn" onClick={handleReset}>← Back to Roadmap</button>
          {isFromCache && (
            <span className="cache-badge">
              <Database size={13} /> Loaded from cache
            </span>
          )}
        </div>

        <MCQView
          mcq={mcqData}
          topic={activeDay?.topic}
          difficulty={activeDay?.difficulty}
          onMarkComplete={activeDay?.day === currentDay ? handleMarkComplete : null}
          completing={completing}
        />
      </div>
    );
  }

  // ── TECH VIEW ───────────────────────────────────────────────────
  if (sessionState === 'tech' && techData) {
    return (
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
          <button className="btn btn-outline back-btn" onClick={handleReset}>← Back to Roadmap</button>
          {isFromCache && (
            <span className="cache-badge">
              <Database size={13} /> Loaded from cache
            </span>
          )}
        </div>

        <TechResultView
          content={techData}
          topic={activeDay?.topic}
          difficulty={activeDay?.difficulty}
          onMarkComplete={activeDay?.day === currentDay ? handleMarkComplete : null}
          completing={completing}
        />
      </div>
    );
  }

  // ── ERROR ────────────────────────────────────────────────────────
  if (sessionState === 'error') {
    return (
      <div>
        <button className="btn btn-outline back-btn" onClick={handleReset} style={{ marginBottom: '1.5rem' }}>← Back to Roadmap</button>
        <div className="glass-panel" style={{ padding: '2rem', borderColor: 'rgba(239,68,68,0.4)', textAlign: 'center' }}>
          <p style={{ color: 'var(--danger)', fontSize: '1.1rem', marginBottom: '1rem' }}>⚠ {errorMsg}</p>
          <button className="btn btn-primary" onClick={handleReset}>Try Again</button>
        </div>
      </div>
    );
  }

  // ── IDLE — ROADMAP ───────────────────────────────────────────────
  return (
    <div>
      <div className="glass-panel" style={{ padding: '2rem', marginBottom: '2rem' }}>
        <h2>{role} — {level} Track</h2>
        <p style={{ color: 'var(--text-muted)', marginTop: '0.5rem' }}>
          You are on <strong style={{ color: 'var(--primary)' }}>Day {currentDay}</strong> of your 30-day journey.
        </p>
      </div>

      <h3>Your 30-Day Roadmap</h3>
      <div style={{ marginTop: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {schedule.map((dayObj) => {
          const isPast    = dayObj.day < currentDay;
          const isCurrent = dayObj.day === currentDay;
          const isFuture  = dayObj.day > currentDay;

          const phaseColor = {
            tech: 'var(--accent-swe)',
            aptitude: 'var(--accent-da)',
            mock_interview: 'var(--accent-ml)',
          }[dayObj.phase] || 'var(--primary)';

          return (
            <div
              key={dayObj.day}
              className="glass-panel"
              style={{
                padding: '1.5rem',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                opacity: isFuture ? 0.45 : 1,
                border: isCurrent ? `1px solid ${phaseColor}` : '1px solid var(--glass-border)',
                boxShadow: isCurrent ? `0 0 20px ${phaseColor}22` : 'none',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <div style={{
                  width: 40, height: 40, borderRadius: '50%',
                  background: isPast ? 'rgba(16,185,129,0.2)' : isCurrent ? phaseColor : 'rgba(255,255,255,0.05)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontWeight: 700, fontSize: '0.85rem', flexShrink: 0,
                  color: isPast ? 'var(--accent-da)' : isCurrent ? 'white' : 'var(--text-muted)',
                  border: isPast ? '1px solid rgba(16,185,129,0.4)' : 'none',
                }}>
                  {isPast ? '✓' : dayObj.day}
                </div>
                <div>
                  <h4 style={{ marginBottom: '0.2rem' }}>
                    <span style={{ color: phaseColor, textTransform: 'uppercase', fontSize: '0.75rem', letterSpacing: 1 }}>
                      {dayObj.phase.replace('_', ' ')}
                    </span>
                    {' — '}
                    {dayObj.topic}
                  </h4>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>{dayObj.difficulty}</p>
                </div>
              </div>

              <div>
                {isPast && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <span style={{ color: 'var(--accent-da)', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                      <CheckCircle2 size={16} /> Completed
                    </span>
                    <button 
                      className="btn btn-outline" 
                      style={{ padding: '0.4rem 1rem', fontSize: '0.85rem' }} 
                      onClick={() => handleStart(dayObj)}
                    >
                      Review
                    </button>
                  </div>
                )}
                {isCurrent && (
                  <button className="btn btn-primary" onClick={() => handleStart(dayObj)}>
                    <PlayCircle size={18} /> Start
                  </button>
                )}
                {isFuture && (
                  <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>🔒 Locked</span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default PrepSession;
