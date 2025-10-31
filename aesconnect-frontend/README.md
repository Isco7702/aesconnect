# 🌍 AES CONNECT - Frontend React + Vite

Frontend moderne pour AES Connect, le réseau social de l'Alliance des États du Sahel.

## 📋 Technologies Utilisées

- **React 18** - Bibliothèque d'interface utilisateur
- **Vite** - Build tool ultra-rapide
- **React Router** - Gestion des routes
- **Axios** - Client HTTP pour les requêtes API
- **CSS3** - Styles modernes et responsive

## 🚀 Démarrage Rapide

### Prérequis

- Node.js (version 16 ou supérieure)
- npm ou yarn

### Installation

```bash
# 1. Aller dans le répertoire du frontend
cd aesconnect-frontend

# 2. Installer les dépendances
npm install

# 3. Lancer l'application en mode développement
npm run dev
```

L'application sera accessible à : **http://localhost:5173**

## 📁 Structure du Projet

```
aesconnect-frontend/
├── src/
│   ├── contexts/
│   │   └── AuthContext.jsx      # Contexte d'authentification
│   ├── pages/
│   │   ├── Login.jsx            # Page de connexion
│   │   ├── Login.css
│   │   ├── Register.jsx         # Page d'inscription
│   │   ├── Register.css
│   │   ├── Feed.jsx             # Fil d'actualité
│   │   └── Feed.css
│   ├── services/
│   │   └── api.js               # Services API avec Axios
│   ├── App.jsx                  # Composant principal avec routes
│   ├── App.css                  # Styles globaux
│   └── main.jsx                 # Point d'entrée
├── .env                         # Variables d'environnement
├── vite.config.js               # Configuration Vite
└── package.json
```

## 🔌 Connexion au Backend

Le frontend communique avec le backend Flask qui doit tourner sur le port 5000.

**Important** : Avant de lancer le frontend, assurez-vous que le backend est démarré.

```bash
# Dans un autre terminal, lancer le backend Flask
cd /home/user/webapp
python3 app.py
```

### Configuration de l'API

L'URL de l'API est configurée dans le fichier `.env` :

```env
VITE_API_URL=http://localhost:5000
```

## 📱 Fonctionnalités

### Pages Implémentées

1. **Page de Connexion (`/login`)** :
   - Formulaire de connexion avec validation
   - Gestion des erreurs
   - Redirection vers le feed après connexion

2. **Page d'Inscription (`/register`)** :
   - Formulaire d'inscription complet
   - Validation des champs
   - Sélection du pays (Mali, Burkina Faso, Niger)

3. **Page Feed (`/feed`)** :
   - Création de nouveaux posts
   - Affichage de la liste des posts
   - Système de likes
   - Support d'images
   - Déconnexion

### Gestion de l'Authentification

L'authentification est gérée via `AuthContext` qui fournit :
- `user` - Utilisateur connecté
- `login(username, password)` - Connexion
- `register(userData)` - Inscription
- `logout()` - Déconnexion
- `isAuthenticated` - Statut de connexion

## 🎨 Design

- **Palette de couleurs** : Dégradé violet (#667eea → #764ba2)
- **Responsive** : Compatible mobile, tablette et desktop
- **Interface moderne** : Design épuré et professionnel
- **Expérience utilisateur** : Navigation fluide avec React Router

## 🔧 Scripts Disponibles

```bash
# Lancer en mode développement
npm run dev

# Build pour la production
npm run build

# Prévisualiser le build de production
npm run preview

# Linter (ESLint)
npm run lint
```

## 🌐 Déploiement

### Build de Production

```bash
npm run build
```

Le build sera généré dans le dossier `dist/`.

### Variables d'Environnement pour Production

Créez un fichier `.env.production` :

```env
VITE_API_URL=https://votre-api-backend.com
```

## 🐛 Dépannage

### Le frontend ne se connecte pas au backend

1. Vérifiez que le backend Flask tourne sur le port 5000
2. Vérifiez la configuration CORS dans le backend
3. Vérifiez l'URL de l'API dans `.env`

### Erreur de CORS

Le backend Flask doit avoir CORS activé. Vérifiez que `flask-cors` est installé et configuré.

## 📝 API Endpoints Utilisés

- `POST /api/register` - Inscription
- `POST /api/login` - Connexion
- `POST /api/logout` - Déconnexion
- `GET /api/user/profile` - Profil utilisateur
- `GET /api/posts` - Liste des posts
- `POST /api/posts` - Créer un post
- `POST /api/posts/:id/like` - Liker un post

## 🤝 Contribution

Les contributions sont les bienvenues ! Suivez les standards de code existants.

## 📄 Licence

MIT

---

**Fait avec ❤️ pour l'Alliance des États du Sahel**

🇲🇱 Mali | 🇧🇫 Burkina Faso | 🇳🇪 Niger
