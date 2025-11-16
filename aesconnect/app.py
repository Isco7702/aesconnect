from flask import Flask, request, jsonify, session, Blueprint, send_from_directory
from flask_cors import CORS
from flask_smorest import Api
import os
import secrets
import cloudinary
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url

# Initialisation de l'application Flask
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config["API_TITLE"] = "AESConnect API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.2"
api = Api(app)
CORS(app, supports_credentials=True)

# --- Configuration de Cloudinary ---
cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET')
)

# --- Configuration de la base de données et de l'ORM ---
from .models import db
DATABASE_PATH = os.environ.get('DATABASE_PATH', 
    '/opt/render/project/src/social_network.db' if os.environ.get('RENDER') else './social_network.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# --- Initialisation des tables de la base de données ---
with app.app_context():
    db.create_all()

# --- Enregistrement des Blueprints ---
from .routes.auth import auth_bp
from .routes.posts import posts_bp
from .routes.groups import groups_bp
from .routes.messages import messages_bp
from .routes.utils import utils_bp
from .routes.notifications import notifications_bp

api.register_blueprint(auth_bp)
api.register_blueprint(posts_bp)
api.register_blueprint(groups_bp)
api.register_blueprint(messages_bp)
api.register_blueprint(utils_bp)
api.register_blueprint(notifications_bp)

# --- Routes de base pour l'API ---
# --- Configuration pour servir le Frontend React (Hybrid Monolithic) ---
FRONTEND_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dist')

# Route pour servir les fichiers statiques (CSS, JS, images)
@app.route('/assets/<path:filename>')
def serve_static_assets(filename):
    return send_from_directory(os.path.join(FRONTEND_FOLDER, 'assets'), filename)

# Route Catch-All pour le routage côté client (SPA)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    # On sert l'index.html pour toutes les routes non gérées par l'API
    return send_from_directory(FRONTEND_FOLDER, 'index.html')

# Gestionnaire d'erreur 404 pour servir le Frontend
@app.errorhandler(404)
def not_found(error):
    # Servir le Frontend pour toutes les routes non trouvées
    return send_from_directory(FRONTEND_FOLDER, 'index.html')

# --- Routes de base pour l'API ---


# --- Exécution de l'application ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

