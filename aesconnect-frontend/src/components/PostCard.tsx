import React from 'react';

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
  const handleLike = () => {
    onLikeToggle(post.id, !post.user_liked);
  };

  return (
    <div className="post-card">
      <div className="post-header">
        <img src={post.avatar_url || '/default-avatar.png'} alt={post.username} className="avatar" />
        <div className="post-info">
          <strong>{post.full_name}</strong> (@{post.username})
          <span className="post-date">{new Date(post.created_at).toLocaleDateString()}</span>
        </div>
      </div>
      <div className="post-content">
        <p>{post.content}</p>
        {post.image_url && <img src={post.image_url} alt="Image du post" className="post-image" />}
      </div>
      <div className="post-actions">
        <button onClick={handleLike} className={post.user_liked ? 'liked' : ''}>
          {post.user_liked ? 'Je n\'aime plus' : 'J\'aime'} ({post.likes_count})
        </button>
        <button>Commentaires ({post.comments_count})</button>
      </div>
    </div>
  );
};

export default PostCard;
