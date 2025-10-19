# 🚀 Guide de Déploiement AESConnect sur Render

## ✅ Prérequis (Déjà fait !)

- ✅ Code source prêt et testé
- ✅ Repository GitHub configuré : `https://github.com/Isco7702/aesconnect`
- ✅ Fichier `render.yaml` configuré
- ✅ Dépendances listées dans `requirements.txt`

---

## 📋 Étapes de Déploiement (5 minutes)

### Étape 1 : Créer un compte Render

1. 🌐 Allez sur **[render.com](https://render.com)**
2. 🔐 Cliquez sur **"Get Started for Free"**
3. 🔑 Connectez-vous avec votre compte **GitHub**
4. ✅ Autorisez Render à accéder à vos repositories GitHub

---

### Étape 2 : Créer un nouveau Web Service

#### Option A : Déploiement Automatique (RECOMMANDÉ) 🌟

1. Dans le dashboard Render, cliquez sur **"New +"** (en haut à droite)
2. Sélectionnez **"Blueprint"**
3. Sélectionnez le repository **"aesconnect"**
4. Render détectera automatiquement le fichier `render.yaml`
5. Cliquez sur **"Apply"**
6. ✨ Le déploiement démarre automatiquement !

#### Option B : Déploiement Manuel

1. Dans le dashboard Render, cliquez sur **"New +"**
2. Sélectionnez **"Web Service"**
3. Connectez votre repository : **"Isco7702/aesconnect"**
4. Configurez les paramètres :

| Paramètre | Valeur |
|-----------|--------|
| **Name** | `aesconnect` |
| **Environment** | `Python 3` |
| **Branch** | `main` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn --bind 0.0.0.0:$PORT app:app` |
| **Plan** | `Free` |

5. Cliquez sur **"Create Web Service"**

---

### Étape 3 : Configuration du Disque Persistant

Pour que la base de données soit sauvegardée :

1. Dans votre service, allez dans **"Disks"** (menu de gauche)
2. Cliquez sur **"Add Disk"**
3. Configurez :
   - **Name** : `aesconnect-disk`
   - **Mount Path** : `/opt/render/project/src`
   - **Size** : `1 GB` (gratuit)
4. Cliquez sur **"Save"**

---

### Étape 4 : Variables d'Environnement (Optionnel mais recommandé)

1. Allez dans **"Environment"** (menu de gauche)
2. Ajoutez ces variables :

| Clé | Valeur |
|-----|--------|
| `FLASK_ENV` | `production` |
| `FLASK_APP` | `app.py` |
| `DATABASE_PATH` | `/opt/render/project/src/social_network.db` |
| `SECRET_KEY` | *(Générer une clé secrète)* |

**Pour générer une clé secrète** :
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

3. Cliquez sur **"Save Changes"**

---

### Étape 5 : Attendre le Déploiement

⏱️ **Durée** : 3-5 minutes

Vous verrez dans les logs :
```
==> Downloading dependencies...
==> Installing packages from requirements.txt
==> Build succeeded 🎉
==> Starting service...
==> Your service is live 🚀
```

---

### Étape 6 : Obtenir votre URL publique

Une fois le déploiement terminé, Render vous fournira une URL comme :

```
https://aesconnect.onrender.com
```

🎉 **Votre application est maintenant en ligne !**

---

## 🔧 Configuration Post-Déploiement

### Créer un Compte Administrateur

1. Dans le dashboard Render, cliquez sur **"Shell"** (menu de gauche)
2. Exécutez :
```bash
python3 create_admin.py
```

### Tester l'Application

Allez sur votre URL et testez :
- ✅ Inscription d'un nouveau compte
- ✅ Connexion
- ✅ Création d'un post
- ✅ Like et commentaire
- ✅ Messagerie

---

## 🌐 Domaine Personnalisé (Optionnel)

Si vous avez un domaine (ex: `aesconnect.com`) :

1. Dans Render, allez dans **"Settings"** → **"Custom Domain"**
2. Ajoutez votre domaine : `www.aesconnect.com`
3. Configurez vos DNS selon les instructions Render :
   - Type : `CNAME`
   - Name : `www`
   - Value : `aesconnect.onrender.com`
4. Render générera automatiquement un **certificat SSL** (HTTPS)

---

## 📊 Monitoring et Logs

### Voir les Logs en Temps Réel

1. Allez dans votre service sur Render
2. Cliquez sur **"Logs"** (menu de gauche)
3. Vous verrez tous les événements en direct

### Métriques de Performance

- **"Metrics"** : CPU, Mémoire, Requêtes
- **"Events"** : Historique des déploiements

---

## 🔄 Mise à Jour de l'Application

### Déploiement Automatique

Render redéploie automatiquement à chaque push sur GitHub !

```bash
# 1. Faire vos modifications
git add .
git commit -m "feat: Nouvelle fonctionnalité"

# 2. Pousser sur GitHub
git push origin main

# 3. Render redéploie automatiquement ! 🚀
```

### Déploiement Manuel

Dans le dashboard Render :
1. Cliquez sur **"Manual Deploy"**
2. Sélectionnez **"Deploy latest commit"**
3. Cliquez sur **"Deploy"**

---

## 🆓 Plan Gratuit Render

### Ce qui est inclus (GRATUIT) :

✅ **750 heures/mois** (suffisant pour un projet personnel)  
✅ **512 MB RAM**  
✅ **0.1 CPU**  
✅ **SSL/HTTPS automatique**  
✅ **Déploiement automatique depuis GitHub**  
✅ **1 GB de stockage disque**  
✅ **Domaine personnalisé**

### ⚠️ Limitations :

- L'application **s'endort après 15 minutes d'inactivité**
- **Première requête** après sommeil : 30-60 secondes (rechargement)
- Solution : Plan payant ($7/mois) pour service toujours actif

---

## 🐛 Dépannage

### Problème : "Application Error"

**Solution** : Vérifiez les logs
- Allez dans **"Logs"** sur Render
- Cherchez les erreurs en rouge

### Problème : Base de données vide après redémarrage

**Solution** : Vérifiez le disque persistant
- Le disque doit être monté sur `/opt/render/project/src`
- Vérifiez dans **"Disks"**

### Problème : Build échoue

**Solution** : Vérifiez `requirements.txt`
- Les versions des packages doivent être compatibles
- Essayez de mettre à jour les versions

---

## 📞 Support

### Documentation Officielle
- 📚 [Documentation Render](https://render.com/docs)
- 💬 [Community Forum](https://community.render.com)

### Support Projet AESConnect
- 📧 GitHub Issues : `https://github.com/Isco7702/aesconnect/issues`
- 📖 Documentation : Voir autres fichiers `.md`

---

## ✅ Checklist de Déploiement

Cochez au fur et à mesure :

- [ ] Compte Render créé
- [ ] Repository GitHub connecté
- [ ] Service web créé
- [ ] Disque persistant configuré (1GB)
- [ ] Variables d'environnement ajoutées
- [ ] Déploiement réussi (Build succeeded)
- [ ] URL publique obtenue
- [ ] Application testée et fonctionnelle
- [ ] Compte admin créé (via Shell)
- [ ] Premier post de test créé

---

## 🎯 Prochaines Étapes

Après le déploiement :

1. **Semaine 1** : Créer des comptes de démonstration
2. **Semaine 2** : Publier du contenu initial
3. **Semaine 3** : Lancer la campagne marketing
4. **Semaine 4** : Analyser les statistiques

---

## 🌟 Conseils Pro

### Optimisation
- Ajoutez un **favicon** à votre site
- Configurez **Google Analytics** pour suivre le trafic
- Ajoutez des **meta tags SEO** pour le référencement

### Sécurité
- Générez une **clé secrète forte** pour `SECRET_KEY`
- Activez les **logs d'accès**
- Surveillez les **tentatives de connexion suspectes**

### Performance
- Activez la **compression gzip**
- Optimisez les **images uploadées**
- Utilisez un **CDN** pour les fichiers statiques (optionnel)

---

<div align="center">

# 🚀 Prêt à Déployer !

**Suivez les étapes ci-dessus et votre application sera en ligne en moins de 5 minutes !**

🇲🇱 Mali | 🇧🇫 Burkina Faso | 🇳🇪 Niger

**Fait avec ❤️ pour l'Alliance des États du Sahel**

---

[⬆ Retour en haut](#-guide-de-déploiement-aesconnect-sur-render)

</div>
