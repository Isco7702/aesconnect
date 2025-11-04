import React, { useState } from 'react';
import api from '../api/axios';

interface PostFormProps {
  onPostCreated: () => void;
}

const PostForm: React.FC<PostFormProps> = ({ onPostCreated }) => {
  const [content, setContent] = useState('');
  const [image, setImage] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setImage(e.target.files[0]);
    } else {
      setImage(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content && !image) {
      setError('Veuillez écrire quelque chose ou ajouter une image.');
      return;
    }

    setLoading(true);
    setError('');

    const formData = new FormData();
    formData.append('content', content);
    if (image) {
      formData.append('image', image);
    }

    try {
      await api.post('/posts/create', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      setContent('');
      setImage(null);
      onPostCreated(); // Notifie le Feed pour recharger les posts
    } catch (err: any) {
      setError(err.response?.data?.message || 'Erreur lors de la création du post.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="post-form-container">
      <h3>Créer un nouveau post</h3>
      <form onSubmit={handleSubmit}>
        {error && <p className="error">{error}</p>}
        <textarea
          placeholder="Quoi de neuf ?"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          rows={3}
        />
        <div className="file-input-group">
          <label htmlFor="image-upload">Ajouter une image :</label>
          <input
            type="file"
            id="image-upload"
            accept="image/*"
            onChange={handleFileChange}
          />
          {image && <p className="file-name">{image.name}</p>}
        </div>
        <button type="submit" disabled={loading}>
          {loading ? 'Publication...' : 'Publier'}
        </button>
      </form>
    </div>
  );
};

export default PostForm;
