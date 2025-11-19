# 🚀 Guide de Lancement Complet - AES CONNECT

Guide complet pour lancer l'application AES Connect avec son backend Flask et son frontend React.

## 📋 Architecture de l'Application

L'application AES Connect est composée de deux parties distinctes :

1. **Backend** : API Flask (Python) - Port 5000
2. **Frontend** : Application React + Vite - Port 5173

```
/home/user/webapp/
├── aesconnect-frontend/     # Frontend React + Vite
│   ├── src/
│   │   ├── contexts/       # Contexte d'authentification
│   │   ├── pages/          # Pages (Login, Register, Feed)
│   │   ├── services/       # Services API (Axios)
│   │   └── ...
│   └── package.json
│
├── app.py                   # Backend Flask (API)
├── requirements.txt
├── templates/
├── static/
└── ...
```

## 🔧 Prérequis

### Backend
- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Frontend
- Node.js 16 ou supérieur
- npm ou yarn

## 📦 Installation

### 1. Installation du Backend

```bash
cd /home/user/webapp

# Installer les dépendances Python
pip install -r requirements.txt
```

### 2. Installation du Frontend

```bash
cd /home/user/webapp/aesconnect-frontend

# Installer les dépendances npm
npm install
```

## 🚀 Lancement de l'Application

### Option 1 : Lancement Manuel (Deux Terminaux)

#### Terminal 1 - Backend Flask

```bash
# Aller dans le répertoire du Backend
cd /home/user/webapp

# Lancer l'API Flask
python3 app.py
```

Le backend sera accessible à : **http://localhost:5000**

#### Terminal 2 - Frontend React

```bash
# Aller dans le répertoire du Frontend
cd /home/user/webapp/aesconnect-frontend

# Lancer l'application React
npm run dev
```

Le frontend sera accessible à : **http://localhost:5173**

### Option 2 : Lancement avec Gunicorn (Production-like)

#### Backend avec Gunicorn

```bash
cd /home/user/webapp

# Installer Gunicorn si ce n'est pas déjà fait
pip install gunicorn

# Lancer avec Gunicorn (4 workers)
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 🌐 Accès à l'Application

1. **Ouvrir le navigateur** et aller à : **http://localhost:5173**
2. **Page de Login** : Vous verrez la page de connexion
3. **Créer un compte** : Cliquez sur "S'inscrire"
4. **Se connecter** : Utilisez vos identifiants
5. **Feed** : Accédez au fil d'actualité

## 📱 Fonctionnalités Disponibles

### Page de Login (`/login`)
- Connexion avec nom d'utilisateur et mot de passe
- Validation des champs
- Gestion des erreurs
- Redirection vers le feed après connexion

### Page d'Inscription (`/register`)
- Création de compte
- Champs : Nom complet, Username, Email, Pays, Mot de passe
- Validation (mot de passe minimum 6 caractères)
- Confirmation du mot de passe

### Page Feed (`/feed`)
- **Créer des posts** : Texte + URL d'image optionnelle
- **Voir les posts** : Liste des publications de tous les utilisateurs
- **Liker** : Système de likes
- **Profil utilisateur** : Nom affiché dans l'en-tête
- **Déconnexion** : Bouton pour se déconnecter

## 🔐 Variables d'Environnement

### Backend (Flask)

Vous pouvez définir ces variables :

```bash
export SECRET_KEY="votre_clé_secrète"
export FLASK_ENV="development"
export DATABASE_PATH="./social_network.db"
```

### Frontend (React)

Fichier `.env` dans `aesconnect-frontend/` :

```env
VITE_API_URL=http://localhost:5000
```

## 🧪 Test de l'Application

### 1. Créer un Compte de Test

1. Aller à http://localhost:5173/register
2. Remplir le formulaire :
   - Nom complet : Mohamed Traoré
   - Username : mohamed_test
   - Email : mohamed@test.com
   - Pays : Mali
   - Mot de passe : test123
   - Confirmer : test123
3. Cliquer sur "S'inscrire"

### 2. Se Connecter

1. Aller à http://localhost:5173/login
2. Username : mohamed_test
3. Mot de passe : test123
4. Cliquer sur "Se connecter"

### 3. Créer un Post

1. Une fois connecté, vous êtes sur `/feed`
2. Écrire quelque chose dans la zone de texte
3. (Optionnel) Ajouter une URL d'image
4. Cliquer sur "Publier"

### 4. Tester les Likes

- Cliquer sur le bouton "❤️ J'aime" sous un post
- Le compteur de likes devrait augmenter

## 🐛 Dépannage

### Problème : Le frontend ne se connecte pas au backend

**Solution** :
1. Vérifier que le backend tourne sur le port 5000
2. Vérifier la console du navigateur (F12) pour les erreurs CORS
3. Vérifier le fichier `.env` du frontend

### Problème : Erreur CORS

**Solution** :
Le backend Flask a déjà `flask-cors` configuré. Si le problème persiste :

```bash
# Installer flask-cors
pip install flask-cors
```

### Problème : "Module not found" dans le frontend

**Solution** :
```bash
cd /home/user/webapp/aesconnect-frontend
npm install
```

### Problème : Base de données verrouillée

**Solution** :
```bash
# Arrêter toutes les instances de l'application
# Supprimer le fichier de base de données
rm /home/user/webapp/social_network.db

