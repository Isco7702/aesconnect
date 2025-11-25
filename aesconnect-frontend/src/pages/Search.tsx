import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Navigate } from 'react-router-dom';
import api from '../api/axios';

interface SearchUser {
  id: number;
  username: string;
  full_name: string;
  avatar_url: string;
  bio: string;
  country: string;
  city: string;
}

interface SearchPost {
  id: number;
  user_id: number;
  content: string;
  image_url: string;
  created_at: string;
  username: string;
  full_name: string;
  avatar_url: string;
  likes_count: number;
  comments_count: number;
}

const Search: React.FC = () => {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const [searchQuery, setSearchQuery] = useState('');
  const [searchType, setSearchType] = useState<'users' | 'posts'>('users');
  const [users, setUsers] = useState<SearchUser[]>([]);
  const [posts, setPosts] = useState<SearchPost[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searched, setSearched] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setLoading(true);
    setError('');
    setSearched(true);

    try {
      if (searchType === 'users') {
        const response = await api.get(`/utils/search/users?q=${encodeURIComponent(searchQuery)}`);
        setUsers(response.data.users || []);
        setPosts([]);
      } else {
        const response = await api.get(`/utils/search/posts?q=${encodeURIComponent(searchQuery)}`);
        setPosts(response.data.posts || []);
        setUsers([]);
      }
    } catch (err: any) {
      setError(err.response?.data?.message || 'Erreur lors de la recherche');
      setUsers([]);
      setPosts([]);
    } finally {
      setLoading(false);
    }
  };

  if (authLoading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  return (
    <div className="search-container">
      <h2>🔍 Recherche</h2>
      
      <form onSubmit={handleSearch} className="search-box">
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder={searchType === 'users' ? 'Rechercher des utilisateurs...' : 'Rechercher des posts...'}
        />
        <select 
          value={searchType}
          onChange={(e) => setSearchType(e.target.value as 'users' | 'posts')}
          style={{
            padding: '14px 20px',
            border: '2px solid var(--border-color)',
            borderRadius: '12px',
            background: 'var(--bg-card)',
            color: 'var(--text-light)',
            cursor: 'pointer'
          }}
        >
          <option value="users">👥 Utilisateurs</option>
          <option value="posts">📝 Posts</option>
        </select>
        <button type="submit" disabled={loading}>
          {loading ? 'Recherche...' : 'Rechercher'}
        </button>
      </form>

      {error && <div className="error">{error}</div>}

      {loading && (
        <div className="loading-container">
          <div className="loading-spinner"></div>
        </div>
      )}

      {!loading && searched && searchType === 'users' && (
        <div className="search-results">
          <h3>Résultats ({users.length})</h3>
          {users.length === 0 ? (
            <p style={{ textAlign: 'center', color: 'var(--text-muted)', marginTop: '40px' }}>
              Aucun utilisateur trouvé pour "{searchQuery}"
            </p>
          ) : (
            users.map((user) => (
              <div key={user.id} className="user-card">
                {user.avatar_url ? (
                  <img src={user.avatar_url} alt={user.username} className="avatar" />
                ) : (
                  <div 
                    className="avatar" 
                    style={{
                      background: 'var(--primary-color)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '2rem',
                      color: 'white'
                    }}
                  >
                    👤
                  </div>
                )}
                <div className="user-card-info">
                  <h3>{user.full_name}</h3>
                  <p>@{user.username}</p>
                  {user.bio && <p style={{ marginTop: '8px', fontStyle: 'italic' }}>{user.bio}</p>}
                  {(user.country || user.city) && (
                    <p style={{ marginTop: '5px', fontSize: '0.9rem' }}>
                      📍 {user.city ? `${user.city}, ` : ''}{user.country}
                    </p>
                  )}
                </div>
                <button
                  style={{
                    padding: '10px 20px',
                    background: 'var(--primary-color)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    fontWeight: 'bold'
                  }}
                  onClick={() => alert('Fonctionnalité de suivi à implémenter')}
                >
                  ➕ Suivre
                </button>
              </div>
            ))
          )}
        </div>
      )}

      {!loading && searched && searchType === 'posts' && (
        <div className="search-results">
          <h3>Résultats ({posts.length})</h3>
          {posts.length === 0 ? (
            <p style={{ textAlign: 'center', color: 'var(--text-muted)', marginTop: '40px' }}>
              Aucun post trouvé pour "{searchQuery}"
            </p>
          ) : (
            <div className="posts-list">
              {posts.map((post) => (
                <div key={post.id} className="post-card">
                  <div className="post-header">
                    {post.avatar_url ? (
                      <img src={post.avatar_url} alt={post.username} className="avatar" />
                    ) : (
                      <div 
                        className="avatar"
                        style={{
                          background: 'var(--primary-color)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontSize: '1.5rem',
                          color: 'white'
                        }}
                      >
                        👤
                      </div>
                    )}
                    <div className="post-info">
                      <strong>{post.full_name}</strong>
                      <span className="post-date">
                        @{post.username} • {new Date(post.created_at).toLocaleDateString('fr-FR')}
                      </span>
                    </div>
                  </div>
                  <div className="post-content">
                    <p>{post.content}</p>
                    {post.image_url && <img src={post.image_url} alt="Post" className="post-image" />}
                  </div>
                  <div className="post-actions">
                    <span>❤️ {post.likes_count}</span>
                    <span>💬 {post.comments_count}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Search;
