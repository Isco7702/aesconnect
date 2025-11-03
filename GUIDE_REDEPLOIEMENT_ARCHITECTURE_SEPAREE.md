# 🚀 Guide de Redéploiement - Architecture Backend/Frontend Séparée

## 📋 Vue d'Ensemble

Ce guide vous accompagne dans le redéploiement d'**AES Connect** avec sa nouvelle architecture séparée :
- **Backend** : API REST Flask (Python)
- **Frontend** : Application React + Vite

---

## 🎯 Étape 1 : Préparation et Fusion

### 1.1 Fusionner la Branche `genspark_ai_developer`

La branche `genspark_ai_developer` contient le Frontend React complet et les ajustements nécessaires au Backend.

```bash
# Se positionner sur la branche main
git checkout main

# Récupérer les dernières modifications
git fetch origin main
git fetch origin genspark_ai_developer

# Fusionner la branche genspark_ai_developer
git merge genspark_ai_developer --no-edit

# Résoudre les conflits éventuels (si nécessaire)
# git add <fichiers-résolus>
# git commit -m "Merge: Intégration architecture séparée Backend/Frontend"

# Pousser vers GitHub
git push origin main
```

### 1.2 Vérifier la Structure du Projet

Après la fusion, votre projet doit avoir cette structure :

```
aesconnect/
├── Backend (Racine)
│   ├── app.py                    # API REST Flask
│   ├── requirements.txt          # Dépendances Python
│   ├── create_admin.py
│   ├── render.yaml              # Config déploiement Backend
│   ├── .env.example             # Variables d'environnement exemple
│   ├── static/
│   └── templates/
│
└── Frontend
    └── aesconnect-frontend/
        ├── src/
        │   ├── pages/           # Login, Register, Feed
        │   ├── contexts/        # AuthContext
        │   ├── services/        # API client (Axios)
        │   └── App.jsx
        ├── package.json
        ├── vite.config.js
        └── .env.example         # Variables Frontend
```

---

## 🔧 Étape 2 : Configuration Backend (API Flask)

### 2.1 Variables d'Environnement Backend

Le Backend nécessite plusieurs variables d'environnement critiques. Sur **Render**, configurez-les dans la section "Environment" de votre Web Service.

#### Variables Critiques :

| Variable | Description | Exemple |
|----------|-------------|---------|
| `SECRET_KEY` | Clé secrète Flask | Générer avec `python3 -c "import secrets; print(secrets.token_hex(32))"` |
| `CLOUDINARY_CLOUD_NAME` | Nom du cloud Cloudinary | `my-cloud-name` |
| `CLOUDINARY_API_KEY` | Clé API Cloudinary | `123456789012345` |
| `CLOUDINARY_API_SECRET` | Secret API Cloudinary | `abcdefghijklmnopqrstuvwxyz` |
| `ADMIN_PASSWORD` | Mot de passe admin | Votre mot de passe sécurisé |
| `FLASK_ENV` | Environnement Flask | `production` |
| `DATABASE_PATH` | Chemin de la BD | `/opt/render/project/src/social_network.db` |

### 2.2 Déploiement Backend sur Render

#### Option A : Déploiement Automatique (Recommandé)

