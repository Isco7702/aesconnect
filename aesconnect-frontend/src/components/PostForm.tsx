import React, { useState } from 'react';
import api from '../api/axios';

interface PostFormProps {
  onPostCreated: () => void;
}

const PostForm: React.FC<PostFormProps> = ({ onPostCreated }) => {
  const [content, setContent] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    const storedUserId = localStorage.getItem('user_id');

    if (!storedUserId) {
      setError('Vous devez être connecté pour publier un post.');
      return;
    }

    try {
      await api.post('/posts', {
        content,
        user_id: Number(storedUserId),
      });
      setContent('');
      onPostCreated();
    } catch (err: any) {
      setError(err.response?.data?.message || 'Erreur lors de la création du post');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {error && <p className="error">{error}</p>}
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder="Écrivez votre post..."
        required
      />
      <button type="submit">Publier</button>
    </form>
  );
};

export default PostForm;
