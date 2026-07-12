import React from 'react';
import { Bot, CheckCircle } from 'lucide-react';

const InterviewResultView = ({ content, topic }) => {
  // Split content into paragraphs
  const paragraphs = typeof content === 'string'
    ? content.split('\n').filter(p => p.trim())
    : [];

  return (
    <div className="tech-result-container">
      {/* Header */}
      <div className="glass-panel mcq-header">
        <div className="mcq-meta">
          <span className="mcq-badge">{topic}</span>
          <span className="cache-badge">
            <CheckCircle size={14} /> Completed
          </span>
        </div>
        <h2 className="mcq-title">Interview Summary</h2>
      </div>

      {/* Content */}
      <div className="glass-panel tech-content-box">
        <div className="tech-content-icon">
          <Bot size={22} color="var(--primary)" />
          <span>AI Feedback Transcript</span>
        </div>

        <div className="tech-content-body">
          {paragraphs.length > 0 ? (
            paragraphs.map((para, i) => {
              // Parse simple markdown-like syntax
              // Very basic bold parsing and URL parsing
              const isHeading = para.startsWith('### ');
              const text = isHeading ? para.replace('### ', '') : para;

              // Parse URLs and bold text
              const urlRegex = /(https?:\/\/[^\s]+)/g;
              const parts = text.split(urlRegex);

              const formattedText = parts.map((part, index) => {
                if (part.match(urlRegex)) {
                  return (
                    <a key={index} href={part} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--primary)', textDecoration: 'underline' }}>
                      {part}
                    </a>
                  );
                }
                // Handle bold
                const boldParts = part.split(/(\*\*.*?\*\*)/g);
                return boldParts.map((bp, bpIdx) => {
                  if (bp.startsWith('**') && bp.endsWith('**')) {
                    return <strong key={`${index}-${bpIdx}`}>{bp.replace(/\*\*/g, '')}</strong>;
                  }
                  return bp;
                });
              });

              if (isHeading) {
                return <h3 key={i} style={{ marginTop: '1rem', marginBottom: '0.5rem', color: 'var(--primary)' }}>{formattedText}</h3>;
              }
              if (para === '---') {
                 return <hr key={i} style={{ border: 'none', borderTop: '1px solid var(--glass-border)', margin: '1rem 0' }} />;
              }

              return <p key={i} className="tech-para">{formattedText}</p>;
            })
          ) : (
            <p className="tech-para" style={{ color: 'var(--text-muted)' }}>No feedback available for this session.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default InterviewResultView;
