// Système de notifications toast pour le feedback utilisateur

export type NotificationType = 'success' | 'error' | 'info';

export const showNotification = (message: string, type: NotificationType = 'info') => {
  const container = document.getElementById('notification-container');
  if (!container) {
    console.warn('Container de notifications non trouvé');
    return;
  }

  const notification = document.createElement('div');
  notification.className = `toast-notification ${type}`;
  
  const icon = type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ';
  const iconColor = type === 'success' ? 'var(--primary-color)' : 
                    type === 'error' ? 'var(--accent-color)' : 
                    'var(--secondary-color)';
  
  notification.innerHTML = `
    <span style="font-size: 1.5rem; color: ${iconColor};">${icon}</span>
    <span style="flex: 1; color: var(--text-light);">${message}</span>
  `;

  container.appendChild(notification);

  // Animation de sortie après 4 secondes
  setTimeout(() => {
    notification.style.opacity = '0';
    notification.style.transform = 'translateX(100%)';
    
    // Suppression du DOM après l'animation
    setTimeout(() => {
      if (notification.parentNode) {
        notification.parentNode.removeChild(notification);
      }
    }, 300);
  }, 4000);
};

// Fonction helper pour valider les données
export const validateEmail = (email: string): boolean => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
};

export const validatePassword = (password: string): { valid: boolean; message?: string } => {
  if (password.length < 6) {
    return { valid: false, message: 'Le mot de passe doit contenir au moins 6 caractères' };
  }
  return { valid: true };
};

export const validateUsername = (username: string): { valid: boolean; message?: string } => {
  if (username.length < 3) {
    return { valid: false, message: 'Le nom d\'utilisateur doit contenir au moins 3 caractères' };
  }
  if (!/^[a-zA-Z0-9_]+$/.test(username)) {
    return { valid: false, message: 'Le nom d\'utilisateur ne peut contenir que des lettres, chiffres et underscores' };
  }
  return { valid: true };
};

// Protection XSS basique
export const sanitizeInput = (input: string): string => {
  const div = document.createElement('div');
  div.textContent = input;
  return div.innerHTML;
};
