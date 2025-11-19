import sqlite3
import os
import sqlite3

# Configuration de la base de données
# Conserver cette constante car elle est utilisée dans app.py pour configurer l'ORM.
DATABASE_PATH = os.environ.get('DATABASE_PATH', 
    '/opt/render/project/src/social_network.db' if os.environ.get('RENDER') else './social_network.db')

# Note: Les fonctions get_db_connection et init_db ont été supprimées car
# toutes les routes de l'application utilisent maintenant l'ORM SQLAlchemy.
# Les scripts externes (create_admin.py, seed_demo_data.py) doivent être mis à jour
# pour utiliser directement l'ORM.

