import React from 'react';
import { BookOpen, ChevronRight, CheckCircle, Loader2 } from 'lucide-react';

const TechResultView = ({ content, topic, difficulty, onMarkComplete, completing }) => {
  // Split content into paragraphs for readable display
  const paragraphs = typeof content === 'string'
    ? content.split('\n').filter(p => p.trim())
    : [];

  return (
    <div className="tech-result-container">
      {/* Header */}
      <div className="glass-panel mcq-header">
        <div className="mcq-meta">
          <span className="mcq-badge">{topic}</span>
          <span className="mcq-badge difficulty">{difficulty}</span>
        </div>
        <h2 className="mcq-title">Tech Study Material</h2>
      </div>

      {/* Content */}
      <div className="glass-panel tech-content-box">
        <div className="tech-content-icon">
          <BookOpen size={22} />
          <span>Study Resource</span>
        </div>

        <div className="tech-content-body">
          {paragraphs.length > 0 ? (
            paragraphs.map((para, i) => {
              // Detect headers (lines starting with # or all caps short lines)
              if (para.startsWith('##')) {
                return <h3 key={i} className="tech-heading-2">{para.replace(/^#+\s*/, '')}</h3>;
              }
              if (para.startsWith('#')) {
                return <h2 key={i} className="tech-heading-1">{para.replace(/^#+\s*/, '')}</h2>;
              }
              // Helper to parse bold and URLs
              const formatText = (text) => {
                let formatted = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
                formatted = formatted.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" rel="noopener noreferrer" style="color: var(--primary); text-decoration: underline; word-break: break-all;">$1</a>');
                return formatted;
              };

              // Detect bullet points
              if (para.trim().startsWith('-') || para.trim().startsWith('•') || para.trim().match(/^\d+\./)) {
                const listText = para.replace(/^[-•\d.]\s*/, '');
                return <li key={i} className="tech-list-item" dangerouslySetInnerHTML={{ __html: formatText(listText) }} />;
              }
              
              // Standard paragraph
              return (
                <p
                  key={i}
                  className="tech-para"
                  dangerouslySetInnerHTML={{ __html: formatText(para) }}
                />
              );
            })
          ) : (
            <p className="tech-para">{content}</p>
          )}
        </div>
      </div>

      {/* Next button */}
      {onMarkComplete && (
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
      )}
    </div>
  );
};

export default TechResultView;
