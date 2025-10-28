// AESConnect Enhanced - Améliorations pour l'Alliance des États du Sahel
// Développé avec Manus AI 🤖
// Version: 2.0

// ========================================
// 1. GESTION GLOBALE DES ERREURS
// ========================================

// Error Logger pour débogage
class ErrorLogger {
    constructor() {
        this.errors = [];
        this.maxErrors = 100;
    }

    log(error, context = '') {
        const errorObj = {
            message: error.message || error.toString(),
            context,
            timestamp: new Date().toISOString(),
            stack: error.stack || 'No stack trace',
            userAgent: navigator.userAgent
        };
        
        this.errors.push(errorObj);
        
        // Garder seulement les 100 dernières erreurs
        if (this.errors.length > this.maxErrors) {
            this.errors.shift();
        }
        
        // Log en console pour développement
        console.error(`[AESConnect Error] ${context}:`, error);
        
        // Envoyer au serveur pour monitoring (optionnel)
        this.sendToServer(errorObj);
    }

    sendToServer(errorObj) {
        // TODO: Implémenter l'envoi au serveur pour monitoring
        // Désactivé pour l'instant
        /*
        fetch('/api/log-error', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify(errorObj)
        }).catch(() => {}); // Ignorer les erreurs d'envoi
        */
    }

    getErrors() {
        return this.errors;
    }

    clear() {
        this.errors = [];
    }
}

const errorLogger = new ErrorLogger();

// Gestionnaire d'erreurs global
window.addEventListener('error', (event) => {
    errorLogger.log(event.error, 'Global Error Handler');
    showNotification('Une erreur est survenue. Notre équipe a été notifiée.', 'error');
});

window.addEventListener('unhandledrejection', (event) => {
    errorLogger.log(event.reason, 'Unhandled Promise Rejection');
});

// ========================================
// 2. SYSTÈME DE CHARGEMENT AMÉLIORÉ
// ========================================

class LoadingManager {
    constructor() {
        this.loadingStates = new Map();
        this.createSpinnerStyles();
    }

    createSpinnerStyles() {
        if (document.getElementById('spinner-styles')) return;
        
        const style = document.createElement('style');
        style.id = 'spinner-styles';
        style.textContent = `
            .aes-spinner-overlay {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.5);
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                z-index: 10000;
                backdrop-filter: blur(4px);
            }

            .aes-spinner {
                width: 60px;
                height: 60px;
                border: 4px solid #f3f3f3;
                border-top: 4px solid #22c55e;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }

            .aes-spinner-message {
                color: white;
                margin-top: 20px;
                font-size: 16px;
                font-weight: 500;
                text-align: center;
                max-width: 80%;
            }

            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            .inline-spinner {
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 3px solid #f3f3f3;
                border-top: 3px solid #22c55e;
                border-radius: 50%;
                animation: spin 0.8s linear infinite;
                margin-right: 8px;
                vertical-align: middle;
            }

            .skeleton-loader {
                background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
                background-size: 200% 100%;
                animation: loading 1.5s ease-in-out infinite;
                border-radius: 4px;
            }

            @keyframes loading {
                0% { background-position: 200% 0; }
                100% { background-position: -200% 0; }
            }

            .skeleton-text {
                height: 16px;
                margin-bottom: 8px;
            }

            .skeleton-title {
                height: 24px;
                margin-bottom: 12px;
                width: 60%;
            }

            .skeleton-avatar {
                width: 48px;
                height: 48px;
                border-radius: 50%;
            }
        `;
        document.head.appendChild(style);
    }

    show(id = 'global', message = 'Chargement en cours...') {
        this.loadingStates.set(id, true);
        
        let overlay = document.getElementById(`loading-${id}`);
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = `loading-${id}`;
            overlay.className = 'aes-spinner-overlay';
            overlay.innerHTML = `
                <div class="aes-spinner"></div>
                <div class="aes-spinner-message">${message}</div>
            `;
            document.body.appendChild(overlay);
        } else {
            overlay.style.display = 'flex';
            overlay.querySelector('.aes-spinner-message').textContent = message;
        }
    }

    hide(id = 'global') {
        this.loadingStates.delete(id);
        
        const overlay = document.getElementById(`loading-${id}`);
        if (overlay) {
            overlay.style.display = 'none';
        }
    }

    isLoading(id = 'global') {
        return this.loadingStates.get(id) || false;
    }

    createInlineSpinner() {
        const spinner = document.createElement('span');
        spinner.className = 'inline-spinner';
        return spinner;
    }

    createSkeletonLoader(type = 'text', count = 3) {
        const container = document.createElement('div');
        container.className = 'skeleton-container';
        
        for (let i = 0; i < count; i++) {
            const skeleton = document.createElement('div');
            skeleton.className = `skeleton-loader skeleton-${type}`;
            container.appendChild(skeleton);
        }
        
        return container;
    }
}

