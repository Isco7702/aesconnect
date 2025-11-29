"""
AESConnect - Réseau Social Monolithique
Backend Flask + Frontend intégré
Tout-en-un pour déploiement sur Render
"""
from flask import Flask, request, jsonify, session, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os
import secrets

# ========== INITIALISATION FLASK ==========
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
CORS(app, supports_credentials=True)

# ========== CONFIGURATION DATABASE ==========
DATABASE_PATH = os.environ.get('DATABASE_PATH', 
    '/opt/render/project/src/social_network.db' if os.environ.get('RENDER') else './social_network.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ========== MODELS ==========
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    bio = db.Column(db.Text, default='')
    avatar_url = db.Column(db.String(255), default='')
    country = db.Column(db.String(80), default='')
    city = db.Column(db.String(80), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    posts = db.relationship('Post', backref='author', lazy='dynamic', foreign_keys='Post.author_id')
    comments = db.relationship('Comment', backref='comment_author', lazy='dynamic')
    likes = db.relationship('Like', backref='liker', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    likes = db.relationship('Like', backref='post_liked', lazy='dynamic')

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Like(db.Model):
    __tablename__ = 'likes'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('post_id', 'user_id', name='_post_user_uc'),)

class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, default='')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_private = db.Column(db.Boolean, default=False)
    
    creator = db.relationship('User', backref='created_groups', foreign_keys=[created_by])
    members = db.relationship('GroupMember', backref='group', lazy='dynamic')

class GroupMember(db.Model):
    __tablename__ = 'group_members'
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.String(20), default='member')
    __table_args__ = (db.UniqueConstraint('group_id', 'user_id', name='_group_user_uc'),)

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    
    sender = db.relationship('User', backref='sent_messages', foreign_keys=[sender_id])
    receiver = db.relationship('User', backref='received_messages', foreign_keys=[receiver_id])

# ========== HELPER FUNCTIONS ==========
def require_login(f):
    """Decorator to require user login"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# ========== ROUTES ==========

# ===== ROUTE D'ACCUEIL =====
@app.route('/')
def index():
    """Page d'accueil - Interface utilisateur"""
    return render_template('index.html')

@app.route('/api')
def api_info():
    """Information sur l'API"""
    return jsonify({
        'status': 'API Running',
        'version': '1.0',
        'message': 'Welcome to AESConnect API',
        'service': 'Social Network - Sahel Region',
        'motto': 'Notre voix, notre espace, notre Sahel'
    })

# ===== AUTH ROUTES =====
@app.route('/register', methods=['POST'])
def register():
    """User registration"""
    data = request.get_json()
    
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name')
    
    if not all([username, email, password, full_name]):
        return jsonify({'success': False, 'error': 'Tous les champs sont requis'})
    
    # Check if user exists
    existing_user = User.query.filter(
        (User.username == username) | (User.email == email)
    ).first()
    
    if existing_user:
        return jsonify({'success': False, 'error': 'Nom d\'utilisateur ou email déjà utilisé'})
    
    # Create new user
    new_user = User(
        username=username,
        email=email,
        full_name=full_name,
        country=data.get('country', ''),
        city=data.get('city', ''),
        avatar_url=data.get('avatar_url', '')
    )
    new_user.set_password(password)
    
    db.session.add(new_user)
    db.session.commit()
    
    session['user_id'] = new_user.id
    
    return jsonify({
        'success': True,
        'message': 'Inscription réussie',
        'user': {
            'id': new_user.id,
            'username': new_user.username,
            'full_name': new_user.full_name,
            'email': new_user.email,
            'avatar_url': new_user.avatar_url
        }
    })

