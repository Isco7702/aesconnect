import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Navigate } from 'react-router-dom';
import api from '../api/axios';
import { showNotification } from '../utils/notifications';

interface UserProfile {
  id: number;
  username: string;
  email: string;
  full_name: string;
  bio: string;
  avatar_url: string;
  country: string;
  city: string;
  created_at: string;
  posts_count?: number;
  followers_count?: number;
  following_count?: number;
}

const Profile: React.FC = () => {
  const { isAuthenticated, loading: authLoading, user } = useAuth();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({
    full_name: '',
    bio: '',
    country: '',
    city: '',
    avatar_url: ''
  });
  const [error, setError] = useState('');

  useEffect(() => {
    if (isAuthenticated) {
      fetchProfile();
    }
  }, [isAuthenticated]);

  const fetchProfile = async () => {
    try {
      const response = await api.get('/auth/profile');
      setProfile(response.data);
      setFormData({
        full_name: response.data.full_name || '',
        bio: response.data.bio || '',
        country: response.data.country || '',
        city: response.data.city || '',
        avatar_url: response.data.avatar_url || ''
      });
    } catch (err: any) {
      setError(err.response?.data?.message || 'Erreur lors du chargement du profil');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      const response = await api.put('/auth/profile', formData);
      setProfile(response.data);
      setEditing(false);
      showNotification('Profil mis à jour avec succès !', 'success');
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || 'Erreur lors de la mise à jour du profil';
      setError(errorMessage);
      showNotification(errorMessage, 'error');
    }
  };

  if (authLoading || loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  if (!profile) {
    return <div className="error">Impossible de charger le profil</div>;
  }

  return (
    <div className="profile-container">
      <div className="profile-header">
        <div className="profile-avatar-section">
          {profile.avatar_url ? (
            <img src={profile.avatar_url} alt={profile.username} className="profile-avatar" />
          ) : (
            <div className="profile-avatar" style={{
              background: 'var(--primary-color)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '4rem',
              color: 'white'
            }}>
              👤
            </div>
          )}
        </div>

        <div className="profile-info">
          <h2>{profile.full_name}</h2>
          <p>@{profile.username}</p>
          <p>📧 {profile.email}</p>
          {profile.country && <p>🌍 {profile.country}</p>}
          {profile.city && <p>📍 {profile.city}</p>}
          {profile.bio && <p style={{ marginTop: '15px', fontStyle: 'italic' }}>{profile.bio}</p>}
          <p style={{ fontSize: '0.85rem', marginTop: '10px' }}>
            Membre depuis {new Date(profile.created_at).toLocaleDateString('fr-FR')}
          </p>
        </div>

        <div className="profile-stats">
          <div className="stat-item">
            <span className="stat-value">{profile.posts_count || 0}</span>
            <span className="stat-label">Posts</span>
          </div>
          <div className="stat-item">
            <span className="stat-value">{profile.followers_count || 0}</span>
            <span className="stat-label">Abonnés</span>
          </div>
          <div className="stat-item">
            <span className="stat-value">{profile.following_count || 0}</span>
            <span className="stat-label">Abonnements</span>
          </div>
        </div>

        {!editing ? (
          <button 
            onClick={() => setEditing(true)}
            style={{ 
              marginTop: '20px', 
              padding: '12px 30px',
              background: 'var(--primary-color)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontWeight: 'bold',
              fontSize: '1rem'
            }}
          >
            ✏️ Modifier le profil
          </button>
        ) : null}
      </div>

      {editing && (
        <div className="auth-container" style={{ maxWidth: '700px' }}>
          <h2>Modifier mon profil</h2>
          {error && <div className="error">{error}</div>}
          
          <form onSubmit={handleSubmit}>
            <div>
              <label htmlFor="full_name">Nom complet *</label>
              <input
                type="text"
                id="full_name"
                name="full_name"
                value={formData.full_name}
                onChange={handleChange}
                required
              />
            </div>

            <div>
              <label htmlFor="bio">Biographie</label>
              <textarea
                id="bio"
                name="bio"
                value={formData.bio}
                onChange={handleChange}
                rows={4}
                placeholder="Parlez-nous de vous..."
                style={{ width: '100%', resize: 'vertical' }}
              />
            </div>

            <div>
              <label htmlFor="country">Pays</label>
              <select
                id="country"
                name="country"
                value={formData.country}
                onChange={handleChange}
              >
                <option value="">Sélectionnez un pays</option>
                <option value="Mali">🇲🇱 Mali</option>
                <option value="Burkina Faso">🇧🇫 Burkina Faso</option>
                <option value="Niger">🇳🇪 Niger</option>
                <option value="Autre">🌍 Autre</option>
              </select>
            </div>

            <div>
              <label htmlFor="city">Ville</label>
              <input
                type="text"
                id="city"
                name="city"
                value={formData.city}
                onChange={handleChange}
                placeholder="Votre ville"
              />
            </div>

            <div>
              <label htmlFor="avatar_url">URL de l'avatar</label>
              <input
                type="url"
                id="avatar_url"
                name="avatar_url"
                value={formData.avatar_url}
                onChange={handleChange}
                placeholder="https://example.com/avatar.jpg"
              />
            </div>

            <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
              <button type="submit" style={{ flex: 1 }}>
                💾 Enregistrer
              </button>
              <button 
                type="button" 
                onClick={() => setEditing(false)}
                style={{ 
                  flex: 1, 
                  background: 'var(--accent-color)' 
                }}
              >
                ❌ Annuler
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};

export default Profile;