const loadingManager = new LoadingManager();

// ========================================
// 3. SYSTÈME DE CACHE INTELLIGENT
// ========================================

class CacheManager {
    constructor() {
        this.cache = new Map();
        this.expirationTimes = new Map();
        this.defaultTTL = 5 * 60 * 1000; // 5 minutes
    }

    set(key, value, ttl = this.defaultTTL) {
        this.cache.set(key, value);
        this.expirationTimes.set(key, Date.now() + ttl);
    }

    get(key) {
        if (!this.cache.has(key)) {
            return null;
        }

        const expirationTime = this.expirationTimes.get(key);
        if (Date.now() > expirationTime) {
            this.cache.delete(key);
            this.expirationTimes.delete(key);
            return null;
        }

        return this.cache.get(key);
    }

    has(key) {
        return this.get(key) !== null;
    }

    clear() {
        this.cache.clear();
        this.expirationTimes.clear();
    }

    clearExpired() {
        const now = Date.now();
        for (const [key, expTime] of this.expirationTimes.entries()) {
            if (now > expTime) {
                this.cache.delete(key);
                this.expirationTimes.delete(key);
            }
        }
    }
}

const cacheManager = new CacheManager();

// Nettoyer le cache expiré toutes les 5 minutes
setInterval(() => cacheManager.clearExpired(), 5 * 60 * 1000);

// ========================================
// 4. SYSTÈME DE RETRY AUTOMATIQUE
// ========================================

class RetryManager {
    constructor() {
        this.maxRetries = 3;
        this.retryDelay = 1000; // 1 seconde
    }

    async fetchWithRetry(url, options = {}, retries = this.maxRetries) {
        try {
            const response = await fetch(url, {
                ...options,
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error(`HTTP Error: ${response.status}`);
            }

            return response;
        } catch (error) {
            if (retries > 0) {
                console.log(`Retry ${this.maxRetries - retries + 1}/${this.maxRetries} pour ${url}`);
                await this.delay(this.retryDelay);
                return this.fetchWithRetry(url, options, retries - 1);
            }
            throw error;
        }
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

const retryManager = new RetryManager();

// ========================================
// 5. API CLIENT AMÉLIORÉ
// ========================================

class APIClient {
    constructor() {
        this.baseURL = '';
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        
        try {
            // Vérifier le cache d'abord pour les requêtes GET
            if (!options.method || options.method === 'GET') {
                const cachedData = cacheManager.get(url);
                if (cachedData) {
                    console.log(`Cache hit pour ${url}`);
                    return cachedData;
                }
            }

            loadingManager.show('api', 'Chargement des données...');

            const response = await retryManager.fetchWithRetry(url, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });

            const data = await response.json();

            // Mettre en cache les réponses GET réussies
            if ((!options.method || options.method === 'GET') && data.success) {
                cacheManager.set(url, data);
            }

            loadingManager.hide('api');
            return data;

        } catch (error) {
            loadingManager.hide('api');
            errorLogger.log(error, `API Request to ${endpoint}`);
            
            // Messages d'erreur en français
            if (!navigator.onLine) {
                throw new Error('Vous êtes hors ligne. Veuillez vérifier votre connexion internet.');
            } else {
                throw new Error('Erreur de connexion au serveur. Veuillez réessayer.');
            }
        }
    }

    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }

    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }
}

const apiClient = new APIClient();

// ========================================
// 6. GESTION DES POSTS AMÉLIORÉE
// ========================================

class PostManager {
    constructor() {
        this.posts = [];
        this.currentPage = 1;
        this.hasMore = true;
    }

    async loadPosts(page = 1) {
        try {
            loadingManager.show('posts', 'Chargement des publications...');
            
            const data = await apiClient.get(`/posts?page=${page}`);
            
            if (data.success) {
                if (page === 1) {
                    this.posts = data.posts;
                } else {
                    this.posts.push(...data.posts);
                }
                this.currentPage = page;
                this.hasMore = data.hasMore || false;
                this.renderPosts();
                loadingManager.hide('posts');
                return true;
            } else {
                throw new Error(data.error || 'Erreur lors du chargement des posts');
            }
        } catch (error) {
            loadingManager.hide('posts');
            errorLogger.log(error, 'Load Posts');
            showNotification(error.message, 'error');
            return false;
        }
    }

