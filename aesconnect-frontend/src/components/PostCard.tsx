import React, { useState } from 'react';
import api from '../api/axios';
import { showNotification } from '../utils/notifications';

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

interface PostCardProps {
  post: Post;
  onLikeToggle: (postId: number, isLiked: boolean) => void;
}

const PostCard: React.FC<PostCardProps> = ({ post, onLikeToggle }) => {
  const [showReportModal, setShowReportModal] = useState(false);
  const [reportReason, setReportReason] = useState('');
  const [isReporting, setIsReporting] = useState(false);

  const handleLike = () => {
    onLikeToggle(post.id, !post.user_liked);
  };

  const handleReport = async () => {
    if (!reportReason.trim()) {
      showNotification('Veuillez indiquer une raison pour le signalement', 'error');
      return;
    }

    setIsReporting(true);
    try {
      await api.post('/utils/report', {
        reported_post_id: post.id,
        reason: reportReason
      });
      showNotification('Signalement envoyé avec succès', 'success');
      setShowReportModal(false);
      setReportReason('');
    } catch (err: any) {
      showNotification(err.response?.data?.message || 'Erreur lors du signalement', 'error');
    } finally {
      setIsReporting(false);
    }
  };

  return (
    <>
      <div className="post-card">
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
          {post.image_url && <img src={post.image_url} alt="Image du post" className="post-image" />}
        </div>
        <div className="post-actions">
          <button onClick={handleLike} className={post.user_liked ? 'liked' : ''}>
            {post.user_liked ? '❤️ J\'aime' : '🤍 J\'aime'} ({post.likes_count})
          </button>
          <button>
            💬 Commentaires ({post.comments_count})
          </button>
          <button className="report" onClick={() => setShowReportModal(true)}>
            🚩 Signaler
          </button>
        </div>
      </div>

      {/* Modal de signalement */}
      {showReportModal && (
        <div 
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0, 0, 0, 0.7)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 9999
          }}
          onClick={() => setShowReportModal(false)}
        >
          <div 
            style={{
              background: 'var(--bg-card)',
              padding: '30px',
              borderRadius: '16px',
              border: '2px solid var(--border-color)',
              maxWidth: '500px',
              width: '90%'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <h3 style={{ marginTop: 0, color: 'var(--accent-color)' }}>🚩 Signaler ce post</h3>
            <p style={{ color: 'var(--text-muted)' }}>
              Merci de nous aider à maintenir une communauté saine. Votre signalement sera examiné par notre équipe de modération.
            </p>
            
            <div style={{ marginTop: '20px' }}>
              <label style={{ display: 'block', marginBottom: '10px', fontWeight: 'bold' }}>
                Raison du signalement *
              </label>
              <textarea
                value={reportReason}
                onChange={(e) => setReportReason(e.target.value)}
                placeholder="Expliquez pourquoi vous signalez ce contenu..."
                rows={4}
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '2px solid var(--border-color)',
                  borderRadius: '8px',
                  background: 'var(--bg-dark)',
                  color: 'var(--text-light)',
                  resize: 'vertical'
                }}
              />
            </div>

            <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
              <button
                onClick={handleReport}
                disabled={isReporting}
                style={{
                  flex: 1,
                  padding: '12px',
                  background: 'var(--accent-color)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: isReporting ? 'not-allowed' : 'pointer',
                  fontWeight: 'bold',
                  opacity: isReporting ? 0.6 : 1
                }}
              >
                {isReporting ? 'Envoi...' : '📤 Envoyer le signalement'}
              </button>
              <button
                onClick={() => setShowReportModal(false)}
                style={{
                  flex: 1,
                  padding: '12px',
                  background: 'transparent',
                  color: 'var(--text-light)',
                  border: '2px solid var(--border-color)',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontWeight: 'bold'
                }}
              >
                Annuler
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default PostCard;
