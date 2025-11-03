# ⚡ Guide Déploiement Render (Version Express)

## 🎯 Objectif
Déployer AES Connect (Backend + Frontend) sur Render en 30 minutes

---

## 📋 Prérequis
- [ ] Compte Render.com
- [ ] Compte Cloudinary (pour images)
- [ ] PR mergée dans main

---

## 🔴 BACKEND - Web Service (15 min)

### 1️⃣ Créer le Service
1. Render Dashboard → **New +** → **Web Service**
2. Connectez GitHub : `Isco7702/aesconnect`
3. **Branch** : `main`

### 2️⃣ Configuration Build
```
Name: aesconnect-api
Environment: Python 3
Branch: main
Build Command: pip install -r requirements.txt
Start Command: gunicorn --bind 0.0.0.0:$PORT app:app
```

### 3️⃣ Variables d'Environnement

Cliquez sur **"Advanced"** → **"Add Environment Variable"**

```env
SECRET_KEY=<générer_une_clé_64_caractères>
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
ADMIN_PASSWORD=VotreMotDePasse123
FLASK_ENV=production
DATABASE_PATH=/opt/render/project/src/social_network.db
```

#### 🔐 Générer SECRET_KEY
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

#### ☁️ Obtenir les Clés Cloudinary
1. Allez sur [cloudinary.com](https://cloudinary.com)
2. Dashboard → Account Details
3. Copiez : Cloud Name, API Key, API Secret

### 4️⃣ Déployer
1. Cliquez sur **"Create Web Service"**
2. Attendez ~5 minutes
3. **Notez l'URL** : `https://aesconnect-api.onrender.com`

### 5️⃣ Créer un Admin
1. Dans le dashboard Backend → **Shell**
2. Exécutez :
   ```bash
   python3 create_admin.py
   ```

---

## 🔵 FRONTEND - Static Site (15 min)

### 1️⃣ Créer le Site
1. Render Dashboard → **New +** → **Static Site**
2. Même repository : `Isco7702/aesconnect`
3. **Branch** : `main`

### 2️⃣ Configuration Build
```
Name: aesconnect-frontend
Branch: main
Root Directory: aesconnect-frontend
Build Command: npm install && npm run build
Publish Directory: dist
```

### 3️⃣ Variable d'Environnement

**Important** : Cliquez sur **"Advanced"** → **"Add Environment Variable"**

```env
VITE_API_BASE_URL=https://aesconnect-api.onrender.com
```

⚠️ **Remplacez** par l'URL réelle de votre Backend (étape Backend 4)

### 4️⃣ Déployer
1. Cliquez sur **"Create Static Site"**
2. Attendez ~3 minutes
3. **Notez l'URL** : `https://aesconnect-frontend.onrender.com`

---

## ✅ Vérifications

### Test Backend
```bash
curl https://aesconnect-api.onrender.com/health
# Réponse attendue: {"status": "healthy"}
```

### Test Frontend
1. Ouvrez `https://aesconnect-frontend.onrender.com`
2. Cliquez sur "S'inscrire"
3. Créez un compte test
4. Connectez-vous
5. Créez un post
6. Likez le post

---

## 🐛 Problèmes Courants

### ❌ Frontend ne charge pas
**Cause** : `VITE_API_BASE_URL` mal configurée

**Solution** :
1. Frontend → Settings → Environment
2. Vérifiez que l'URL Backend est correcte
3. Redéployez : **Manual Deploy** → **Deploy latest commit**

### ❌ "Network Error" dans le Frontend
**Cause** : Backend pas démarré ou CORS mal configuré

**Solution** :
1. Vérifiez que Backend est "Live" (vert)
2. Testez : `curl https://votre-backend.onrender.com/health`
3. Vérifiez les logs Backend pour erreurs

### ❌ Build Frontend échoue
**Cause** : Problème de dépendances Node.js

**Solution** :
1. Vérifiez les logs de build
2. Problème fréquent : Mauvais `Root Directory`
3. Doit être : `aesconnect-frontend`

### ❌ Backend démarre puis s'arrête
**Cause** : Variables d'environnement manquantes

**Solution** :
1. Backend → Settings → Environment
2. Vérifiez que toutes les variables sont présentes
3. Surtout `SECRET_KEY`, `CLOUDINARY_*`

---

## 📊 Checklist Finale

### Backend ✅
- [ ] Service créé
- [ ] Variables d'environnement configurées
- [ ] Déployé avec succès (statut "Live")
- [ ] `/health` retourne `{"status": "healthy"}`
- [ ] Admin créé

### Frontend ✅
- [ ] Static Site créé
- [ ] `VITE_API_BASE_URL` configurée
- [ ] Déployé avec succès
- [ ] Site accessible dans le navigateur
- [ ] Connexion fonctionne

### Tests ✅
- [ ] Inscription fonctionne
- [ ] Connexion fonctionne
- [ ] Création de post fonctionne
- [ ] Likes fonctionnent
- [ ] Pas d'erreur dans Console navigateur (F12)

---

## 🔄 Mises à Jour Futures

### Mettre à jour le code

1. Modifiez le code localement
2. Commitez et pushez :
   ```bash
   git add .
   git commit -m "feat: Nouvelle fonctionnalité"
   git push origin main
   ```
3. Render redéploiera automatiquement !

---

## 🎯 URLs Finales

Notez vos URLs ici :

```
Backend API  : https://______________________.onrender.com
Frontend App : https://______________________.onrender.com
GitHub PR    : https://github.com/Isco7702/aesconnect/pull/4
```

---

## 📞 Ressources

- **Documentation Render** : https://render.com/docs
- **Support Render** : https://render.com/docs/support
- **Guide Complet** : `GUIDE_REDEPLOIEMENT_ARCHITECTURE_SEPAREE.md`

---

## 🎉 Félicitations !

Si tout fonctionne :
- ✅ Backend API déployé
- ✅ Frontend React déployé
- ✅ Application accessible publiquement
- ✅ Architecture moderne et scalable

**Temps total** : ~30 minutes

---

<div align="center">

**🇲🇱 🇧🇫 🇳🇪**

**AES Connect - Fait avec ❤️ pour l'Alliance des États du Sahel**

</div>
