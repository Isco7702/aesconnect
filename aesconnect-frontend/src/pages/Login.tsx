import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';
import { showNotification, validateEmail } from '../utils/notifications';

const Login: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validation côté client
    if (!username.trim()) {
      setError('Veuillez entrer votre nom d\'utilisateur ou email');
      showNotification('Veuillez entrer votre nom d\'utilisateur ou email', 'error');
      return;
    }

    if (!password) {
      setError('Veuillez entrer votre mot de passe');
      showNotification('Veuillez entrer votre mot de passe', 'error');
      return;
    }

    try {
      const response = await api.post('/auth/login', { username, password });
      login(response.data.user);
      showNotification('Connexion réussie ! Bienvenue ' + response.data.user.username, 'success');
      navigate('/feed');
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || 'Erreur de connexion';
      setError(errorMessage);
      showNotification(errorMessage, 'error');
    }
  };

  return (
    <div className="auth-container">
      <h2>🔑 Connexion</h2>
      <form onSubmit={handleSubmit}>
        {error && <p className="error">{error}</p>}
        <div>
          <label htmlFor="username">Nom d'utilisateur ou Email *</label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Entrez votre nom d'utilisateur ou email"
            required
          />
        </div>
        <div>
          <label htmlFor="password">Mot de passe *</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Entrez votre mot de passe"
            required
            minLength={6}
          />
        </div>
        <button type="submit">🚀 Se connecter</button>
      </form>
      <p style={{ textAlign: 'center', marginTop: '20px', color: 'var(--text-muted)' }}>
        Pas encore de compte ? <Link to="/register" style={{ color: 'var(--primary-color)', fontWeight: 'bold' }}>S'inscrire</Link>
      </p>
    </div>
  );
};

export default Login;