# Relancer l'application (la DB sera recréée)
python3 app.py
```

## 📊 Endpoints API Utilisés

### Authentification
- `POST /api/register` - Inscription
- `POST /api/login` - Connexion
- `POST /api/logout` - Déconnexion
- `GET /api/user/profile` - Profil utilisateur

### Posts
- `GET /api/posts` - Liste des posts
- `POST /api/posts` - Créer un post
- `POST /api/posts/:id/like` - Liker un post
- `GET /api/posts/:id/comments` - Commentaires d'un post
- `POST /api/posts/:id/comments` - Ajouter un commentaire

## 🎨 Technologies Utilisées

### Backend
- Flask 3.0.0
- SQLite
- Flask-CORS
- Werkzeug (sécurité)

### Frontend
- React 18
- Vite
- React Router
- Axios
- CSS3

## 📦 Build pour Production

### Frontend

```bash
cd /home/user/webapp/aesconnect-frontend
npm run build
```

Le build sera dans `aesconnect-frontend/dist/`

### Backend

```bash
cd /home/user/webapp
gunicorn --bind 0.0.0.0:5000 app:app
```

## 🌍 Déploiement

### Backend sur Render

Voir le fichier `DEPLOIEMENT.md` et `GUIDE_DEPLOIEMENT_RENDER.md`

### Frontend

Le frontend peut être déployé sur :
- Vercel
- Netlify
- Render (Static Site)
- GitHub Pages

**Important** : Mettre à jour `VITE_API_URL` avec l'URL du backend en production.

## ✅ Checklist de Lancement

- [ ] Backend Flask lancé sur le port 5000
- [ ] Frontend React lancé sur le port 5173
- [ ] Page de login accessible
- [ ] Inscription fonctionne
- [ ] Connexion fonctionne
- [ ] Création de posts fonctionne
- [ ] Likes fonctionnent
- [ ] Déconnexion fonctionne

## 🎯 Prochaines Étapes

1. Tester toutes les fonctionnalités
2. Créer quelques comptes de test
3. Publier quelques posts
4. Déployer en production
5. Commencer la campagne publicitaire

---

**Fait avec ❤️ pour l'Alliance des États du Sahel**

🇲🇱 Mali | 🇧🇫 Burkina Faso | 🇳🇪 Niger

## 🆘 Support

En cas de problème, vérifiez :
1. Les logs du backend (terminal où tourne Flask)
2. La console du navigateur (F12 → Console)
3. L'onglet Network du navigateur pour les requêtes API

**Bon lancement ! 🚀**