    async createPost(content, imageUrl = '') {
        try {
            if (!content.trim()) {
                showNotification('Le contenu ne peut pas être vide', 'error');
                return false;
            }

            loadingManager.show('create-post', 'Publication en cours...');

            const data = await apiClient.post('/posts', { content, image_url: imageUrl });

            loadingManager.hide('create-post');

            if (data.success) {
                showNotification('Publication créée avec succès! 🎉', 'success');
                // Invalider le cache et recharger
                cacheManager.clear();
                await this.loadPosts(1);
                return true;
            } else {
                throw new Error(data.error || 'Erreur lors de la création du post');
            }
        } catch (error) {
            loadingManager.hide('create-post');
            errorLogger.log(error, 'Create Post');
            showNotification(error.message, 'error');
            return false;
        }
    }

    async toggleLike(postId) {
        try {
            const data = await apiClient.post(`/posts/${postId}/like`, {});

            if (data.success) {
                // Mettre à jour le post localement
                const post = this.posts.find(p => p.id === postId);
                if (post) {
                    post.user_liked = data.liked ? 1 : 0;
                    post.likes_count = data.likes_count;
                    this.updatePostUI(postId);
                }
                
                // Animation de like
                this.animateLike(postId, data.liked);
                
                return true;
            } else {
                throw new Error(data.error || 'Erreur lors du like');
            }
        } catch (error) {
            errorLogger.log(error, 'Toggle Like');
            showNotification(error.message, 'error');
            return false;
        }
    }

    animateLike(postId, liked) {
        const likeButton = document.querySelector(`[data-post-id="${postId}"] .like-button`);
        if (likeButton) {
            likeButton.classList.add(liked ? 'liked-animation' : 'unliked-animation');
            setTimeout(() => {
                likeButton.classList.remove('liked-animation', 'unliked-animation');
            }, 300);
        }
    }

    updatePostUI(postId) {
        const post = this.posts.find(p => p.id === postId);
        if (!post) return;

        const postElement = document.querySelector(`[data-post-id="${postId}"]`);
        if (!postElement) return;

        const likeButton = postElement.querySelector('.like-button');
        const likeCount = postElement.querySelector('.like-count');

        if (likeButton) {
            likeButton.classList.toggle('liked', post.user_liked === 1);
            likeButton.innerHTML = post.user_liked ? '❤️ J\'aime' : '🤍 J\'aime';
        }

        if (likeCount) {
            likeCount.textContent = post.likes_count;
        }
    }