@app.route('/login', methods=['POST'])
def login():
    """User login"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'error': 'Username et password requis'})
    
    user = User.query.filter(
        (User.username == username) | (User.email == username)
    ).first()
    
    if user and user.check_password(password):
        session['user_id'] = user.id
        
        return jsonify({
            'success': True,
            'message': 'Connexion réussie',
            'user': {
                'id': user.id,
                'username': user.username,
                'full_name': user.full_name,
                'email': user.email,
                'avatar_url': user.avatar_url
            }
        })
    
    return jsonify({'success': False, 'error': 'Identifiants incorrects'})

@app.route('/logout', methods=['POST'])
def logout():
    """User logout"""
    session.clear()
    return jsonify({'success': True, 'message': 'Déconnexion réussie'})

@app.route('/profile', methods=['GET'])
@require_login
def profile():
    """Get current user profile"""
    user = User.query.get(session['user_id'])
    if user:
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'full_name': user.full_name,
                'email': user.email,
                'avatar_url': user.avatar_url,
                'country': user.country,
                'city': user.city
            }
        })
    return jsonify({'success': False, 'error': 'Utilisateur non trouvé'})

# ===== POSTS ROUTES =====
@app.route('/posts', methods=['GET', 'POST'])
@require_login
def posts():
    """Get all posts or create a new post"""
    if request.method == 'GET':
        # Get all posts with likes and comments count
        posts_query = db.session.query(
            Post,
            User.full_name,
            db.func.count(Like.id.distinct()).label('likes_count'),
            db.func.count(Comment.id.distinct()).label('comments_count'),
            db.func.max(
                db.case((Like.user_id == session['user_id'], 1), else_=0)
            ).label('user_liked')
        ).join(User, Post.author_id == User.id)\
        .outerjoin(Like, Post.id == Like.post_id)\
        .outerjoin(Comment, Post.id == Comment.post_id)\
        .group_by(Post.id)\
        .order_by(Post.created_at.desc())\
        .all()
        
        posts_list = [{
            'id': post.Post.id,
            'content': post.Post.content,
            'image_url': post.Post.image_url,
            'author_id': post.Post.author_id,
            'full_name': post.full_name,
            'created_at': post.Post.created_at.isoformat(),
            'likes_count': post.likes_count,
            'comments_count': post.comments_count,
            'user_liked': post.user_liked
        } for post in posts_query]
        
        return jsonify({'success': True, 'posts': posts_list})
    
    elif request.method == 'POST':
        # Create new post
        data = request.get_json()
        content = data.get('content')
        
        if not content:
            return jsonify({'success': False, 'error': 'Contenu requis'})
        
        new_post = Post(
            content=content,
            author_id=session['user_id'],
            image_url=data.get('image_url', '')
        )
        
        db.session.add(new_post)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Post créé', 'post_id': new_post.id})

@app.route('/posts/<int:post_id>/like', methods=['POST'])
@require_login
def toggle_like(post_id):
    """Toggle like on a post"""
    existing_like = Like.query.filter_by(
        post_id=post_id,
        user_id=session['user_id']
    ).first()
    
    if existing_like:
        db.session.delete(existing_like)
        db.session.commit()
        liked = False
    else:
        new_like = Like(post_id=post_id, user_id=session['user_id'])
        db.session.add(new_like)
        db.session.commit()
        liked = True
    
    # Get updated likes count
    likes_count = Like.query.filter_by(post_id=post_id).count()
    
    return jsonify({
        'success': True,
        'liked': liked,
        'likes_count': likes_count
    })

# ===== GROUPS ROUTES =====
@app.route('/groups', methods=['GET', 'POST'])
@require_login
def groups():
    """Get all groups or create a new group"""
    if request.method == 'GET':
        # Get all groups with member count
        groups_query = db.session.query(
            Group,
            db.func.count(GroupMember.id).label('members_count')
        ).outerjoin(GroupMember, Group.id == GroupMember.group_id)\
        .group_by(Group.id)\
        .order_by(Group.created_at.desc())\
        .all()
        
        groups_list = [{
            'id': group.Group.id,
            'name': group.Group.name,
            'description': group.Group.description,
            'is_private': group.Group.is_private,
            'created_by': group.Group.created_by,
            'members_count': group.members_count,
            'created_at': group.Group.created_at.isoformat()
        } for group in groups_query]
        
        return jsonify({'success': True, 'groups': groups_list})
    
    elif request.method == 'POST':
        # Create new group
        data = request.get_json()
        name = data.get('name')
        
        if not name:
            return jsonify({'success': False, 'error': 'Nom du groupe requis'})
        
        new_group = Group(
            name=name,
            description=data.get('description', ''),
            is_private=data.get('is_private', False),
            created_by=session['user_id']
        )
        
        db.session.add(new_group)
        db.session.commit()
        
        # Add creator as admin member
        member = GroupMember(
            group_id=new_group.id,
            user_id=session['user_id'],
            role='admin'
        )
        db.session.add(member)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Groupe créé', 'group_id': new_group.id})

# ===== MESSAGES ROUTES =====
@app.route('/messages', methods=['GET', 'POST'])
@require_login
def messages():
    """Get all messages or send a new message"""
    if request.method == 'GET':
        # Get all messages for current user
        messages_query = db.session.query(
            Message,
            User.full_name.label('sender_name')
        ).join(User, Message.sender_id == User.id)\
        .filter(
            (Message.sender_id == session['user_id']) | (Message.receiver_id == session['user_id'])
        ).order_by(Message.created_at.desc())\
        .all()
        
        # Get receiver names
        messages_list = []
        for msg in messages_query:
            receiver_name = None
            if msg.Message.receiver_id != session['user_id']:
                receiver = User.query.get(msg.Message.receiver_id)
                if receiver:
                    receiver_name = receiver.full_name
            
            messages_list.append({
                'id': msg.Message.id,
                'content': msg.Message.content,
                'sender_id': msg.Message.sender_id,
                'receiver_id': msg.Message.receiver_id,
                'sender_name': msg.sender_name,
                'receiver_name': receiver_name,
                'is_read': msg.Message.is_read,
                'created_at': msg.Message.created_at.isoformat()
            })
        
        return jsonify({'success': True, 'messages': messages_list})
    
    elif request.method == 'POST':
        # Send new message
        data = request.get_json()
        receiver_id = data.get('receiver_id')
        content = data.get('content')
        
        if not all([receiver_id, content]):
            return jsonify({'success': False, 'error': 'Destinataire et contenu requis'})
        
        new_message = Message(
            sender_id=session['user_id'],
            receiver_id=receiver_id,
            content=content
        )
        
        db.session.add(new_message)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Message envoyé', 'message_id': new_message.id})

# ===== USERS ROUTES =====
@app.route('/users/search', methods=['GET'])
@require_login
def search_users():
    """Search users"""
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({'success': True, 'users': []})
    
    users = User.query.filter(
        (User.username.like(f'%{query}%')) | (User.full_name.like(f'%{query}%'))
    ).filter(User.id != session['user_id']).limit(10).all()
    
    users_list = [{
        'id': user.id,
        'username': user.username,
        'full_name': user.full_name,
        'avatar_url': user.avatar_url
    } for user in users]
    
    return jsonify({'success': True, 'users': users_list})

# ===== HEALTH CHECK =====
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        db.session.execute(db.text('SELECT 1'))
        db_status = 'connected'
    except Exception as e:
        db_status = f'error: {str(e)}'
    
    return jsonify({
        'status': 'healthy',
        'service': 'AESConnect',
        'database': db_status,
        'motto': 'Notre voix, notre espace, notre Sahel 🇲🇱 🇧🇫 🇳🇪'
    })

# ========== INITIALIZATION ==========
with app.app_context():
    db.create_all()
    print("✅ Database tables created successfully!")

# ========== RUN APPLICATION ==========
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
