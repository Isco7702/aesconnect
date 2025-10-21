// AESConnect - Optimized JavaScript
// PWA and Performance Enhancements

// Service Worker Registration
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/service-worker.js')
            .then(registration => {
                console.log('Service Worker enregistré:', registration);
            })
            .catch(error => {
                console.log('Erreur Service Worker:', error);
            });
    });
}

// PWA Install Prompt
let deferredPrompt;
window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    showPWAInstallBanner();
});

function showPWAInstallBanner() {
    const banner = document.getElementById('pwa-install-banner');
    if (banner) {
        banner.classList.add('show');
    }
}

function installPWA() {
    const banner = document.getElementById('pwa-install-banner');
    if (banner) {
        banner.classList.remove('show');
    }
    
    if (deferredPrompt) {
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then((choiceResult) => {
            if (choiceResult.outcome === 'accepted') {
                console.log('PWA installée');
            }
            deferredPrompt = null;
        });
    }
}

function dismissPWABanner() {
    const banner = document.getElementById('pwa-install-banner');
    if (banner) {
        banner.classList.remove('show');
    }
    localStorage.setItem('pwa-banner-dismissed', 'true');
}

// Loading Screen Management
function hideLoadingScreen() {
    const loadingScreen = document.getElementById('loading-screen');
    if (loadingScreen) {
        setTimeout(() => {
            loadingScreen.classList.add('hidden');
        }, 1000);
    }
}

// Show loading screen on page navigation
function showLoadingScreen() {
    const loadingScreen = document.getElementById('loading-screen');
    if (loadingScreen) {
        loadingScreen.classList.remove('hidden');
    }
}

// Auth Tab Switching
function switchAuthTab(tab) {
    // Update tabs
    document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
    document.querySelector(`[onclick="switchAuthTab('${tab}')"]`).classList.add('active');
    
    // Update forms
    document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));
    document.getElementById(`${tab}-form`).classList.add('active');
}

// Show/Hide Charter Modal
function showCharter() {
    document.getElementById('charter-modal').classList.add('show');
}

function hideCharter() {
    document.getElementById('charter-modal').classList.remove('show');
}

// Form Validation
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePassword(password) {
    return password.length >= 6;
}

function validateUsername(username) {
    const re = /^[a-zA-Z0-9_]{3,20}$/;
    return re.test(username);
}

// Enhanced Registration with new fields
async function handleRegister(event) {
    event.preventDefault();
    
    const formData = {
        username: document.getElementById('register-username').value.trim(),
        email: document.getElementById('register-email').value.trim(),
        password: document.getElementById('register-password').value,
        full_name: document.getElementById('register-fullname').value.trim(),
        country: document.getElementById('register-country').value,
        city: document.getElementById('register-city').value.trim(),
        avatar_url: '' // Default empty, can be enhanced later
    };
    
    // Validation
    if (!validateUsername(formData.username)) {
        showNotification('Nom d\'utilisateur invalide (3-20 caractères, lettres, chiffres et _ uniquement)', 'error');
        return;
    }
    
    if (!validateEmail(formData.email)) {
        showNotification('Email invalide', 'error');
        return;
    }
    
    if (!validatePassword(formData.password)) {
        showNotification('Le mot de passe doit contenir au moins 6 caractères', 'error');
        return;
    }
    
    if (!formData.full_name) {
        showNotification('Le nom complet est requis', 'error');
        return;
    }
    
    if (!formData.country) {
        showNotification('Veuillez sélectionner votre pays', 'error');
        return;
    }
    
    showLoadingScreen();
    
    try {
        const response = await fetch('/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification('Compte créé avec succès ! Bienvenue sur AESConnect 🎉', 'success');
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            hideLoadingScreen();
            showNotification(result.error, 'error');
        }
    } catch (error) {
        hideLoadingScreen();
        showNotification('Erreur de connexion au serveur', 'error');
        console.error('Register error:', error);
    }
}

