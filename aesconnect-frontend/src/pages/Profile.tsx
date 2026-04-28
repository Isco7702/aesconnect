import React, { useState } from 'react';
import FlagIcon from '../components/FlagIcon';
import { useAuth } from '../context/AuthContext';
import api from '../api/axios';
import { Navigate } from 'react-router-dom';

const Profile: React.FC = () => {
  const { user, isAuthenticated, loading, login } = useAuth();
  const [image, setImage] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  if (loading) return <div>Chargement du profil...</div>;
  if (!isAuthenticated || !user) return <Navigate to="/login" />;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setImage(e.target.files[0]);
      setMessage('');
      setError('');
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!image) {
      setError('Veuillez sélectionner une image.');
      return;
    }

    setUploading(true);
    setMessage('');
    setError('');

    const formData = new FormData();
    formData.append('image', image);

    try {
      const response = await api.post('/auth/profile/avatar', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      // Mise à jour du contexte utilisateur avec la nouvelle URL d'avatar
      login({ ...user, avatar_url: (response.data as { avatar_url: string }).avatar_url });
      setMessage('Photo de profil mise à jour avec succès !');
      setImage(null);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Erreur lors de l\'upload de la photo de profil.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="profile-container">
      <h2>Mon Profil</h2>
      <div className="avatar-display">
        <img src={user.avatar_url || '/default-avatar.png'} alt={user.username} className="avatar-large" />
        <h3>{user.full_name} <FlagIcon countryCode={user.country} size="medium" /> (@{user.username})</h3>
        <p>Email: {user.email}</p>
        <p>Localisation: {user.city}, {user.country}</p>
      </div>

      <div className="avatar-upload-section">
        <h4>Changer ma photo de profil</h4>
        {message && <p className="success-message">{message}</p>}
        {error && <p className="error">{error}</p>}
        <form onSubmit={handleUpload}>
          <input
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            disabled={uploading}
          />
          <button type="submit" disabled={uploading || !image}>
            {uploading ? 'Téléchargement...' : 'Télécharger'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Profile;
