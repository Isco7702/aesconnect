# 🌍 AES CONNECT - Réseau Social de l'Alliance des États du Sahel

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com)
[![React](https://img.shields.io/badge/React-19.1+-61DAFB.svg)](https://reactjs.org)
[![Vite](https://img.shields.io/badge/Vite-7.1+-646CFF.svg)](https://vitejs.dev)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)]()

**AES Connect** est une plateforme de réseau social moderne dédiée à l'Alliance des États du Sahel (Mali, Burkina Faso, Niger). Elle permet aux citoyens de se connecter, partager, échanger et construire une communauté sahélienne forte et unie.

## 🏗️ Architecture

Ce projet utilise une **architecture moderne séparée** :
- **Backend** : API REST Flask (port 5000)
- **Frontend** : Application React + Vite (port 5173)

## ✨ Fonctionnalités Principales

### 👤 Gestion des Utilisateurs
- ✅ Inscription et connexion sécurisées
- ✅ Profils utilisateur personnalisables (avatar, bio, nom complet)
- ✅ Système de follow/following
- ✅ Gestion des sessions sécurisées

### 📱 Réseau Social
- ✅ Publications de posts avec support d'images
- ✅ Système de likes et de commentaires
- ✅ Fil d'actualité personnalisé
- ✅ Messagerie privée entre utilisateurs
- ✅ Notifications en temps réel

### 👥 Communauté
- ✅ Création et gestion de groupes
- ✅ Espaces de discussion thématiques
- ✅ Partage de contenus multimédias

### 🎨 Interface Utilisateur
- ✅ Design responsive (mobile, tablette, desktop)
- ✅ Interface moderne et intuitive
- ✅ Thème aux couleurs de l'Alliance des États du Sahel
- ✅ Navigation fluide (Single Page Application)

## 🚀 Installation & Démarrage Rapide

### Prérequis
- **Python 3.8+** (pour le Backend)
- **Node.js 16+** (pour le Frontend)
- **pip** et **npm** (gestionnaires de paquets)

### Installation Locale

#### 1️⃣ Backend (API Flask)

```bash
# Cloner le repository
git clone https://github.com/Isco7702/aesconnect.git
cd aesconnect

# Installer les dépendances Backend
pip install -r requirements.txt

# Configurer les variables d'environnement (optionnel pour développement)
cp .env.example .env
# Éditez .env avec vos clés Cloudinary si nécessaire

# Lancer le Backend
python3 app.py
```

Le Backend API sera accessible à : **http://localhost:5000**

#### 2️⃣ Frontend (React + Vite)

```bash
# Dans un nouveau terminal
cd aesconnect-frontend

# Installer les dépendances
npm install

# Configurer l'URL de l'API
cp .env.example .env
# Le fichier .env pointe déjà vers http://localhost:5000

# Lancer le Frontend
npm run dev
```

Le Frontend sera accessible à : **http://localhost:5173**

### Mode Production

#### Backend (avec Gunicorn)
```bash
gunicorn --bind 0.0.0.0:5000 app:app
```

#### Frontend (Build)
```bash
cd aesconnect-frontend
npm run build
# Les fichiers de production seront dans le dossier dist/
```

## 🌐 Déploiement sur Render

### Architecture de Déploiement

Le projet nécessite **DEUX services séparés** sur Render :

#### 1️⃣ Backend API (Web Service Python)

**Configuration Backend :**
- **Build Command** : `pip install -r requirements.txt`
- **Start Command** : `gunicorn --bind 0.0.0.0:$PORT app:app`
- **Environment** : Python 3

**Variables d'Environnement Critiques :**
```env
SECRET_KEY=votre_clé_secrète_unique_64_caractères
CLOUDINARY_CLOUD_NAME=votre_cloud_name
CLOUDINARY_API_KEY=votre_api_key
CLOUDINARY_API_SECRET=votre_api_secret
ADMIN_PASSWORD=votre_mot_de_passe_admin
FLASK_ENV=production
DATABASE_PATH=/opt/render/project/src/social_network.db
```

**Générer une clé secrète** :
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

L'URL de votre API sera : `https://aesconnect-api.onrender.com` (exemple)

#### 2️⃣ Frontend React (Static Site ou Web Service)

**Configuration Frontend :**
- **Build Command** : `cd aesconnect-frontend && npm install && npm run build`
- **Publish Directory** : `aesconnect-frontend/dist`

**Variables d'Environnement Frontend :**
```env
VITE_API_BASE_URL=https://votre-api-render-url.onrender.com
```

⚠️ **Important** : Remplacez `votre-api-render-url.onrender.com` par l'URL réelle de votre Backend API déployé.

### Déploiement Automatique (Recommandé)

1. **Connectez-vous** à [render.com](https://render.com)
2. **Créez le Backend** :
   - New + → Web Service
   - Connectez `Isco7702/aesconnect`
   - Configurez comme décrit ci-dessus
3. **Créez le Frontend** :
   - New + → Static Site
   - Même repository : `Isco7702/aesconnect`
   - Configurez avec les paramètres Frontend

📖 Voir le guide détaillé : [GUIDE_DEPLOIEMENT_RENDER.md](GUIDE_DEPLOIEMENT_RENDER.md)

## 📁 Structure du Projet

```
aesconnect/
├── Backend (API Flask)
│   ├── app.py                     # API REST Flask principale
│   ├── requirements.txt           # Dépendances Python
│   ├── render.yaml               # Configuration déploiement Backend
│   ├── create_admin.py           # Script de création d'admin
│   ├── .env.example              # Variables d'environnement (exemple)
│   └── static/                   # Fichiers statiques (favicon, etc.)
│
├── Frontend (React + Vite)
│   └── aesconnect-frontend/
│       ├── src/
│       │   ├── pages/            # Pages React (Login, Register, Feed)
│       │   ├── contexts/         # Contexte d'authentification
│       │   ├── services/         # Services API (Axios)
│       │   └── App.jsx           # Composant principal avec routes
│       ├── package.json          # Dépendances Frontend
│       ├── vite.config.js        # Configuration Vite
│       └── .env.example          # Variables d'environnement Frontend
│
├── Documentation
│   ├── README.md                 # Ce fichier
│   ├── GUIDE_DEPLOIEMENT_RENDER.md
│   └── GUIDE_LANCEMENT_COMPLET.md
```

## 🛠️ Technologies Utilisées

### Backend (API REST)
- **Flask 3.0.0** - Framework web Python pour API REST
- **Flask-CORS** - Gestion des requêtes cross-origin
- **SQLite** - Base de données relationnelle
- **Werkzeug** - Sécurité et hachage des mots de passe
- **Gunicorn** - Serveur WSGI pour production

### Frontend (SPA React)
- **React 19.1** - Bibliothèque d'interface utilisateur
- **Vite 7.1** - Build tool ultra-rapide
- **React Router** - Gestion des routes côté client
- **Axios** - Client HTTP pour requêtes API
- **CSS3 moderne** - Styles responsive

## 🔐 Sécurité

- ✅ Hachage sécurisé des mots de passe (Werkzeug)
- ✅ Protection CORS configurée
- ✅ Sessions sécurisées avec clés secrètes
- ✅ Validation des données côté serveur
- ✅ Gestion d'erreurs robuste

## 📊 Base de Données

L'application utilise SQLite avec les tables suivantes :
- **users** - Informations utilisateurs
- **posts** - Publications
- **comments** - Commentaires sur les posts
- **likes** - Likes des posts
- **follows** - Relations de suivi
- **messages** - Messages privés
- **groups** - Groupes/communautés
- **notifications** - Système de notifications

## 🎯 Utilisation

### Créer un Compte Administrateur

```bash
python3 create_admin.py
```

### Première Connexion

1. Accédez à l'application dans votre navigateur
2. Cliquez sur "S'inscrire"
3. Remplissez le formulaire d'inscription
4. Connectez-vous avec vos identifiants

### Fonctionnalités Disponibles

- **Créer des posts** : Partagez vos pensées avec ou sans images
- **Interagir** : Likez et commentez les posts
- **Suivre** : Connectez-vous avec d'autres utilisateurs
- **Messagerie** : Envoyez des messages privés
- **Groupes** : Rejoignez ou créez des communautés

## 📱 Captures d'Écran

*(Les captures d'écran peuvent être ajoutées dans un dossier `screenshots/`)*

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Forkez le projet
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Poussez vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 🐛 Signaler un Bug

Si vous trouvez un bug, veuillez ouvrir une [issue](https://github.com/Isco7702/aesconnect/issues) avec :
- Une description claire du problème
- Les étapes pour reproduire
- Le comportement attendu vs actuel
- Des captures d'écran si pertinent

## 📝 Roadmap

### Version 1.1 (À venir)
- [ ] Système de stories (24h)
- [ ] Appels vidéo intégrés
- [ ] Mode sombre
- [ ] Application mobile (React Native)

### Version 1.2
- [ ] Marketplace intégré
- [ ] Événements communautaires
- [ ] Streaming en direct
- [ ] Traduction multilingue

## 📜 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 👨‍💻 Auteur

**Isco7702** - [GitHub](https://github.com/Isco7702)

## 🌟 Remerciements

- La communauté Flask pour l'excellent framework
- Tous les contributeurs qui ont participé au projet
- L'Alliance des États du Sahel pour l'inspiration

## 📞 Support & Contact

- **Email** : support@aesconnect.com *(à configurer)*
- **Twitter** : @aesconnect *(à configurer)*
- **Facebook** : /aesconnect *(à configurer)*

---

<div align="center">

**Fait avec ❤️ pour l'Alliance des États du Sahel**

🇲🇱 Mali | 🇧🇫 Burkina Faso | 🇳🇪 Niger

[⬆ Retour en haut](#-aes-connect---réseau-social-de-lalliance-des-états-du-sahel)

</div>
