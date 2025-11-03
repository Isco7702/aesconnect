# 🔄 Migration vers l'Architecture Séparée

## 📢 Changements Importants

Ce projet a été **refactorisé** pour séparer le Backend et le Frontend en deux applications indépendantes.

### Avant (Monolithique)
```
Flask + Templates HTML dans le même projet
```

### Après (Architecture Moderne)
```
Backend (API REST Flask) ← HTTP/JSON → Frontend (React SPA)
```

---

## 🎯 Avantages de la Nouvelle Architecture

### ✅ Pour les Développeurs
- **Séparation des préoccupations** : Backend et Frontend complètement découplés
- **Développement parallèle** : Les équipes peuvent travailler indépendamment
- **Stack moderne** : React + Vite pour une expérience de développement optimale
- **Hot Reload** : Rechargement instantané des modifications (Frontend)

### ✅ Pour le Déploiement
- **Déploiement indépendant** : Mise à jour Backend sans toucher Frontend (et vice-versa)
- **Scalabilité** : Backend et Frontend peuvent être mis à l'échelle séparément
- **Performance** : Frontend servi comme site statique (très rapide)
- **Flexibilité** : Possibilité d'héberger sur des services différents

### ✅ Pour les Utilisateurs
- **Performance améliorée** : SPA React = Navigation ultra-rapide
- **Expérience utilisateur** : Pas de rechargement de page complet
- **Réactivité** : Interface moderne et fluide
- **Progressive Web App ready** : Possibilité de transformer en PWA facilement

---

## 📂 Nouvelle Structure

```
aesconnect/
│
├── Backend (Racine du projet)
│   ├── app.py                    # 🔴 API REST pure (plus de templates HTML)
│   ├── requirements.txt          # Dépendances Python
│   ├── create_admin.py           # Script utilitaire
│   ├── .env.example              # Variables d'environnement Backend
│   └── static/                   # Fichiers statiques (favicon, etc.)
│
└── Frontend (Sous-dossier)
    └── aesconnect-frontend/
        ├── src/
        │   ├── pages/            # Pages React
        │   │   ├── Login.jsx
        │   │   ├── Register.jsx
        │   │   └── Feed.jsx
        │   ├── contexts/         # Gestion d'état (AuthContext)
        │   ├── services/         # Client API (Axios)
        │   └── App.jsx           # Application principale
        ├── package.json          # Dépendances Node.js
        ├── vite.config.js        # Configuration Vite
        └── .env.example          # Variables d'environnement Frontend
```

---

## 🚀 Démarrage Rapide

### Backend (Terminal 1)
```bash
# À la racine du projet
pip install -r requirements.txt
python3 app.py
# Backend disponible sur http://localhost:5000
```

### Frontend (Terminal 2)
```bash
cd aesconnect-frontend
npm install
npm run dev
# Frontend disponible sur http://localhost:5173
```

---

## 🔌 Communication Backend ↔ Frontend

### Comment ça marche ?

1. **Frontend** fait des requêtes HTTP vers le **Backend**
2. **Backend** répond avec des données JSON
3. **Frontend** affiche les données dans l'interface React

### Exemple de Flux

```
Utilisateur clique "Connexion"
    ↓
Frontend envoie POST /login avec username/password
    ↓
Backend vérifie les credentials
    ↓
Backend répond avec token + données utilisateur (JSON)
    ↓
Frontend stocke le token et redirige vers /feed
```

### Configuration de la Communication

Le Frontend doit connaître l'URL du Backend via la variable d'environnement :

```env
# aesconnect-frontend/.env
VITE_API_BASE_URL=http://localhost:5000
```

En production :
```env
# aesconnect-frontend/.env.production
VITE_API_BASE_URL=https://votre-backend-api.onrender.com
```

---

## 🔐 Gestion de l'Authentification

### Session-based (Actuel)

Le Backend utilise des **sessions Flask** avec cookies :

```python
# Backend - Login
session['user_id'] = user.id
```

Le Frontend envoie le cookie de session avec chaque requête :

```javascript
// Frontend - Configuration Axios
axios.defaults.withCredentials = true;
```

