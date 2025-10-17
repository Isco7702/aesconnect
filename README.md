# 🌍 AES CONNECT - Réseau Social de l'Alliance des États du Sahel

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)]()

**AES Connect** est une plateforme de réseau social moderne dédiée à l'Alliance des États du Sahel (Mali, Burkina Faso, Niger). Elle permet aux citoyens de se connecter, partager, échanger et construire une communauté sahélienne forte et unie.

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
- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Installation Locale

```bash
# 1. Cloner le repository
git clone https://github.com/Isco7702/aesconnect.git
cd aesconnect

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Lancer l'application
python3 app.py
```

L'application sera accessible à l'adresse : **http://localhost:5000**

### Mode Production (avec Gunicorn)

```bash
gunicorn --bind 0.0.0.0:5000 app:app
```

## 🌐 Déploiement sur Render

### Déploiement Automatique

1. **Connectez-vous** à [render.com](https://render.com)
2. **Créez un nouveau Web Service**
3. **Connectez votre repository GitHub** : `Isco7702/aesconnect`
4. Render détectera automatiquement le fichier `render.yaml`
5. Le déploiement se fera automatiquement en ~5 minutes

### Configuration Manuelle

Si vous préférez configurer manuellement :

- **Build Command** : `pip install -r requirements.txt`
- **Start Command** : `gunicorn --bind 0.0.0.0:$PORT app:app`
- **Environment** : Python 3

### Variables d'Environnement (Optionnelles)

```env
FLASK_ENV=production
SECRET_KEY=votre_clé_secrète_générée
DATABASE_PATH=/opt/render/project/src/social_network.db
```

## 📁 Structure du Projet

```
aesconnect/
├── app.py                  # Application Flask principale (590+ lignes)
├── requirements.txt        # Dépendances Python
├── render.yaml            # Configuration Render
├── create_admin.py        # Script de création d'admin
├── .gitignore             # Fichiers à ignorer
├── templates/
│   └── index.html         # Interface utilisateur complète (44KB)
├── README.md              # Ce fichier
├── STATUS_PROJET.md       # État détaillé du projet
└── DEMARRAGE_RAPIDE.md    # Guide de lancement rapide
```

## 🛠️ Technologies Utilisées

### Backend
- **Flask 3.0.0** - Framework web Python
- **SQLite** - Base de données relationnelle
- **Werkzeug** - Sécurité et hachage des mots de passe
- **Gunicorn** - Serveur WSGI pour production

### Frontend
- **HTML5 / CSS3** - Structure et style
- **JavaScript (Vanilla)** - Logique applicative
- **Responsive Design** - Compatible tous appareils

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