// Enhanced Login
async function handleLogin(event) {
    event.preventDefault();
    
    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value;
    
    if (!username || !password) {
        showNotification('Tous les champs sont requis', 'error');
        return;
    }
    
    showLoadingScreen();
    
    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ username, password })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification('Connexion réussie ! Bienvenue 🎉', 'success');
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            hideLoadingScreen();
            showNotification(result.error, 'error');
        }
    } catch (error) {
        hideLoadingScreen();
        showNotification('Erreur de connexion au serveur', 'error');
        console.error('Login error:', error);
    }
}

// Notification System
function showNotification(message, type = 'success') {
    // Remove existing notifications
    const existing = document.querySelector('.notification-toast');
    if (existing) {
        existing.remove();
    }
    
    const notification = document.createElement('div');
    notification.className = `notification-toast ${type}`;
    notification.innerHTML = `
        <div class="notification-icon">${type === 'success' ? '✅' : '❌'}</div>
        <div class="notification-message">${message}</div>
    `;
    
    // Add styles if not already present
    if (!document.getElementById('notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            .notification-toast {
                position: fixed;
                top: 20px;
                right: 20px;
                background: white;
                padding: 15px 20px;
                border-radius: 8px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
                display: flex;
                align-items: center;
                gap: 10px;
                z-index: 10001;
                animation: slideInRight 0.3s ease-out;
                max-width: 400px;
            }
            
            @keyframes slideInRight {
                from { transform: translateX(400px); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            
            .notification-toast.success {
                border-left: 4px solid #22c55e;
            }
            
            .notification-toast.error {
                border-left: 4px solid #ef4444;
            }
            
            .notification-icon {
                font-size: 24px;
            }
            
            .notification-message {
                flex: 1;
                color: #1f2937;
                font-weight: 500;
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(notification);
    
    // Auto remove after 4 seconds
    setTimeout(() => {
        notification.style.animation = 'slideInRight 0.3s ease-out reverse';
        setTimeout(() => notification.remove(), 300);
    }, 4000);
}

// Report Content Function
async function reportContent(contentType, contentId, reason) {
    try {
        const payload = {
            reason: reason || 'Contenu inapproprié'
        };
        
        if (contentType === 'post') {
            payload.reported_post_id = contentId;
        } else if (contentType === 'user') {
            payload.reported_user_id = contentId;
        }
        
        const response = await fetch('/report', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify(payload)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification('Signalement envoyé. Notre équipe va l\'examiner.', 'success');
        } else {
            showNotification(result.error, 'error');
        }
    } catch (error) {
        showNotification('Erreur lors du signalement', 'error');
        console.error('Report error:', error);
    }
}

// Performance Optimization: Lazy Load Images
function lazyLoadImages() {
    const images = document.querySelectorAll('img[data-src]');
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    observer.unobserve(img);
                }
            });
        });
        
        images.forEach(img => imageObserver.observe(img));
    } else {
        // Fallback for older browsers
        images.forEach(img => {
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
        });
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Hide loading screen after content is loaded
    hideLoadingScreen();
    
    // Lazy load images
    lazyLoadImages();
    
    // Check if PWA banner was dismissed
    if (!localStorage.getItem('pwa-banner-dismissed') && !window.matchMedia('(display-mode: standalone)').matches) {
        // Banner will show when beforeinstallprompt fires
    }
    
    // Close modals on overlay click
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                overlay.classList.remove('show');
            }
        });
    });
});

// Network Status Indicator
window.addEventListener('online', () => {
    showNotification('Connexion rétablie', 'success');
});

window.addEventListener('offline', () => {
    showNotification('Vous êtes hors ligne. Certaines fonctionnalités peuvent être limitées.', 'error');
});

// Prevent double form submission
let isSubmitting = false;

function preventDoubleSubmit(callback) {
    return async function(event) {
        event.preventDefault();
        
        if (isSubmitting) {
            return;
        }
        
        isSubmitting = true;
        
        try {
            await callback(event);
        } finally {
            setTimeout(() => {
                isSubmitting = false;
            }, 2000);
        }
    };
}

// Export functions for global use
window.AESConnect = {
    switchAuthTab,
    showCharter,
    hideCharter,
    handleRegister: preventDoubleSubmit(handleRegister),
    handleLogin: preventDoubleSubmit(handleLogin),
    showNotification,
    reportContent,
    installPWA,
    dismissPWABanner,
    showLoadingScreen,
    hideLoadingScreen
};
