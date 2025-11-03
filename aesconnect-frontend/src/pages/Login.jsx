import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './Login.css';

const Login = () => {
  const navigate = useNavigate();
  const { login, loading } = useAuth();
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });
  const [error, setError] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!formData.username || !formData.password) {
      setError('Veuillez remplir tous les champs');
      return;
    }

    const result = await login(formData.username, formData.password);
    
    if (result.success) {
      navigate('/feed');
    } else {
      setError(result.message || 'Erreur lors de la connexion');
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <div className="login-header">
          <h1>🌍 AES CONNECT</h1>
          <p className="subtitle">Alliance des États du Sahel</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <h2>Connexion</h2>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <div className="form-group">
            <label htmlFor="username">Nom d'utilisateur</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              placeholder="Entrez votre nom d'utilisateur"
              disabled={loading}
              autoFocus
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Mot de passe</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Entrez votre mot de passe"
              disabled={loading}
            />
          </div>

          <button 
            type="submit" 
            className="btn-primary"
            disabled={loading}
          >
            {loading ? 'Connexion...' : 'Se connecter'}
          </button>

          <div className="login-footer">
            <p>
              Pas encore de compte ?{' '}
              <Link to="/register" className="link">
                S'inscrire
              </Link>
            </p>
          </div>
        </form>

        <div className="country-flags">
          <span>🇲🇱 Mali</span>
          <span>🇧🇫 Burkina Faso</span>
          <span>🇳🇪 Niger</span>
        </div>
      </div>
    </div>
  );
};

export default Login;
