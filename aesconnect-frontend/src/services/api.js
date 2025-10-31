import axios from 'axios';

// Configuration de l'URL du backend
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

// Instance Axios configurée
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Pour supporter les sessions/cookies
});

// Intercepteur pour gérer les erreurs globalement
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Rediriger vers login si non authentifié
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Services d'authentification
export const authService = {
  login: async (username, password) => {
    const response = await api.post('/api/login', { username, password });
    return response.data;
  },
  
  register: async (userData) => {
    const response = await api.post('/api/register', userData);
    return response.data;
  },
  
  logout: async () => {
    const response = await api.post('/api/logout');
    return response.data;
  },
  
  getCurrentUser: async () => {
    const response = await api.get('/api/user/profile');
    return response.data;
  },
};

// Services pour les posts
export const postsService = {
  getAllPosts: async () => {
    const response = await api.get('/api/posts');
    return response.data;
  },
  
  createPost: async (content, imageUrl = '') => {
    const response = await api.post('/api/posts', { content, image_url: imageUrl });
    return response.data;
  },
  
  likePost: async (postId) => {
    const response = await api.post(`/api/posts/${postId}/like`);
    return response.data;
  },
  
  commentPost: async (postId, content) => {
    const response = await api.post(`/api/posts/${postId}/comments`, { content });
    return response.data;
  },
  
  getPostComments: async (postId) => {
    const response = await api.get(`/api/posts/${postId}/comments`);
    return response.data;
  },
};

export default api;
