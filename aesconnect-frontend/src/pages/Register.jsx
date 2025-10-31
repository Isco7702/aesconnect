import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './Register.css';

const Register = () => {
  const navigate = useNavigate();
  const { register, loading } = useAuth();
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    full_name: '',
    country: '',
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const countries = ['Mali', 'Burkina Faso', 'Niger'];

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
    setSuccess('');

    // Validation
    if (!formData.username || !formData.email || !formData.password || 
        !formData.confirmPassword || !formData.full_name) {
      setError('Veuillez remplir tous les champs obligatoires');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Les mots de passe ne correspondent pas');
      return;
    }

    if (formData.password.length < 6) {
      setError('Le mot de passe doit contenir au moins 6 caractères');
      return;
    }

    // Envoi des données
    const userData = {
      username: formData.username,
      email: formData.email,
      password: formData.password,
      full_name: formData.full_name,
      country: formData.country,
    };

    const result = await register(userData);
    
    if (result.success) {
      setSuccess(result.message);
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } else {
      setError(result.message || 'Erreur lors de l\'inscription');
    }
  };

  return (
    <div className="register-container">
      <div className="register-box">
        <div className="register-header">
          <h1>🌍 AES CONNECT</h1>
          <p className="subtitle">Rejoignez la communauté de l'Alliance des États du Sahel</p>
        </div>

        <form onSubmit={handleSubmit} className="register-form">
          <h2>Inscription</h2>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          {success && (
            <div className="success-message">
              {success}
            </div>
          )}

          <div className="form-group">
            <label htmlFor="full_name">Nom complet *</label>
            <input
              type="text"
              id="full_name"
              name="full_name"
              value={formData.full_name}
              onChange={handleChange}
              placeholder="Ex: Mohamed Traoré"
              disabled={loading}
              autoFocus
            />
          </div>

          <div className="form-group">
            <label htmlFor="username">Nom d'utilisateur *</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              placeholder="Ex: mohamed_traore"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email *</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="Ex: mohamed@example.com"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="country">Pays</label>
            <select
              id="country"
              name="country"
              value={formData.country}
              onChange={handleChange}
              disabled={loading}
            >
              <option value="">Sélectionnez votre pays</option>
              {countries.map((country) => (
                <option key={country} value={country}>
                  {country}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="password">Mot de passe *</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Au moins 6 caractères"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">Confirmer le mot de passe *</label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              placeholder="Retapez votre mot de passe"
              disabled={loading}
            />
          </div>

          <button 
            type="submit" 
            className="btn-primary"
            disabled={loading}
          >
            {loading ? 'Inscription...' : 'S\'inscrire'}
          </button>

          <div className="register-footer">
            <p>
              Vous avez déjà un compte ?{' '}
              <Link to="/login" className="link">
                Se connecter
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

export default Register;
