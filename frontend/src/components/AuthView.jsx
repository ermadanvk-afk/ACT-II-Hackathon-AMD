import React, { useState, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

const AuthView = () => {
  const { login, register } = useContext(AuthContext);
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

    const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      if (isLogin) {
        await login(username, password);
        navigate('/');
      } else {
        await register(username, password);
        navigate('/')
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Authentication failed");
    }
  };

  return (
    <div className="auth-container">
      <div className="glass-panel auth-box">
        <h2>{isLogin ? 'Welcome Back' : 'Join the Platform'}</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Username</label>
            <input 
              type="text" 
              value={username} 
              onChange={e => setUsername(e.target.value)}
              placeholder="Enter your username"
              required 
            />
          </div>
          <div className="form-group">
            <label>Password</label>
            <input 
              type="password" 
              value={password} 
              onChange={e => setPassword(e.target.value)}
              placeholder="Enter your password"
              required 
            />
          </div>
          {error && <div className="error-msg mb-4">{error}</div>}
          <button type="submit" className="btn btn-primary" style={{width: '100%'}}>
            {isLogin ? 'Login' : 'Register'}
          </button>
        </form>
        <div className="mt-4" style={{color: 'var(--text-muted)'}}>
          {isLogin ? "Don't have an account? " : "Already have an account? "}
          <span 
            style={{color: 'var(--primary)', cursor: 'pointer', fontWeight: 600}} 
            onClick={() => setIsLogin(!isLogin)}
          >
            {isLogin ? 'Sign up' : 'Log in'}
          </span>
        </div>
      </div>
    </div>
  );
};

export default AuthView;
