import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/axios';

const Register: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    full_name: '',
    country: '',
    city: '',
  });
  const [error, setError] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      const response = await api.post('/auth/register', formData);
      alert(response.data.message); // Succès
      navigate('/login'); // Redirection vers la page de connexion
    } catch (err: any) {
      setError(err.response?.data?.message || 'Erreur d\'inscription');
    }
  };

  return (
    <div className="auth-container">
      <h2>Inscription</h2>
      <form onSubmit={handleSubmit}>
        {error && <p className="error">{error}</p>}
        <div>
          <label htmlFor="username">Nom d'utilisateur</label>
          <input type="text" name="username" value={formData.username} onChange={handleChange} required />
        </div>
        <div>
          <label htmlFor="email">Email</label>
          <input type="email" name="email" value={formData.email} onChange={handleChange} required />
        </div>
        <div>
          <label htmlFor="password">Mot de passe</label>
          <input type="password" name="password" value={formData.password} onChange={handleChange} required />
        </div>
        <div>
          <label htmlFor="full_name">Nom complet</label>
          <input type="text" name="full_name" value={formData.full_name} onChange={handleChange} required />
        </div>
        <div>
          <label htmlFor="country">Pays</label>
          <input type="text" name="country" value={formData.country} onChange={handleChange} />
        </div>
        <div>
          <label htmlFor="city">Ville</label>
          <input type="text" name="city" value={formData.city} onChange={handleChange} />
        </div>
        <button type="submit">S'inscrire</button>
      </form>
    </div>
  );
};

export default Register;
