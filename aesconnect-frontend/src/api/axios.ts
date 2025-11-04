import axios from 'axios';

// L'URL de base de l'API Flask.
// IMPORTANT: Pour le développement local, l'API est supposée tourner sur le port 5000.
// Pour le déploiement, cette variable devra être ajustée.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000';

const api = axios.create({
    baseURL: API_BASE_URL,
    // Ceci est crucial pour que Flask puisse gérer la session (cookies)
    withCredentials: true,
    headers: {
        'Content-Type': 'application/json',
    },
});

export default api;
