import React, { useState } from 'react';
import { CheckCircle, XCircle, BookOpen, Loader2, ChevronRight } from 'lucide-react';

const MCQView = ({ mcq, topic, difficulty, onMarkComplete, completing }) => {
  const mcqList = Array.isArray(mcq) ? mcq : (mcq ? [mcq] : []);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selected, setSelected] = useState(null);
  const [revealed, setRevealed] = useState(false);

  const currentMcq = mcqList[currentIndex] || {};
  const options = currentMcq?.options || {};
  const correctAnswer = currentMcq?.correct_answer;

  const handleNext = () => {
    setSelected(null);
    setRevealed(false);
    setCurrentIndex((prev) => prev + 1);
  };

  const handleSelect = (key) => {
    if (revealed) return;
    setSelected(key);
  };

  const handleSubmit = () => {
    if (!selected) return;
    setRevealed(true);
  };

  const isCorrect = selected === correctAnswer;

  return (
    <div className="mcq-container">
      {/* Header */}
      <div className="mcq-header glass-panel">
        <div className="mcq-meta">
          <span className="mcq-badge">{topic}</span>
          <span className="mcq-badge difficulty">{difficulty}</span>
        </div>
        <h2 className="mcq-title">
          Aptitude Question {mcqList.length > 1 && <span style={{fontSize: '0.9rem', color: 'var(--text-muted)'}}>({currentIndex + 1} of {mcqList.length})</span>}
        </h2>
      </div>

      {/* Question */}
      <div className="glass-panel mcq-question-box">
        <div className="mcq-question-icon"><BookOpen size={20} /></div>
        <p className="mcq-question-text">{currentMcq?.question}</p>
      </div>

      {/* Options */}
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
              onClick={() => handleSelect(key)}
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

      {/* Submit / Result */}
      {!revealed ? (
        <button
          className="btn btn-primary mcq-submit"
          onClick={handleSubmit}
          disabled={!selected}
        >
          Submit Answer
        </button>
      ) : (
        <div className={`mcq-result-banner ${isCorrect ? 'banner-correct' : 'banner-wrong'}`}>
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

      {/* Next / Complete actions */}
      {revealed && (
        currentIndex < mcqList.length - 1 ? (
          <button
            className="btn btn-primary mcq-next"
            onClick={handleNext}
            style={{ alignSelf: 'flex-end' }}
          >
            Next Question <ChevronRight size={18} />
          </button>
        ) : (
          onMarkComplete && (
            <button
              className="btn btn-complete"
              onClick={onMarkComplete}
              disabled={completing}
              style={{ alignSelf: 'flex-start' }}
            >
              {completing
                ? <><Loader2 size={16} className="spin" /> Saving...</>
                : <><CheckCircle size={18} /> Mark Day Complete & Unlock Next</>}
            </button>
          )
        )
      )}
    </div>
  );
};

export default MCQView;
