import React, { useState } from 'react';
import FlagIcon from './FlagIcon';
import CommentSection from './CommentSection';
import type { Post } from '../types';



interface PostCardProps {
  post: Post;
  onLikeToggle: (postId: number, isLiked: boolean) => void;
}

const PostCard: React.FC<PostCardProps> = ({ post, onLikeToggle }) => {
  const [showComments, setShowComments] = useState(false);
  const handleLike = () => {
    onLikeToggle(post.id, !post.user_liked);
  };

  return (
    <div className="post-card">
      <div className="post-header">
        <img src={post.avatar_url || '/default-avatar.png'} alt={post.username} className="avatar" />
          <div className="post-info">
            <strong>{post.full_name}</strong> <FlagIcon countryCode={post.country} size="small" /> (@{post.username})
          <span className="post-date">{new Date(post.created_at).toLocaleDateString()}</span>
        </div>
      </div>
      <div className="post-content">
        <p>{post.content}</p>
        {post.image_url && <img src={post.image_url} alt="Image du post" className="post-image" />}
      </div>
      <div className="post-actions">
        <button onClick={handleLike} className={post.user_liked ? 'liked liked-aes' : ''}>
          {post.user_liked ? 'Je n\'aime plus' : 'J\'aime'} ({post.likes_count})
        </button>
        <button onClick={() => setShowComments(!showComments)}>Commentaires ({post.comments_count})</button>
      </div>
      {showComments && <CommentSection postId={post.id} />}
    </div>
  );
};

export default PostCard;
