from flask_smorest import Blueprint, abort
from flask import request, jsonify, session, current_app
from models import db, User
from cloudinary.uploader import upload
from werkzeug.security import generate_password_hash, check_password_hash
from schemas import UserSchema, UserRegisterSchema, UserLoginSchema, SuccessSchema

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

def require_login(f):
    """Decorator to require user login"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            abort(401, message="Authentication required")
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@auth_bp.route('/register', methods=['POST'])
@auth_bp.arguments(UserRegisterSchema)
@auth_bp.response(201, SuccessSchema(exclude=('success',)), description="Inscription réussie")
def register(new_user_data):
    """User registration"""
    try:
        username = new_user_data['username']
        email = new_user_data['email']
        password = new_user_data['password']
        
        # Vérifier si l'utilisateur ou l'email existe déjà via l'ORM
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            abort(400, message='Nom d\'utilisateur ou email déjà utilisé')
        
        # Créer un nouvel utilisateur via l'ORM
        new_user = User(
            username=username,
            email=email,
            full_name=new_user_data['full_name'],
            country=new_user_data.get('country', ''),
            city=new_user_data.get('city', ''),
            avatar_url=new_user_data.get('avatar_url', '')
        )
        new_user.set_password(password) # Utilise la méthode set_password du modèle User
        
        db.session.add(new_user)
        db.session.commit()
        
        user_id = new_user.id
        
        # Log in the user
        session['user_id'] = user_id
        session['username'] = username
        
        return {
            'message': 'Compte créé avec succès',
            'user': new_user.to_dict()
        }
    
    except Exception as e:
        current_app.logger.error(f"Erreur: {e}")
        abort(500, message=str(e))

@auth_bp.route('/login', methods=['POST'])
@auth_bp.arguments(UserLoginSchema)
@auth_bp.response(200, SuccessSchema(exclude=('success',)), description="Connexion réussie")
def login(login_data):
    """User login"""
    try:
        username = login_data['username']
        password = login_data['password']
        
        # Récupérer l'utilisateur via l'ORM
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            
            return {
                'message': 'Connexion réussie',
                'user': user.to_dict() # Utilisation de la méthode to_dict() du modèle
            }
        else:
            abort(401, message='Nom d\'utilisateur ou mot de passe incorrect')
    
    except Exception as e:
        current_app.logger.error(f"Erreur: {e}")
        abort(500, message=str(e))

@auth_bp.route('/logout', methods=['POST'])
@auth_bp.response(200, SuccessSchema, description="Déconnexion réussie")
def logout():
    """User logout"""
    session.clear()
    return {'success': True, 'message': 'Déconnexion réussie'}

@auth_bp.route('/profile', methods=['GET'])
@require_login
@auth_bp.response(200, UserSchema, description="Récupération du profil réussie")
def get_profile():
    """Get user profile"""
    try:
        # Récupérer l'utilisateur par ID de session via l'ORM
        user = User.query.get(session['user_id'])
        
        if user:
            return user
        else:
            abort(404, message='Utilisateur non trouvé')
    
    except Exception as e:
        current_app.logger.error(f"Erreur: {e}")
        abort(500, message=str(e))

@auth_bp.route('/profile', methods=['PUT'])
@require_login
def update_profile():
    """Update user profile"""
    try:
        user = User.query.get(session['user_id'])
        if not user:
            abort(404, message='Utilisateur non trouvé')
        
        data = request.get_json()
        
        # Mise à jour des champs autorisés
        if 'full_name' in data:
            user.full_name = data['full_name']
        if 'bio' in data:
            user.bio = data['bio']
        if 'country' in data:
            user.country = data['country']
        if 'city' in data:
            user.city = data['city']
        if 'avatar_url' in data:
            user.avatar_url = data['avatar_url']
        
        db.session.commit()
        
        return jsonify(user.to_dict())
        
    except Exception as e:
        current_app.logger.error(f"Erreur update profile: {e}")
        db.session.rollback()
        abort(500, message=str(e))

@auth_bp.route('/profile/avatar', methods=['POST'])
@require_login
def upload_avatar():
    """Upload or update user profile picture"""
    try:
        if 'avatar' not in request.files:
            abort(400, message='Aucun fichier d\'avatar fourni')
        
        avatar_file = request.files['avatar']
        
        if avatar_file.filename == '':
            abort(400, message='Nom de fichier invalide')
        
        # Upload vers Cloudinary
        upload_result = upload(avatar_file, folder="aesconnect_avatars", public_id=f"user_{session['user_id']}_avatar", overwrite=True)
        avatar_url = upload_result.get('secure_url')
        
        if not avatar_url:
            abort(500, message="Échec de l'upload de l'avatar")
            
        # Mise à jour de l'URL dans la base de données
        user = User.query.get(session['user_id'])
        if not user:
            abort(404, message='Utilisateur non trouvé')

        user.avatar_url = avatar_url
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Avatar mis à jour avec succès',
            'avatar_url': avatar_url
        })
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de l\\'upload de l\\'avatar: {e}")
        db.session.rollback()
        abort(500, message=str(e))

