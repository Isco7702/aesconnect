# AES Connect - Reseau Social de l'Alliance des Etats du Sahel

Le reseau social moderne et securise pour les citoyens du Mali, du Burkina Faso et du Niger.

**Notre voix, notre espace, notre Sahel.**

## Fonctionnalites

### Reseau Social Complet
- Profils utilisateurs avec photos et bio
- Publications avec images, localisation et humeurs
- Systeme de reactions (like, love, support, celebrate, think)
- Commentaires avec reponses en threads
- Systeme de follow/unfollow
- Messagerie privee en temps reel
- Notifications
- Groupes (publics et prives)
- Recherche globale (utilisateurs, posts, groupes)
- Page Decouvrir avec suggestions

### Contenu Culturel AES
- Proverbe sahelien du jour (30+ proverbes)
- Calendrier culturel (fetes nationales, evenements)
- 10 groupes par defaut (communautes AES)

### Securite
- Authentification JWT avec tokens securises
- Hashage bcrypt des mots de passe
- Validation stricte des inputs
- Rate limiting sur les endpoints critiques
- Protection XSS et injection
- Systeme de signalement
- Blocage d'utilisateurs

### Performance
- Progressive Web App (installable)
- Service Worker pour cache offline
- Lazy loading des images
- Pagination et infinite scroll
- Design responsive (mobile-first)

### Design
- Interface sombre moderne
- Couleurs AES (vert, rouge, or)
- Animations et micro-interactions
- Typographie Poppins + Inter
- Compatible mobile, tablette et desktop

## Stack Technique

- **Backend**: Flask (Python)
- **Base de donnees**: SQLite avec SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, JavaScript vanilla
- **Auth**: JWT custom
- **Upload**: Cloudinary (optionnel)
- **Deploiement**: Render.com

## Configuration

### Variables d'environnement
```
SECRET_KEY=<votre_cle_secrete>
JWT_SECRET=<votre_jwt_secret>
DATABASE_PATH=/opt/render/project/src/aesconnect.db
CLOUDINARY_CLOUD_NAME=<optionnel>
CLOUDINARY_API_KEY=<optionnel>
CLOUDINARY_API_SECRET=<optionnel>
```

### Installation locale
```bash
pip install -r requirements.txt
python app.py
```

### Deploiement Render
1. Connecter le repository GitHub
2. Configurer les variables d'environnement
3. Deployer automatiquement

## URL de production
https://aesconnect-1.onrender.com

## Licence
Tous droits reserves - AES Connect 2024-2026
