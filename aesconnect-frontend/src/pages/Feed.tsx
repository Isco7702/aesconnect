import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Navigate } from 'react-router-dom';
import api from '../api/axios';
import PostCard from '../components/PostCard';
import PostForm from '../components/PostForm';

interface Post {
  id: number;
  user_id: number;
  content: string;
  image_url: string | null;
  created_at: string;
  likes_count: number;
  comments_count: number;
  username: string;
  full_name: string;
  avatar_url: string;
  user_liked: boolean;
}

const Feed: React.FC = () => {
  const { isAuthenticated, loading } = useAuth();
  const [posts, setPosts] = useState<Post[]>([]);
  const [likeLoading, setLikeLoading] = useState(false);
  const [feedLoading, setFeedLoading] = useState(true);
  const [refreshKey, setRefreshKey] = useState(0);
  const [error, setError] = useState('');

  useEffect(() => {
    if (isAuthenticated) {
      const fetchPosts = async () => {
        try {
          const response = await api.get('/posts/posts');
          setPosts(response.data.posts);
        } catch (err: any) {
          setError(err.response?.data?.message || 'Erreur lors du chargement du fil d\'actualité');
        } finally {
          setFeedLoading(false);
        }
      };
      fetchPosts();
    }
  }, [isAuthenticated, refreshKey]); // Déclenche le rechargement quand refreshKey change

  const handlePostCreated = () => {
    setRefreshKey(prevKey => prevKey + 1); // Incrémente la clé pour forcer le rechargement
  };

  const handleLikeToggle = async (postId: number, isLiked: boolean) => {
    if (likeLoading) return;

    setLikeLoading(true);
    try {
      await api.post(`/posts/like/${postId}`);
      
      // Mise à jour optimiste de l'interface utilisateur
      setPosts(prevPosts => prevPosts.map(post => {
        if (post.id === postId) {
          return {
            ...post,
            user_liked: isLiked,
            likes_count: post.likes_count + (isLiked ? 1 : -1)
          };
        }
        return post;
      }));
    } catch (err) {
      setError('Erreur lors de l\'opération J\'aime.');
    } finally {
      setLikeLoading(false);
    }
  };

  if (loading || feedLoading) {
    return <div>Chargement...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  return (
    <div className="feed-container">
      <h2>Fil d'actualité</h2>
      <PostForm onPostCreated={handlePostCreated} />
      {error && <p className="error">{error}</p>}
      {posts.length === 0 && !feedLoading ? (
        <p>Aucun post à afficher pour le moment.</p>
      ) : (
        <div className="posts-list">
          {posts.map((post) => (
            <PostCard key={post.id} post={post} onLikeToggle={handleLikeToggle} />
          ))}
        </div>
      )}
    </div>
  );
};

export default Feed;
