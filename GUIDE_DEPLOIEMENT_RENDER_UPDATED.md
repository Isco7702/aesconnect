# 🚀 Guide de Déploiement Render - AES Connect

## ✅ Problème Résolu

Le frontend ne s'affichait pas car le dossier `dist` n'existait pas. Cette mise à jour résout complètement le problème.

## 📋 Prérequis

- Compte GitHub avec le repository `Isco7702/aesconnect`
- Compte Render.com (gratuit)
- Le code doit être mergé depuis le PR #3

## 🔧 Configuration Automatique

Le fichier `render.yaml` est déjà configuré pour :

1. **Build le frontend** : `cd aesconnect-frontend && npm install && npm run build`
2. **Installer les dépendances backend** : `cd ../aesconnect && pip install -r requirements.txt`
3. **Démarrer l'application** : `gunicorn --bind 0.0.0.0:$PORT aesconnect.app:app`

## 🌐 Étapes de Déploiement

### Option 1 : Déploiement Automatique (Recommandé)

1. **Connectez-vous à Render** : https://render.com
2. **Nouveau Web Service** : Cliquez sur "New +" → "Web Service"
3. **Connectez GitHub** : Sélectionnez `Isco7702/aesconnect`
4. **Détection Automatique** : Render détecte `render.yaml` automatiquement
5. **Déploiement** : Cliquez sur "Apply" - Le déploiement démarre (~5-10 minutes)

### Option 2 : Déploiement Manuel

Si vous préférez configurer manuellement :

**Paramètres de base :**
- **Name** : `aesconnect`
- **Environment** : `Python 3`
- **Build Command** :
  ```bash
  cd aesconnect-frontend && npm install && npm run build && cd ../aesconnect && pip install -r requirements.txt
  ```
- **Start Command** :
  ```bash
  gunicorn --bind 0.0.0.0:$PORT aesconnect.app:app
  ```

**Variables d'environnement :**
- `FLASK_ENV` = `production`
- `FLASK_APP` = `aesconnect/app.py`
- `DATABASE_PATH` = `/opt/render/project/src/social_network.db`

**Configuration du disque :**
- **Name** : `aesconnect-disk`
- **Size** : `1GB`
- **Mount Path** : `/opt/render/project/src`

**Health Check :**
- **Path** : `/utils/health`

## 🎯 Variables d'Environnement Optionnelles

Pour Cloudinary (upload d'images) :
```
CLOUDINARY_CLOUD_NAME=votre_cloud_name
CLOUDINARY_API_KEY=votre_api_key
CLOUDINARY_API_SECRET=votre_api_secret
```

Pour sécurité renforcée :
```
SECRET_KEY=générer_une_clé_secrète_forte_ici
```

## ✅ Vérification du Déploiement

1. **Attendez la fin du build** (~5-10 minutes)
2. **Testez l'URL fournie** : `https://aesconnect-xxxx.onrender.com`
3. **Vérifiez le health check** : `https://aesconnect-xxxx.onrender.com/utils/health`
   - Devrait retourner : `{"message":"Statut de l'API"}`
4. **Testez le frontend** : Visitez la racine de l'URL
   - Le frontend React devrait s'afficher

## 🐛 Dépannage

### Problème : Build échoue
**Solution** : Vérifiez les logs de build sur Render
- Erreur npm : Vérifiez `package.json` et `package-lock.json`
- Erreur pip : Vérifiez `requirements.txt`

### Problème : Frontend ne s'affiche pas
**Solution** : 
1. Vérifiez que le dossier `dist` existe dans `aesconnect/`
2. Vérifiez les logs : "No such file or directory: 'dist'"
3. Re-déclenchez le build sur Render

### Problème : Erreur 404 sur les routes API
**Solution** : 
- Les routes API sont correctement configurées sous :
  - `/auth/*`
  - `/posts/*`
  - `/groups/*`
  - `/messages/*`
  - `/utils/*`
  - `/notifications/*`

## 📊 Structure de Déploiement

```
Render Build Process:
├── 1. Clone Repository
├── 2. Build Frontend (npm install + npm run build)
│   └── Génère: aesconnect/dist/
├── 3. Install Backend Dependencies (pip install)
└── 4. Start Gunicorn Server
    └── Sert: Frontend (/) + API Routes (/auth, /posts, etc.)
```

## 🔄 Redéploiement

Pour redéployer après des changements :

1. **Push vers GitHub** : `git push origin main`
2. **Render redéploie automatiquement** si l'auto-deploy est activé
3. **Ou manuellement** : Cliquez sur "Manual Deploy" → "Deploy latest commit"

## 🎉 Succès !

Une fois déployé, votre application est accessible publiquement :
- **Frontend** : Interface React complète
- **Backend API** : Tous les endpoints fonctionnels
- **Base de données** : SQLite persistante avec le disque Render

---

## 📞 Support

Si vous rencontrez des problèmes :
1. Vérifiez les logs sur Render
2. Consultez le PR #3 : https://github.com/Isco7702/aesconnect/pull/3
3. Testez localement d'abord avec :
   ```bash
   cd aesconnect-frontend && npm run build
   cd ..
   gunicorn --bind 0.0.0.0:5000 aesconnect.app:app
   ```

**Bon déploiement ! 🚀**
