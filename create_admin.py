#!/usr/bin/env python3
"""
Script pour créer un utilisateur administrateur par défaut
"""
import os
import sys
import sqlite3
from werkzeug.security import generate_password_hash

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(__file__))

from app import DATABASE_PATH, init_db

def create_admin_user():
    """Créer un utilisateur administrateur par défaut"""
    try:
        # Initialiser la base de données
        init_db()
        print("Base de données initialisée avec succès")
        
        # Connexion à la base de données
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Vérifier si l'admin existe déjà
        cursor.execute('SELECT id FROM users WHERE username = ?', ('admin',))
        if cursor.fetchone():
            print("L'utilisateur admin existe déjà")
            conn.close()
            return
        
        # Créer l'utilisateur admin
        admin_data = {
            'username': 'admin',
            'email': 'admin@aesconnect.com',
            'password_hash': generate_password_hash('admin123'),
            'full_name': 'Administrateur AES',
            'bio': 'Compte administrateur de la plateforme AES Connect'
        }
        
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, full_name, bio)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            admin_data['username'],
            admin_data['email'],
            admin_data['password_hash'],
            admin_data['full_name'],
            admin_data['bio']
        ))
        
        conn.commit()
        conn.close()
        
        print("Utilisateur admin créé avec succès!")
        print("Nom d'utilisateur: admin")
        print("Mot de passe: admin123")
        print("Email: admin@aesconnect.com")
        
    except Exception as e:
        print(f"Erreur lors de la création de l'admin: {e}")
        sys.exit(1)

if __name__ == '__main__':
    create_admin_user()