1. Connectez-vous à [Render](https://render.com)
2. **New +** → **Web Service**
3. Connectez votre repository : `Isco7702/aesconnect`
4. Configuration :
   - **Name** : `aesconnect-api` (ou votre choix)
   - **Branch** : `main`
   - **Root Directory** : *Laisser vide*
   - **Environment** : `Python 3`
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `gunicorn --bind 0.0.0.0:$PORT app:app`
   - **Plan** : Free (ou selon vos besoins)

5. **Ajoutez les Variables d'Environnement** (section Environment)
6. Cliquez sur **Create Web Service**
7. Attendez le déploiement (3-5 minutes)

#### Option B : Avec render.yaml (Blueprint)

Si vous utilisez `render.yaml` :

1. **New +** → **Blueprint**
2. Sélectionnez le repository `Isco7702/aesconnect`
3. Render détectera automatiquement `render.yaml`
4. Ajoutez les variables d'environnement
5. **Apply**

### 2.3 Obtenir l'URL du Backend

Une fois déployé, Render vous fournira une URL :
```
https://aesconnect-api.onrender.com
```

⚠️ **IMPORTANT** : Notez cette URL, vous en aurez besoin pour le Frontend !

### 2.4 Créer un Compte Administrateur

Depuis le Shell Render ou en local :

```bash
python3 create_admin.py
```

Entrez un nom d'utilisateur et utilisez le mot de passe défini dans `ADMIN_PASSWORD`.

---

## ⚛️ Étape 3 : Configuration Frontend (React + Vite)

### 3.1 Variables d'Environnement Frontend

Le Frontend a besoin de connaître l'URL de votre Backend API.

#### En Local (Développement)

Créez le fichier `aesconnect-frontend/.env` :

```env
VITE_API_BASE_URL=http://localhost:5000
```

#### En Production (Render)

Créez le fichier `aesconnect-frontend/.env.production` :

```env
VITE_API_BASE_URL=https://aesconnect-api.onrender.com
```

⚠️ Remplacez `aesconnect-api.onrender.com` par l'URL réelle de votre Backend déployé (étape 2.3).

### 3.2 Déploiement Frontend sur Render

#### Option 1 : Static Site (Recommandé pour React)

1. Sur Render : **New +** → **Static Site**
2. Connectez le même repository : `Isco7702/aesconnect`
3. Configuration :
   - **Name** : `aesconnect-frontend`
   - **Branch** : `main`
   - **Root Directory** : `aesconnect-frontend`
   - **Build Command** : `npm install && npm run build`
   - **Publish Directory** : `dist`

4. **Variables d'Environnement** :
   ```env
   VITE_API_BASE_URL=https://aesconnect-api.onrender.com
   ```

5. Cliquez sur **Create Static Site**
6. Attendez le build (2-3 minutes)

#### Option 2 : Web Service (Alternative)

Si vous préférez un Web Service :

```bash
Build Command: cd aesconnect-frontend && npm install && npm run build && npm install -g serve
Start Command: cd aesconnect-frontend && serve -s dist -l $PORT
```

### 3.3 Obtenir l'URL du Frontend

Render fournira une URL :
```
https://aesconnect-frontend.onrender.com
```

---

## ✅ Étape 4 : Tests et Vérifications

### 4.1 Tester le Backend

```bash
# Healthcheck
curl https://aesconnect-api.onrender.com/health

# Devrait retourner :
{"status": "healthy"}
```

### 4.2 Tester le Frontend

1. Ouvrez `https://aesconnect-frontend.onrender.com` dans votre navigateur
2. Testez l'inscription d'un nouvel utilisateur
3. Testez la connexion
4. Créez un post test
5. Likez un post

### 4.3 Vérifier les Logs

#### Backend (Render Dashboard)
- Allez dans votre Web Service Backend
- Cliquez sur **Logs**
- Vérifiez qu'il n'y a pas d'erreurs

#### Frontend (Console navigateur)
- Ouvrez les DevTools (F12)
- Vérifiez la console pour d'éventuelles erreurs
- Dans l'onglet Network, vérifiez que les requêtes API fonctionnent

---

## 🔄 Étape 5 : Mises à Jour Futures

### Mettre à Jour le Backend

```bash
# Modifier le code Backend
vim app.py

# Commit et push
git add .
git commit -m "feat: Nouvelle fonctionnalité Backend"
git push origin main
```

Render redéploiera automatiquement le Backend.

### Mettre à Jour le Frontend

```bash
# Modifier le code Frontend
cd aesconnect-frontend
vim src/pages/Feed.jsx

# Commit et push
git add .
git commit -m "feat: Amélioration interface Feed"
git push origin main
```

Render redéploiera automatiquement le Frontend.

---

## 🐛 Dépannage

### Problème : "Network Error" dans le Frontend

**Cause** : Le Frontend ne peut pas joindre le Backend.

**Solutions** :
1. Vérifiez que `VITE_API_BASE_URL` est correctement configurée
2. Vérifiez que le Backend est démarré et accessible
3. Vérifiez les logs du Backend pour des erreurs CORS

### Problème : "CORS Error"

**Cause** : Configuration CORS incorrecte dans le Backend.

**Solution** : Vérifiez que `flask-cors` est installé et configuré :

```python
from flask_cors import CORS
CORS(app, supports_credentials=True)
```

### Problème : Variables d'environnement non prises en compte

**Cause** : Fichier `.env` non chargé ou syntaxe incorrecte.

**Solutions** :
1. En local : Utilisez `python-dotenv`
2. Sur Render : Ajoutez les variables dans la section "Environment"
3. Pour Vite : Les variables doivent commencer par `VITE_`

### Problème : Build Frontend échoue

**Cause** : Dépendances manquantes ou erreurs dans le code.

**Solutions** :
1. Vérifiez les logs de build sur Render
2. Testez le build localement : `npm run build`
3. Vérifiez que `package.json` est correct

---

## 📞 Support et Ressources

- **Documentation Backend** : [Flask Docs](https://flask.palletsprojects.com)
- **Documentation Frontend** : [React Docs](https://react.dev) | [Vite Docs](https://vitejs.dev)
- **Support Render** : [Render Docs](https://render.com/docs)
- **Issues GitHub** : [Ouvrir une issue](https://github.com/Isco7702/aesconnect/issues)

---

## 🎉 Félicitations !

Votre application **AES Connect** est maintenant déployée avec une architecture moderne et séparée !

### Prochaines Étapes

- [ ] Configurer un domaine personnalisé (optionnel)
- [ ] Activer le SSL/HTTPS (automatique sur Render)
- [ ] Configurer des sauvegardes régulières de la base de données
- [ ] Mettre en place un monitoring (Render Metrics)
- [ ] Ajouter des tests automatisés (CI/CD)

---

<div align="center">

**Fait avec ❤️ pour l'Alliance des États du Sahel**

🇲🇱 Mali | 🇧🇫 Burkina Faso | 🇳🇪 Niger

[⬆ Retour en haut](#-guide-de-redéploiement---architecture-backendfrontend-séparée)

</div>
