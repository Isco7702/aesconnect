import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../api/axios';
import { showNotification, validateEmail, validatePassword, validateUsername } from '../utils/notifications';

const Register: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    full_name: '',
    country: '',
    city: '',
    bio: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validation côté client
    const usernameValidation = validateUsername(formData.username);
    if (!usernameValidation.valid) {
      setError(usernameValidation.message || '');
      showNotification(usernameValidation.message || 'Nom d\'utilisateur invalide', 'error');
      return;
    }

    if (!validateEmail(formData.email)) {
      setError('Adresse email invalide');
      showNotification('Adresse email invalide', 'error');
      return;
    }

    const passwordValidation = validatePassword(formData.password);
    if (!passwordValidation.valid) {
      setError(passwordValidation.message || '');
      showNotification(passwordValidation.message || 'Mot de passe invalide', 'error');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Les mots de passe ne correspondent pas');
      showNotification('Les mots de passe ne correspondent pas', 'error');
      return;
    }

    if (!formData.full_name.trim()) {
      setError('Le nom complet est requis');
      showNotification('Le nom complet est requis', 'error');
      return;
    }

    setLoading(true);

    try {
      const { confirmPassword, ...dataToSend } = formData;
      const response = await api.post('/auth/register', dataToSend);
      showNotification('Inscription réussie ! Vous pouvez maintenant vous connecter', 'success');
      setTimeout(() => {
        navigate('/login');
      }, 1500);
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || 'Erreur d\'inscription';
      setError(errorMessage);
      showNotification(errorMessage, 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container" style={{ maxWidth: '600px' }}>
      <h2>📝 Inscription</h2>
      <p style={{ textAlign: 'center', color: 'var(--text-muted)', marginBottom: '20px' }}>
        Rejoignez la communauté AESConnect
      </p>
      <form onSubmit={handleSubmit}>
        {error && <p className="error">{error}</p>}
        
        <div>
          <label htmlFor="username">Nom d'utilisateur *</label>
          <input 
            type="text" 
            name="username" 
            id="username"
            value={formData.username} 
            onChange={handleChange} 
            placeholder="choisissez_un_nom_unique"
            required 
            minLength={3}
          />
          <small style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
            Minimum 3 caractères, lettres, chiffres et underscores uniquement
          </small>
        </div>

        <div>
          <label htmlFor="email">Email *</label>
          <input 
            type="email" 
            name="email" 
            id="email"
            value={formData.email} 
            onChange={handleChange} 
            placeholder="votre.email@exemple.com"
            required 
          />
        </div>

        <div>
          <label htmlFor="password">Mot de passe *</label>
          <input 
            type="password" 
            name="password" 
            id="password"
            value={formData.password} 
            onChange={handleChange} 
            placeholder="Minimum 6 caractères"
            required 
            minLength={6}
          />
        </div>

        <div>
          <label htmlFor="confirmPassword">Confirmer le mot de passe *</label>
          <input 
            type="password" 
            name="confirmPassword" 
            id="confirmPassword"
            value={formData.confirmPassword} 
            onChange={handleChange} 
            placeholder="Répétez votre mot de passe"
            required 
            minLength={6}
          />
        </div>

        <div>
          <label htmlFor="full_name">Nom complet *</label>
          <input 
            type="text" 
            name="full_name" 
            id="full_name"
            value={formData.full_name} 
            onChange={handleChange} 
            placeholder="Prénom Nom"
            required 
          />
        </div>

        <div>
          <label htmlFor="country">Pays</label>
          <select 
            name="country" 
            id="country"
            value={formData.country} 
            onChange={handleChange}
          >
            <option value="">Sélectionnez un pays</option>
            <option value="Mali">🇲🇱 Mali</option>
            <option value="Burkina Faso">🇧🇫 Burkina Faso</option>
            <option value="Niger">🇳🇪 Niger</option>
            <option value="Sénégal">🇸🇳 Sénégal</option>
            <option value="Côte d'Ivoire">🇨🇮 Côte d'Ivoire</option>
            <option value="Autre">🌍 Autre</option>
          </select>
        </div>

        <div>
          <label htmlFor="city">Ville</label>
          <input 
            type="text" 
            name="city" 
            id="city"
            value={formData.city} 
            onChange={handleChange} 
            placeholder="Votre ville"
          />
        </div>

        <div>
          <label htmlFor="bio">Biographie (optionnel)</label>
          <textarea 
            name="bio" 
            id="bio"
            value={formData.bio} 
            onChange={handleChange} 
            placeholder="Parlez-nous de vous en quelques mots..."
            rows={3}
            style={{ width: '100%', resize: 'vertical' }}
          />
        </div>

        <button type="submit" disabled={loading}>
          {loading ? '⏳ Inscription en cours...' : '🚀 S\'inscrire'}
        </button>
      </form>
      
      <p style={{ textAlign: 'center', marginTop: '20px', color: 'var(--text-muted)' }}>
        Vous avez déjà un compte ? <Link to="/login" style={{ color: 'var(--primary-color)', fontWeight: 'bold' }}>Se connecter</Link>
      </p>
    </div>
  );
};

export default Register;
