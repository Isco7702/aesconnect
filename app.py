from flask import Flask, request, jsonify, session
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

# Configuration Flask-Smorest
app.config['API_TITLE'] = 'AESConnect API'
app.config['API_VERSION'] = 'v1'
app.config['OPENAPI_VERSION'] = '3.0.2'
app.config['OPENAPI_URL_PREFIX'] = '/'
app.config['OPENAPI_SWAGGER_UI_PATH'] = '/swagger-ui'
app.config['OPENAPI_SWAGGER_UI_URL'] = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist/'

api = Api(app)
CORS(app, supports_credentials=True)

# --- Configuration de Cloudinary ---
cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET')
)

# --- Configuration de la base de données et de l'ORM ---
from models import db
DATABASE_PATH = os.environ.get('DATABASE_PATH', 
    '/opt/render/project/src/social_network.db' if os.environ.get('RENDER') else './social_network.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# --- Initialisation des tables de la base de données ---
with app.app_context():
    db.create_all()

# --- Enregistrement des Blueprints ---
from routes.auth import auth_bp
from routes.posts import posts_bp
from routes.groups import groups_bp
from routes.messages import messages_bp
from routes.utils import utils_bp
from routes.notifications import notifications_bp

api.register_blueprint(auth_bp)
api.register_blueprint(posts_bp)
api.register_blueprint(groups_bp)
api.register_blueprint(messages_bp)
api.register_blueprint(utils_bp)
api.register_blueprint(notifications_bp)

# --- Routes de base pour l'API ---
@app.route('/')
def index():
    """Endpoint de base de l'API"""
    return jsonify({
        'status': 'API Running',
        'version': '1.0',
        'message': 'Welcome to the AESConnect API. Use /health to check database status.'
    })

# --- Exécution de l'application ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

