# Configuration Frontend et API

## 🎉 Changements effectués

L'application a été configurée pour servir correctement :
- **L'interface utilisateur** sur la route principale `/`
- **L'API** sur le préfixe `/api`

## 📋 Structure des routes

### Routes Frontend (Interface Utilisateur)
Ces routes sont accessibles par le navigateur et servent l'interface HTML :

- **`/`** - Page d'accueil (interface utilisateur complète)
  - Affiche le frontend React/HTML avec tous les boutons, couleurs et drapeaux
  - Formulaires de connexion et d'inscription
  - Feed de posts, groupes, messages

### Routes API pour le Frontend
Ces routes sont utilisées par JavaScript dans le navigateur pour interagir avec le serveur :

#### Authentification
- **`POST /login`** - Connexion utilisateur
- **`POST /register`** - Inscription utilisateur
- **`POST /logout`** - Déconnexion
- **`GET /profile`** - Profil de l'utilisateur connecté

#### Posts
- **`GET /posts`** - Liste de tous les posts
- **`POST /posts`** - Créer un nouveau post
- **`POST /posts/<id>/like`** - Liker/Unliker un post

#### Groupes
- **`GET /groups`** - Liste de tous les groupes
- **`POST /groups`** - Créer un nouveau groupe

#### Messages
- **`GET /messages`** - Liste de tous les messages
- **`POST /messages`** - Envoyer un message

#### Recherche
- **`GET /users/search?q=...`** - Rechercher des utilisateurs

### Routes API (pour clients externes)
Ces routes sont préfixées par `/api` et utilisent Flask-Smorest :

- **`GET /api`** - Information sur l'API
- **`/api/auth/*`** - Endpoints d'authentification
- **`/api/posts/*`** - Endpoints de posts
- **`/api/groups/*`** - Endpoints de groupes
- **`/api/messages/*`** - Endpoints de messages
- **`/api/notifications/*`** - Endpoints de notifications

## 🔧 Fichiers modifiés

### `app.py`
- Ajout de `render_template` pour servir `templates/index.html`
- Route `/` modifiée pour afficher le frontend
- Route `/api` ajoutée pour l'information API

### `frontend_routes.py` (nouveau)
- Contient toutes les routes de compatibilité pour le frontend
- Permet au JavaScript du frontend d'appeler directement `/login`, `/posts`, etc.
- Utilise les mêmes modèles de base de données que les blueprints API

### `render.yaml`
- Configuration corrigée pour pointer vers `app:app` à la racine
- `buildCommand` simplifié
- `healthCheckPath` changé pour `/api`

## 🚀 Déploiement

### Sur Render.com
Une fois les modifications poussées sur GitHub, Render va automatiquement :
1. Détecter le nouveau commit
2. Reconstruire l'application
3. Redémarrer le service
4. L'interface sera accessible sur `https://aesconnect-1.onrender.com`

### Test local
```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer le serveur
python app.py

# Accéder à l'interface
# Ouvrir http://localhost:5000 dans le navigateur
```

## 🎨 Interface utilisateur

L'interface affiche maintenant :
- ✅ Header bleu avec le logo "AESConnect"
- ✅ Boutons de connexion et d'inscription
- ✅ Sidebar avec navigation (Accueil, Profil, Messages, Groupes, Amis)
- ✅ Zone de création de posts
- ✅ Feed de posts avec likes et commentaires
- ✅ Panneau latéral avec amis en ligne et groupes suggérés
- ✅ Formulaires de connexion/inscription avec design moderne
- ✅ Notifications en temps réel
- ✅ Design responsive pour mobile et desktop

## 🔐 Fonctionnalités disponibles

### Sans authentification
- Voir la page d'accueil
- Accéder aux formulaires de connexion/inscription

### Avec authentification
- Créer des posts
- Liker/Commenter des posts
- Créer et rejoindre des groupes
- Envoyer et recevoir des messages
- Rechercher d'autres utilisateurs
- Voir les notifications

## 📱 Accès

### Production (Render)
**URL principale :** https://aesconnect-1.onrender.com

- `/` → Interface utilisateur complète
- `/api` → Information sur l'API

### Local (développement)
**URL locale :** http://localhost:5000

- `/` → Interface utilisateur
- `/api` → Information sur l'API

## ✅ Résumé

Les modifications permettent maintenant :
1. ✅ Afficher l'interface utilisateur sur la racine `/`
2. ✅ Accès aux routes d'authentification (`/login`, `/register`)
3. ✅ Création et affichage de posts
4. ✅ Création et affichage de groupes
5. ✅ Envoi et réception de messages
6. ✅ API REST disponible sous `/api/*` pour clients externes
7. ✅ Design moderne avec couleurs et drapeaux d'Afrique de l'Est
