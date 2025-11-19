import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { postsService } from '../services/api';
import './Feed.css';

const Feed = () => {
  const navigate = useNavigate();
  const { user, logout, isAuthenticated } = useAuth();
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newPost, setNewPost] = useState('');
  const [imageUrl, setImageUrl] = useState('');
  const [posting, setPosting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    fetchPosts();
  }, [isAuthenticated, navigate]);

  const fetchPosts = async () => {
    try {
      setLoading(true);
      const data = await postsService.getAllPosts();
      setPosts(data.posts || []);
    } catch (err) {
      console.error('Erreur lors du chargement des posts:', err);
      setError('Erreur lors du chargement des posts');
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePost = async (e) => {
    e.preventDefault();
    
    if (!newPost.trim()) {
      setError('Veuillez écrire quelque chose');
      return;
    }

    try {
      setPosting(true);
      setError('');
      await postsService.createPost(newPost, imageUrl);
      setNewPost('');
      setImageUrl('');
      await fetchPosts(); // Recharger les posts
    } catch (err) {
      console.error('Erreur lors de la création du post:', err);
      setError('Erreur lors de la création du post');
    } finally {
      setPosting(false);
    }
  };

  const handleLike = async (postId) => {
    try {
      await postsService.likePost(postId);
      await fetchPosts(); // Recharger pour mettre à jour les likes
    } catch (err) {
      console.error('Erreur lors du like:', err);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'À l\'instant';
    if (diffMins < 60) return `Il y a ${diffMins} min`;
    if (diffHours < 24) return `Il y a ${diffHours}h`;
    if (diffDays < 7) return `Il y a ${diffDays}j`;
    
    return date.toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="feed-container">
        <div className="loading">Chargement...</div>
      </div>
    );
  }

  return (
    <div className="feed-container">
      {/* Header */}
      <header className="feed-header">
        <div className="header-content">
          <h1>🌍 AES CONNECT</h1>
          <div className="header-actions">
            <span className="user-name">Bonjour, {user?.full_name || user?.username}</span>
            <button onClick={handleLogout} className="btn-logout">
              Déconnexion
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="feed-main">
        {/* Create Post Section */}
        <div className="create-post-card">
          <h2>Créer une publication</h2>
          
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <form onSubmit={handleCreatePost}>
            <textarea
              value={newPost}
              onChange={(e) => setNewPost(e.target.value)}
              placeholder="Quoi de neuf ?"
              rows="4"
              disabled={posting}
            />
            
            <input
              type="text"
              value={imageUrl}
              onChange={(e) => setImageUrl(e.target.value)}
              placeholder="URL de l'image (optionnel)"
              disabled={posting}
            />

            <button 
              type="submit" 
              className="btn-post"
              disabled={posting || !newPost.trim()}
            >
              {posting ? 'Publication...' : 'Publier'}
            </button>
          </form>
        </div>

        {/* Posts Feed */}
        <div className="posts-container">
          {posts.length === 0 ? (
            <div className="no-posts">
              <p>Aucune publication pour le moment.</p>
              <p>Soyez le premier à partager quelque chose !</p>
            </div>
          ) : (
            posts.map((post) => (
              <div key={post.id} className="post-card">
                <div className="post-header">
                  <div className="post-author">
                    <div className="author-avatar">
                      {post.user_avatar ? (
                        <img src={post.user_avatar} alt={post.username} />
                      ) : (
                        <div className="avatar-placeholder">
                          {post.username?.charAt(0).toUpperCase()}
                        </div>
                      )}
                    </div>
                    <div className="author-info">
                      <span className="author-name">{post.full_name || post.username}</span>
                      <span className="post-date">{formatDate(post.created_at)}</span>
                    </div>
                  </div>
                </div>

                <div className="post-content">
                  <p>{post.content}</p>
                  {post.image_url && (
                    <img 
                      src={post.image_url} 
                      alt="Post" 
                      className="post-image"
                      onError={(e) => e.target.style.display = 'none'}
                    />
                  )}
                </div>

                <div className="post-actions">
                  <button 
                    onClick={() => handleLike(post.id)}
                    className="btn-action"
                  >
                    ❤️ {post.likes_count || 0} J'aime
                  </button>
                  <button className="btn-action">
                    💬 {post.comments_count || 0} Commentaires
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="feed-footer">
        <p>🇲🇱 Mali | 🇧🇫 Burkina Faso | 🇳🇪 Niger</p>
        <p>Alliance des États du Sahel - 2025</p>
      </footer>
    </div>
  );
};

export default Feed;
