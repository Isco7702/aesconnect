export interface User {
  id: number;
  username: string;
  full_name: string;
  email: string;
  city: string;
  country: string;
  avatar_url: string;
  is_admin: boolean;
}

export interface Post {
  avatar_url: string;
  user_liked: boolean;
  id: number;
  user_id: number;
  username: string;
  full_name: string;
  country: string;
  content: string;
  image_url: string | null;
  created_at: string;
  likes_count: number;
  comments_count: number;
  is_liked: boolean;
}

export interface Comment {
  avatar_url: string;
  id: number;
  post_id: number;
  user_id: number;
  username: string;
  full_name: string;
  content: string;
  created_at: string;
}

export interface Notification {
  id: number;
  user_id: number;
  type: 'like' | 'comment' | 'follow';
  content: string;
  is_read: boolean;
  created_at: string;
}

