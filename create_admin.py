#!/usr/bin/env python3
"""
Script pour créer un utilisateur administrateur par défaut
"""
import os
import sys
import getpass
from werkzeug.security import generate_password_hash
from flask import Flask
from .database import DATABASE_PATH
from .models import db, User

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(__file__))

# Configuration temporaire de l'application Flask pour le contexte
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def create_admin_user():
    """Créer un utilisateur administrateur par défaut en utilisant l'ORM"""
    try:
        # Assurer que les tables existent
        db.create_all()
        
        ADMIN_USERNAME = 'admin'
        ADMIN_EMAIL = 'admin@aesconnect.com'
        ADMIN_FULL_NAME = 'Administrateur AES'
        ADMIN_BIO = 'Compte administrateur de la plateforme AES Connect'
        
        # Vérifier si l'admin existe déjà
        existing_admin = User.query.filter_by(username=ADMIN_USERNAME).first()
        
        if existing_admin:
            print(f"Utilisateur admin '{ADMIN_USERNAME}' existe déjà.")
            return
        
        # Récupérer le mot de passe de l'administrateur
        admin_password = os.environ.get('ADMIN_PASSWORD')
        
        if not admin_password:
            print("Erreur: La variable d'environnement ADMIN_PASSWORD n'est pas définie.")
            print("Veuillez exécuter le script avec: ADMIN_PASSWORD='votre_mot_de_passe' python3 create_admin.py")
            sys.exit(1)

        # Créer l'utilisateur admin via l'ORM
        new_admin = User(
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            full_name=ADMIN_FULL_NAME,
            bio=ADMIN_BIO
        )
        # La méthode set_password doit être définie dans le modèle User (ce qui est le cas)
        new_admin.set_password(admin_password)
        
        db.session.add(new_admin)
        db.session.commit()
        
        print("Utilisateur admin créé avec succès!")
        print(f"Nom d'utilisateur: {ADMIN_USERNAME}")
        print("Mot de passe: [Utilise la variable d'environnement ADMIN_PASSWORD]")
        print(f"Email: {ADMIN_EMAIL}")
        
    except Exception as e:
        db.session.rollback()
        print(f"Erreur lors de la création de l'admin: {e}")
        sys.exit(1)

if __name__ == '__main__':
    with app.app_context():
        create_admin_user()