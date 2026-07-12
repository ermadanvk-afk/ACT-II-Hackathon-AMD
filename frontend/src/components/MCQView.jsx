import React, { useState } from 'react';
import { CheckCircle, XCircle, BookOpen, Loader2 } from 'lucide-react';

const MCQView = ({ mcq, topic, difficulty, onMarkComplete, completing }) => {
  // 1. BULLETPROOF PARSING
  // We extract the JSON array even if the AI added conversational text around it
  let parsedMcq = [];
  if (Array.isArray(mcq)) {
    parsedMcq = mcq;
  } else if (typeof mcq === 'string') {
    try {
      let cleaned = mcq.trim();
      // Remove any conversational text before the JSON array starts
      const startIdx = cleaned.indexOf('[');
      if (startIdx !== -1) {
        cleaned = cleaned.substring(startIdx);
      }
      // LLMs frequently truncate the final closing bracket of the array
      // If it ends perfectly on an object brace but is missing the array bracket, append it!
      if (cleaned.endsWith('}')) {
        cleaned += ']';
      }
      // Also aggressively strip markdown backticks if they are stuck at the end
      cleaned = cleaned.replace(/```(?:json)?/g, '').trim();
      if (cleaned.endsWith('}')) {
        cleaned += ']';
      }

      parsedMcq = JSON.parse(cleaned);
    } catch (e) {
      console.error("Total parse failure, falling back to empty array:", e);
      parsedMcq = [];
    }
  } else if (mcq && typeof mcq === 'object') {
    parsedMcq = [mcq];
  }

  const mcqList = Array.isArray(parsedMcq) ? parsedMcq : [];

  // 2. STATE MAPS FOR VERTICAL LIST
  const [selectedMap, setSelectedMap] = useState({});
  const [revealedMap, setRevealedMap] = useState({});

  const handleSelect = (index, key) => {
    if (revealedMap[index]) return;
    setSelectedMap(prev => ({ ...prev, [index]: key }));
  };

  const handleSubmit = (index) => {
    if (!selectedMap[index]) return;
    setRevealedMap(prev => ({ ...prev, [index]: true }));
  };

  return (
    <div className="mcq-container">
      {/* Header */}
      <div className="mcq-header glass-panel" style={{ marginBottom: '2rem' }}>
        <div className="mcq-meta">
          <span className="mcq-badge">{topic}</span>
          <span className="mcq-badge difficulty">{difficulty}</span>
        </div>
        <h2 className="mcq-title">
          Aptitude Practice ({mcqList.length} Questions)
        </h2>
      </div>

      {/* Fallback if parsing completely fails */}
      {mcqList.length === 0 && (
        <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center', marginBottom: '2rem', borderColor: 'rgba(239,68,68,0.4)' }}>
          <p style={{ color: 'var(--text-muted)' }}>
            The AI returned an improperly formatted string for this topic. 
            <br/><br/>
            <strong>Don't worry! You can still mark this day as complete below to proceed to the next module.</strong>
          </p>
        </div>
      )}

      {/* ALL MCQs RENDERED VERTICALLY */}
      {mcqList.map((currentMcq, index) => {
        const options = currentMcq?.options || {};
        const correctAnswer = currentMcq?.correct_answer;
        const selected = selectedMap[index];
        const revealed = revealedMap[index];
        const isCorrect = selected === correctAnswer;

        return (
          <div key={index} className="glass-panel" style={{ marginBottom: '2.5rem', padding: '2rem' }}>
            <h3 style={{ marginBottom: '1rem', color: 'var(--primary)', fontSize: '1.2rem' }}>Question {index + 1}</h3>
            
            <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
              <BookOpen size={20} style={{ color: 'var(--accent-da)' }} />
              <p className="mcq-question-text" style={{ fontSize: '1.1rem', lineHeight: '1.6' }}>{currentMcq?.question}</p>
            </div>

            <div className="mcq-options">
              {Object.entries(options).map(([key, text]) => {
                let optionClass = 'mcq-option glass-panel';
                if (revealed) {
                  if (key === correctAnswer) optionClass += ' correct';
                  else if (key === selected) optionClass += ' wrong';
                  else optionClass += ' dimmed';
                } else if (selected === key) {
                  optionClass += ' selected';
                }

                return (
                  <button
                    key={key}
                    className={optionClass}
                    onClick={() => handleSelect(index, key)}
                    disabled={revealed}
                  >
                    <span className="option-key">{key}</span>
                    <span className="option-text">{text}</span>
                    {revealed && key === correctAnswer && <CheckCircle size={20} className="option-icon correct-icon" />}
                    {revealed && key === selected && key !== correctAnswer && <XCircle size={20} className="option-icon wrong-icon" />}
                  </button>
                );
              })}
            </div>

            {!revealed ? (
              <button
                className="btn btn-primary mcq-submit"
                style={{ marginTop: '1.5rem' }}
                onClick={() => handleSubmit(index)}
                disabled={!selected}
              >
                Submit Answer
              </button>
            ) : (
              <div className={`mcq-result-banner ${isCorrect ? 'banner-correct' : 'banner-wrong'}`} style={{ marginTop: '1.5rem' }}>
                <div className="banner-heading">
                  {isCorrect
                    ? <><CheckCircle size={22} /> Correct! Well done.</>
                    : <><XCircle size={22} /> Incorrect — the correct answer is <strong>{correctAnswer}</strong>.</>
                  }
                </div>
                <div className="banner-explanation">
                  <strong>Explanation:</strong> {currentMcq?.explanation}
                </div>
              </div>
            )}
          </div>
        );
      })}

      {/* 
        GUARANTEED TO RENDER: The Mark Complete Button. 
        It is now pinned to the bottom completely outside the MCQ loop.
      */}
      {onMarkComplete && (
        <button
          className="btn btn-complete"
          onClick={onMarkComplete}
          disabled={completing}
          style={{ width: '100%', padding: '1.2rem', marginTop: '1rem', fontSize: '1.1rem', justifyContent: 'center' }}
        >
          {completing
            ? <><Loader2 size={20} className="spin" /> Saving Progress...</>
            : <><CheckCircle size={22} /> Mark Day Complete & Unlock Next</>}
        </button>
      )}
    </div>
  );
};

export default MCQView;
