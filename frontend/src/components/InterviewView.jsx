import React, { useState, useEffect, useRef } from 'react';
import { Mic, Loader2, CheckCircle, StopCircle, User, Bot, Play } from 'lucide-react';

const InterviewView = ({ wsUrl, topic, onMarkComplete, completing }) => {
  const [messages, setMessages] = useState([]);
  const [isWsConnected, setIsWsConnected] = useState(false);
  const [isAiSpeaking, setIsAiSpeaking] = useState(true); // Initially waiting for AI
  const [isListening, setIsListening] = useState(false);
  const [error, setError] = useState('');
  
  const ws = useRef(null);
  const recognition = useRef(null);
  const chatEndRef = useRef(null);
  const currentAiMessage = useRef(""); // To accumulate chunks before speaking

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    // 1. Setup Speech Recognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      recognition.current = new SpeechRecognition();
      recognition.current.continuous = false;
      recognition.current.interimResults = false;
      
      recognition.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        handleUserSpeech(transcript);
      };
      
      recognition.current.onerror = (event) => {
        console.error("Speech recognition error", event.error);
        setIsListening(false);
      };
      
      recognition.current.onend = () => {
        setIsListening(false);
      };
    } else {
      setError("Your browser does not support Speech Recognition. Please use Chrome or Edge.");
    }

    // 2. Setup WebSocket
    ws.current = new WebSocket(wsUrl);
    
    ws.current.onopen = () => {
      setIsWsConnected(true);
      // Backend expects us to say we are ready
      ws.current.send("Hello, I am ready for the interview.");
      setMessages([{ role: 'user', content: 'Connecting to Live AI Interviewer...', isSystem: true }]);
    };
    
    ws.current.onmessage = (event) => {
      const data = event.data;
      if (data === "[END_OF_TURN]") {
        setIsAiSpeaking(false);
        // Speak the accumulated text
        if (currentAiMessage.current && window.speechSynthesis) {
          const utterance = new SpeechSynthesisUtterance(currentAiMessage.current);
          window.speechSynthesis.speak(utterance);
        }
        currentAiMessage.current = ""; // Reset for next turn
      } else {
        setIsAiSpeaking(true);
        currentAiMessage.current += data;
        
        setMessages((prev) => {
          const newMsgs = [...prev];
          const lastMsg = newMsgs[newMsgs.length - 1];
          if (lastMsg && lastMsg.role === 'ai') {
            lastMsg.content += data;
          } else {
            newMsgs.push({ role: 'ai', content: data });
          }
          return newMsgs;
        });
      }
    };
    
    ws.current.onerror = (err) => {
      console.error('WebSocket Error:', err);
      setError("Connection to interview server lost.");
    };
    
    ws.current.onclose = () => {
      setIsWsConnected(false);
    };

    return () => {
      if (ws.current) ws.current.close();
      if (window.speechSynthesis) window.speechSynthesis.cancel();
      if (recognition.current) recognition.current.stop();
    };
  }, [wsUrl]);

  const handleUserSpeech = (transcript) => {
    if (!ws.current || ws.current.readyState !== WebSocket.OPEN) return;
    
    // Add to UI
    setMessages((prev) => [...prev, { role: 'user', content: transcript }]);
    
    // Send to backend
    ws.current.send(transcript);
    setIsAiSpeaking(true); // AI is now generating
  };

  const startListening = () => {
    if (recognition.current && !isAiSpeaking) {
      setError('');
      setIsListening(true);
      // If AI is currently talking, stop it so we can speak
      if (window.speechSynthesis) window.speechSynthesis.cancel();
      recognition.current.start();
    }
  };
  
  const stopListening = () => {
    if (recognition.current) {
      recognition.current.stop();
      setIsListening(false);
    }
  };

  const handleComplete = () => {
    if (!onMarkComplete) return;
    const aiMessages = messages.filter(m => m.role === 'ai' && !m.isSystem).map(m => m.content);
    const summary = aiMessages.length > 0 
        ? "### Interview Transcript (AI Feedback)\n\n" + aiMessages.map((m, i) => `**Response ${i+1}:**\n${m}`).join("\n\n---\n\n")
        : "No AI feedback recorded during this session.";
    onMarkComplete(summary);
  };

  return (
    <div className="interview-container glass-panel" style={{ display: 'flex', flexDirection: 'column', height: '70vh', padding: 0 }}>
      {/* Header */}
      <div className="interview-header" style={{ padding: '1.5rem', borderBottom: '1px solid var(--glass-border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ margin: 0, fontSize: '1.25rem', color: 'white' }}>Mock Interview</h2>
          <p style={{ margin: '0.2rem 0 0 0', fontSize: '0.85rem', color: 'var(--text-muted)' }}>Topic: {topic}</p>
        </div>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          {isWsConnected ? (
            <span style={{ color: '#10b981', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
              <div className="pulse-dot"></div> Live
            </span>
          ) : (
            <span style={{ color: 'var(--accent-swe)', fontSize: '0.85rem' }}>Disconnected</span>
          )}
        </div>
      </div>

      {/* Chat Area */}
      <div className="interview-chat" style={{ flex: 1, overflowY: 'auto', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {error && <div className="banner-wrong" style={{ padding: '1rem', borderRadius: '8px' }}>{error}</div>}
        
        {messages.map((msg, i) => (
          <div key={i} style={{
            display: 'flex',
            justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
            alignItems: 'flex-end',
            gap: '0.5rem'
          }}>
            {msg.role === 'ai' && !msg.isSystem && (
              <div style={{ background: 'rgba(255,255,255,0.1)', padding: '0.5rem', borderRadius: '50%' }}>
                <Bot size={18} color="var(--primary)" />
              </div>
            )}
            
            <div style={{
              background: msg.isSystem ? 'transparent' : (msg.role === 'user' ? 'var(--primary)' : 'rgba(255,255,255,0.05)'),
              color: msg.isSystem ? 'var(--text-muted)' : 'white',
              padding: msg.isSystem ? '0' : '0.8rem 1.2rem',
              borderRadius: '16px',
              borderBottomRightRadius: msg.role === 'user' ? '4px' : '16px',
              borderBottomLeftRadius: msg.role === 'ai' ? '4px' : '16px',
              maxWidth: '80%',
              fontSize: msg.isSystem ? '0.85rem' : '0.95rem',
              border: msg.role === 'ai' && !msg.isSystem ? '1px solid var(--glass-border)' : 'none'
            }}>
              {msg.content}
            </div>
            
            {msg.role === 'user' && !msg.isSystem && (
              <div style={{ background: 'rgba(255,255,255,0.1)', padding: '0.5rem', borderRadius: '50%' }}>
                <User size={18} />
              </div>
            )}
          </div>
        ))}
        <div ref={chatEndRef} />
      </div>

      {/* Controls */}
      <div className="interview-controls" style={{ padding: '1.5rem', borderTop: '1px solid var(--glass-border)', display: 'flex', justifyContent: 'center', gap: '1rem', alignItems: 'center' }}>
        {onMarkComplete && (
          <button 
            className="btn btn-complete"
            onClick={handleComplete}
            disabled={completing}
            style={{ position: 'absolute', left: '1.5rem', bottom: '1.5rem' }}
          >
            {completing ? <><Loader2 size={16} className="spin"/> Saving...</> : <><CheckCircle size={18}/> Finish</>}
          </button>
        )}
        
        <button
          className={`mic-btn ${isListening ? 'listening' : ''} ${isAiSpeaking ? 'disabled' : ''}`}
          onMouseDown={startListening}
          onMouseUp={stopListening}
          onMouseLeave={stopListening}
          onTouchStart={startListening}
          onTouchEnd={stopListening}
          disabled={!isWsConnected || isAiSpeaking}
        >
          {isListening ? <StopCircle size={28} /> : (isAiSpeaking ? <Loader2 className="spin" size={28} /> : <Mic size={28} />)}
        </button>
        <span style={{ position: 'absolute', right: '1.5rem', bottom: '1.5rem', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
          {isAiSpeaking ? 'AI is speaking...' : (isListening ? 'Listening...' : 'Hold Mic to Speak')}
        </span>
      </div>
    </div>
  );
};

export default InterviewView;
