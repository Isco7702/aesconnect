import React, { useState, useEffect } from 'react';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';
import type { Comment } from '../types';



interface CommentSectionProps {
  postId: number;
}

const CommentSection: React.FC<CommentSectionProps> = ({ postId }) => {
  const { isAuthenticated } = useAuth();
  const [comments, setComments] = useState<Comment[]>([]);
  const [newComment, setNewComment] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchComments = async () => {
    setLoading(true);
    try {
      const response = await api.get(`/posts/${postId}/comments`);
      setComments((response.data as { comments: Comment[] }).comments);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Erreur lors du chargement des commentaires');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchComments();
  }, [postId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    try {
      await api.post(`/posts/${postId}/comment`, { content: newComment });
      setNewComment('');
      fetchComments(); // Recharger les commentaires après l'ajout
    } catch (err: any) {
      setError(err.response?.data?.message || 'Erreur lors de l\'ajout du commentaire');
    }
  };

  if (loading) return <div>Chargement des commentaires...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="comment-section">
      <h4>Commentaires</h4>
      {comments.map((comment) => (
        <div key={comment.id} className="comment-item">
          <img src={comment.avatar_url || '/default-avatar.png'} alt={comment.username} className="avatar-small" />
          <div className="comment-content">
            <strong>{comment.full_name}</strong>
            <p>{comment.content}</p>
            <span className="comment-date">{new Date(comment.created_at).toLocaleDateString()}</span>
          </div>
        </div>
      ))}

      {isAuthenticated && (
        <form onSubmit={handleSubmit} className="comment-form">
          <textarea
            placeholder="Ajouter un commentaire..."
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            rows={2}
          />
          <button type="submit">Commenter</button>
        </form>
      )}
    </div>
  );
};

export default CommentSection;