### CORS Configuration

Pour que le Frontend puisse communiquer avec le Backend :

```python
# Backend - app.py
from flask_cors import CORS
CORS(app, supports_credentials=True)
```

---

## 📋 Endpoints API Disponibles

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/register` | POST | Inscription utilisateur |
| `/login` | POST | Connexion |
| `/logout` | POST | Déconnexion |
| `/profile` | GET | Profil utilisateur |
| `/posts` | GET | Liste des posts |
| `/posts` | POST | Créer un post |
| `/posts/:id/like` | POST | Liker un post |
| `/posts/:id/comments` | GET | Commentaires d'un post |
| `/posts/:id/comments` | POST | Commenter un post |
| `/health` | GET | Healthcheck |

---

## 🔄 Migration de l'Ancien Code

### Ancien (Templates HTML)
```python
@app.route('/')
def index():
    return render_template('index.html')
```

### Nouveau (API REST)
```python
@app.route('/posts', methods=['GET'])
def get_posts():
    # Récupérer les posts depuis la DB
    return jsonify({'posts': posts})
```

Le Frontend consomme maintenant cette API :

```javascript
// Frontend - services/api.js
export const getPosts = async () => {
  const response = await axios.get('/posts');
  return response.data.posts;
};
```

---

## 🌐 Déploiement

### Ancien (Un seul service)
```
Render Web Service → Flask + Templates HTML
```

### Nouveau (Deux services)
```
Render Web Service → Backend API Flask (Python)
Render Static Site  → Frontend React (Build statique)
```

**Voir le guide complet** : [GUIDE_REDEPLOIEMENT_ARCHITECTURE_SEPAREE.md](GUIDE_REDEPLOIEMENT_ARCHITECTURE_SEPAREE.md)

---

## 🛠️ Fonctionnalités Actuellement Implémentées

### ✅ Backend API
- [x] Authentification (register, login, logout)
- [x] Gestion des posts (CRUD)
- [x] Système de likes
- [x] Système de commentaires
- [x] Profils utilisateurs
- [x] Groupes
- [x] Messages privés
- [x] Recherche d'utilisateurs

### ✅ Frontend React
- [x] Page de connexion
- [x] Page d'inscription
- [x] Fil d'actualité (Feed)
- [x] Création de posts
- [x] Système de likes
- [x] Authentification avec contexte React

### 🚧 À Implémenter dans le Frontend
- [ ] Affichage des commentaires
- [ ] Interface de messagerie
- [ ] Page de profil utilisateur
- [ ] Upload de photo de profil
- [ ] Système de notifications
- [ ] Gestion des groupes
- [ ] Recherche d'utilisateurs

---

## 📚 Ressources et Documentation

- **README Principal** : [README.md](README.md)
- **Guide Déploiement** : [GUIDE_REDEPLOIEMENT_ARCHITECTURE_SEPAREE.md](GUIDE_REDEPLOIEMENT_ARCHITECTURE_SEPAREE.md)
- **Frontend README** : [aesconnect-frontend/README.md](aesconnect-frontend/README.md)

---

## 💡 Conseils pour les Développeurs

### Backend Development
```bash
# Activer le mode debug
export FLASK_ENV=development
python3 app.py
```

### Frontend Development
```bash
cd aesconnect-frontend
npm run dev
# Vite avec Hot Module Replacement
```

### Tester l'API avec curl
```bash
# Register
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"test123","full_name":"Test User"}'

# Login
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}' \
  -c cookies.txt

# Get posts (avec cookie de session)
curl http://localhost:5000/posts -b cookies.txt
```

---

## 🎉 Conclusion

Cette migration vers une architecture séparée prépare **AES Connect** pour :
- Une meilleure maintenabilité
- Une scalabilité future
- Une expérience utilisateur moderne
- Des déploiements plus flexibles

Bon développement ! 🚀

---

<div align="center">

**Fait avec ❤️ pour l'Alliance des États du Sahel**

🇲🇱 Mali | 🇧🇫 Burkina Faso | 🇳🇪 Niger

</div>
