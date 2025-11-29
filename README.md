# AESConnect

**Notre voix, notre espace, notre Sahel** 🇲🇱 🇧🇫 🇳🇪

## Description

Réseau social monolithique pour les jeunes du Sahel (Mali, Burkina Faso, Niger).
Backend Flask + Frontend intégré, déployé sur Render.

## Fonctionnalités

- ✅ Inscription et connexion
- ✅ Création et partage de posts
- ✅ Système de likes et commentaires
- ✅ Groupes communautaires
- ✅ Messagerie privée
- ✅ Recherche d'utilisateurs

## Technologies

- **Backend**: Flask + SQLAlchemy
- **Frontend**: HTML/CSS/JavaScript (Vanilla)
- **Database**: SQLite
- **Déploiement**: Render

## Installation

```bash
pip install -r requirements.txt
python app.py
```

## Déploiement sur Render

L'application se déploie automatiquement via GitHub.

URL de production: https://aesconnect-1.onrender.com

## Structure

```
aesconnect/
├── app.py              # Backend Flask complet (routes + models)
├── templates/
│   └── index.html      # Frontend intégré
├── static/             # Assets CSS/JS/Images (optionnel)
├── requirements.txt    # Dépendances Python
├── Procfile            # Configuration Render
├── render.yaml         # Configuration service Render
└── README.md           # Documentation
```

## Auteur

Développé pour la communauté du Sahel 🌍