    renderPosts() {
        const container = document.getElementById('posts-container');
        if (!container) return;

        if (this.posts.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📝</div>
                    <h3>Aucune publication pour le moment</h3>
                    <p>Soyez le premier à publier quelque chose!</p>
                </div>
            `;
            return;
        }

        container.innerHTML = this.posts.map(post => this.renderPost(post)).join('');
    }

    renderPost(post) {
        return `
            <div class="post-card" data-post-id="${post.id}">
                <div class="post-header">
                    <div class="post-author">
                        <div class="avatar">${post.username[0].toUpperCase()}</div>
                        <div>
                            <div class="author-name">${post.full_name || post.username}</div>
                            <div class="post-time">${this.formatTime(post.created_at)}</div>
                        </div>
                    </div>
                    <button class="post-menu-button" onclick="showPostMenu(${post.id})">⋮</button>
                </div>
                <div class="post-content">${this.escapeHtml(post.content)}</div>
                ${post.image_url ? `<img src="${post.image_url}" alt="Post image" class="post-image">` : ''}
                <div class="post-actions">
                    <button class="post-action-button like-button ${post.user_liked ? 'liked' : ''}" 
                            onclick="postManager.toggleLike(${post.id})">
                        ${post.user_liked ? '❤️' : '🤍'} J'aime
                    </button>
                    <span class="like-count">${post.likes_count || 0}</span>
                    <button class="post-action-button" onclick="showComments(${post.id})">
                        💬 Commenter
                    </button>
                    <span class="comment-count">${post.comments_count || 0}</span>
                    <button class="post-action-button" onclick="sharePost(${post.id})">
                        📤 Partager
                    </button>
                </div>
            </div>
        `;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = Math.floor((now - date) / 1000); // différence en secondes

        if (diff < 60) return 'À l\'instant';
        if (diff < 3600) return `Il y a ${Math.floor(diff / 60)} min`;
        if (diff < 86400) return `Il y a ${Math.floor(diff / 3600)} h`;
        if (diff < 604800) return `Il y a ${Math.floor(diff / 86400)} j`;
        
        return date.toLocaleDateString('fr-FR', { 
            day: 'numeric', 
            month: 'short', 
            year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined 
        });
    }
}

const postManager = new PostManager();

// ========================================
// 7. SYSTÈME DE RECHERCHE
// ========================================

class SearchManager {
    constructor() {
        this.searchCache = new Map();
        this.debounceTimer = null;
    }

    async search(query, type = 'all') {
        if (!query.trim()) return { users: [], posts: [], groups: [] };

        try {
            // Vérifier le cache
            const cacheKey = `search-${type}-${query}`;
            if (this.searchCache.has(cacheKey)) {
                return this.searchCache.get(cacheKey);
            }

            loadingManager.show('search', 'Recherche en cours...');

            const data = await apiClient.get(`/search?q=${encodeURIComponent(query)}&type=${type}`);

            loadingManager.hide('search');

            if (data.success) {
                this.searchCache.set(cacheKey, data);
                return data;
            } else {
                throw new Error(data.error || 'Erreur lors de la recherche');
            }
        } catch (error) {
            loadingManager.hide('search');
            errorLogger.log(error, 'Search');
            showNotification(error.message, 'error');
            return { users: [], posts: [], groups: [] };
        }
    }

    debounceSearch(query, callback, delay = 500) {
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => {
            this.search(query).then(callback);
        }, delay);
    }
}

const searchManager = new SearchManager();

// ========================================
// 8. NOTIFICATIONS AMÉLIORÉES
// ========================================

function showNotification(message, type = 'success', duration = 4000) {
    // Supprimer les notifications existantes
    document.querySelectorAll('.notification-toast').forEach(n => n.remove());
    
    const notification = document.createElement('div');
    notification.className = `notification-toast aes-notification-${type}`;
    
    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };
    
    notification.innerHTML = `
        <div class="notification-icon">${icons[type] || icons.info}</div>
        <div class="notification-content">
            <div class="notification-message">${message}</div>
        </div>
        <button class="notification-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    // Ajouter les styles si pas déjà présents
    if (!document.getElementById('aes-notification-styles')) {
        const style = document.createElement('style');
        style.id = 'aes-notification-styles';
        style.textContent = `
            .notification-toast {
                position: fixed;
                top: 20px;
                right: 20px;
                min-width: 300px;
                max-width: 500px;
                background: white;
                padding: 16px 20px;
                border-radius: 12px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
                display: flex;
                align-items: center;
                gap: 12px;
                z-index: 10001;
                animation: slideInRight 0.3s ease-out;
            }
            
            @keyframes slideInRight {
                from { transform: translateX(400px); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            
            .aes-notification-success {
                border-left: 4px solid #22c55e;
            }
            
            .aes-notification-error {
                border-left: 4px solid #ef4444;
            }
            
            .aes-notification-warning {
                border-left: 4px solid #f59e0b;
            }
            
            .aes-notification-info {
                border-left: 4px solid #3b82f6;
            }
            
            .notification-icon {
                font-size: 24px;
                flex-shrink: 0;
            }
            
            .notification-content {
                flex: 1;
            }
            
            .notification-message {
                color: #1f2937;
                font-weight: 500;
                line-height: 1.5;
            }
            
            .notification-close {
                background: none;
                border: none;
                font-size: 24px;
                color: #9ca3af;
                cursor: pointer;
                padding: 0;
                width: 24px;
                height: 24px;
                display: flex;
                align-items: center;
                justify-content: center;
                flex-shrink: 0;
                transition: color 0.2s;
            }
            
            .notification-close:hover {
                color: #1f2937;
            }

            @media (max-width: 640px) {
                .notification-toast {
                    left: 20px;
                    right: 20px;
                    min-width: auto;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(notification);
    
    // Vibration sur mobile pour feedback
    if (navigator.vibrate && type === 'success') {
        navigator.vibrate(100);
    }
    
    // Auto-suppression
    setTimeout(() => {
        notification.style.animation = 'slideInRight 0.3s ease-out reverse';
        setTimeout(() => notification.remove(), 300);
    }, duration);
}

// ========================================
// 9. INITIALISATION
// ========================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 AESConnect Enhanced chargé');
    console.log('🇲🇱 Mali | 🇳🇪 Niger | 🇧🇫 Burkina Faso');
    
    // Charger les posts si on est sur la page principale
    const postsContainer = document.getElementById('posts-container');
    if (postsContainer) {
        postManager.loadPosts(1);
    }
    
    // Initialiser la recherche si présente
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            searchManager.debounceSearch(e.target.value, (results) => {
                // Render results
                console.log('Search results:', results);
            });
        });
    }
});

// ========================================
// 10. EXPORT DES FONCTIONS GLOBALES
// ========================================

window.AESConnectEnhanced = {
    errorLogger,
    loadingManager,
    cacheManager,
    retryManager,
    apiClient,
    postManager,
    searchManager,
    showNotification
};

console.log('✅ AESConnect Enhanced initialisé avec succès!');
