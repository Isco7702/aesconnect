import React, { useState } from 'react';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';

const AUTH_USER_ID_KEY = 'aesconnect_user_id';

interface PostFormProps {
  onPostCreated: () => void;
}

const PostForm: React.FC<PostFormProps> = ({ onPostCreated }) => {
  const { user, isAuthenticated } = useAuth();
  const [content, setContent] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const storedUserId = localStorage.getItem(AUTH_USER_ID_KEY);
    const userId = user?.id ?? (storedUserId ? Number(storedUserId) : null);

    if (!isAuthenticated || !userId) {
      setError('Vous devez être connecté pour publier.');
      return;
    }

    if (!content.trim()) {
      setError('Le contenu du post est requis.');
      return;
    }

    setError('');
    setSubmitting(true);

    try {
      await api.post('/posts/create', {
        user_id: userId,
        content: content.trim(),
      });

      setContent('');
      onPostCreated();
    } catch (err: any) {
      setError(err.response?.data?.message || 'Erreur lors de la création du post');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="post-form">
      {error && <p className="error">{error}</p>}
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder="Partagez votre message..."
        rows={4}
      />
      <button type="submit" disabled={submitting}>
        {submitting ? 'Publication...' : 'Publier'}
      </button>
    </form>
  );
};

export default PostForm;
