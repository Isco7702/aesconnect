# 🚀 Guide de Déploiement - AES CONNECT

Ce guide vous accompagne étape par étape pour déployer AES Connect en production.

## 📋 Table des Matières
1. [Déploiement sur Render](#déploiement-sur-render)
2. [Déploiement sur Heroku](#déploiement-sur-heroku)
3. [Déploiement sur VPS](#déploiement-sur-vps)
4. [Configuration Post-Déploiement](#configuration-post-déploiement)

---

## 🎯 Déploiement sur Render (Recommandé)

### Pourquoi Render ?
- ✅ **Gratuit** pour commencer (plan Free)
- ✅ **Déploiement automatique** depuis GitHub
- ✅ **SSL/HTTPS** automatique
- ✅ **Configuration simple** avec `render.yaml`

### Étapes de Déploiement

#### 1. Préparation du Repository

Assurez-vous que votre code est poussé sur GitHub :

```bash
cd /home/user/webapp
git add .
git commit -m "chore: Préparer pour déploiement production"
git push origin main
```

#### 2. Créer un Compte Render

1. Allez sur [render.com](https://render.com)
2. Inscrivez-vous avec votre compte GitHub
3. Autorisez Render à accéder à vos repositories

#### 3. Déploiement Automatique

**Option A : Déploiement via Blueprint (Automatique)**

1. Cliquez sur **"New +"** → **"Blueprint"**
2. Sélectionnez votre repository : `Isco7702/aesconnect`
3. Render détectera automatiquement `render.yaml`
4. Cliquez sur **"Apply"**
5. Le déploiement commence automatiquement ! ⏳

**Option B : Déploiement Manuel**

1. Cliquez sur **"New +"** → **"Web Service"**
2. Connectez votre repository GitHub : `Isco7702/aesconnect`
3. Configurez les paramètres :
   - **Name** : `aesconnect`
   - **Environment** : `Python 3`
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `gunicorn --bind 0.0.0.0:$PORT app:app`
   - **Plan** : `Free`
4. Cliquez sur **"Create Web Service"**

#### 4. Attendre le Déploiement

- ⏱️ **Durée** : 3-5 minutes
- 📊 **Suivi** : Vous pouvez voir les logs en temps réel
- ✅ **Succès** : Quand vous voyez "Build succeeded" et "Service live"

#### 5. Obtenir l'URL Publique

Une fois déployé, Render vous fournira une URL :
```
https://aesconnect.onrender.com
```

---

## 🔧 Configuration Post-Déploiement

### 1. Variables d'Environnement (Optionnelles)

Dans le dashboard Render, allez dans **"Environment"** et ajoutez :

```env
FLASK_ENV=production
SECRET_KEY=votre_clé_secrète_unique_très_longue
DATABASE_PATH=/opt/render/project/src/social_network.db
```

**Générer une clé secrète** :
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 2. Configuration du Domaine Personnalisé

Si vous avez un domaine (ex: aesconnect.com) :

1. Allez dans **"Settings"** → **"Custom Domain"**
2. Ajoutez votre domaine : `www.aesconnect.com`
3. Configurez vos DNS selon les instructions Render
4. Render générera automatiquement un certificat SSL

### 3. Créer un Compte Administrateur

Connectez-vous via SSH (Render Shell) :

1. Dans le dashboard, cliquez sur **"Shell"**
2. Exécutez :
```bash
python3 create_admin.py
```

---

## 🌍 Déploiement sur Heroku

### Prérequis
- Compte Heroku
- Heroku CLI installé

### Étapes

```bash
# 1. Installer Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# 2. Se connecter
heroku login

# 3. Créer l'application
heroku create aesconnect

# 4. Créer un Procfile
echo "web: gunicorn app:app" > Procfile

# 5. Déployer
git add Procfile
git commit -m "Add Procfile for Heroku"
git push heroku main

# 6. Ouvrir l'application
heroku open
```

---

## 🖥️ Déploiement sur VPS (Ubuntu/Debian)

### Prérequis
- Serveur VPS (Ubuntu 20.04+)
- Accès root ou sudo
- Domaine pointant vers votre serveur

### Installation Complète

```bash
# 1. Connexion au serveur
ssh user@votre-serveur.com

# 2. Mise à jour du système
sudo apt update && sudo apt upgrade -y

# 3. Installation de Python et dépendances
sudo apt install python3 python3-pip python3-venv nginx -y

# 4. Cloner le projet
cd /var/www
sudo git clone https://github.com/Isco7702/aesconnect.git
cd aesconnect

# 5. Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate

# 6. Installer les dépendances
pip install -r requirements.txt

# 7. Configuration Gunicorn (systemd)
sudo nano /etc/systemd/system/aesconnect.service
```

Contenu de `aesconnect.service` :

```ini
[Unit]
Description=AES Connect Web Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/aesconnect
Environment="PATH=/var/www/aesconnect/venv/bin"
ExecStart=/var/www/aesconnect/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:5000 app:app

[Install]
WantedBy=multi-user.target
```

```bash
# 8. Activer et démarrer le service
sudo systemctl daemon-reload
sudo systemctl start aesconnect
sudo systemctl enable aesconnect

# 9. Configuration Nginx
sudo nano /etc/nginx/sites-available/aesconnect
```

Contenu de la config Nginx :

```nginx
server {
    listen 80;
    server_name votre-domaine.com www.votre-domaine.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /var/www/aesconnect/static;
    }
}
```

```bash
# 10. Activer la configuration
sudo ln -s /etc/nginx/sites-available/aesconnect /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 11. Installer SSL avec Let's Encrypt
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d votre-domaine.com -d www.votre-domaine.com
```

---

## ✅ Vérification du Déploiement

### Tests de Base

1. **Accès à l'application**
   ```bash
   curl -I https://votre-url.com
   # Devrait retourner 200 OK
   ```

2. **Test d'inscription**
   - Créez un compte test
   - Vérifiez la connexion

3. **Test des fonctionnalités**
   - ✅ Créer un post
   - ✅ Liker un post
   - ✅ Commenter
   - ✅ Envoyer un message

### Monitoring

**Sur Render** : Dashboard intégré avec logs en temps réel

**Sur VPS** :
```bash
# Voir les logs
sudo journalctl -u aesconnect -f

# Statut du service
sudo systemctl status aesconnect

# Redémarrer
sudo systemctl restart aesconnect
```

---

## 🔄 Mise à Jour du Code

### Sur Render
Simplement poussez sur GitHub :
```bash
git add .
git commit -m "feat: Nouvelle fonctionnalité"
git push origin main
```
Render détecte automatiquement et redéploie !

### Sur VPS
```bash
cd /var/www/aesconnect
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart aesconnect
```

---

## 🐛 Dépannage

### Problème : "Application Error"
**Solution** : Vérifiez les logs
```bash
# Sur Render : Voir les logs dans le dashboard
# Sur VPS :
sudo journalctl -u aesconnect -n 50
```

### Problème : Base de données non initialisée
**Solution** :
```bash
python3 -c "from app import init_db; init_db()"
```

### Problème : Port déjà utilisé
**Solution** :
```bash
# Trouver le processus
sudo lsof -i :5000
# Tuer le processus
sudo kill -9 <PID>
```

---

## 📞 Support

Si vous rencontrez des problèmes :
1. Consultez les logs d'erreur
2. Vérifiez la documentation officielle de votre plateforme
3. Ouvrez une issue sur GitHub

---

## 🎉 Félicitations !

Votre application **AES Connect** est maintenant en production et accessible au monde entier ! 🌍

**Prochaines étapes** :
- 📱 Créer des comptes de démonstration
- 📸 Préparer du contenu initial
- 📢 Lancer la campagne marketing
- 📊 Monitorer les performances

---

<div align="center">

**Bon lancement ! 🚀**

[⬆ Retour en haut](#-guide-de-déploiement---aes-connect)

</div>
