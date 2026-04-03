"""
AES Connect - Reseau Social de l'Alliance des Etats du Sahel
Backend Flask complet + Frontend integre
Mali - Burkina Faso - Niger
"""
import os
import re
import json
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from functools import wraps

from flask import (Flask, request, jsonify, render_template,
                   send_from_directory, make_response)
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func, or_, and_, desc, text

# ══════════════════════════════════════════════════════════════
# INITIALISATION FLASK
# ══════════════════════════════════════════════════════════════
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Database
DATABASE_PATH = os.environ.get('DATABASE_PATH',
    '/opt/render/project/src/aesconnect.db' if os.environ.get('RENDER') else './aesconnect.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

db = SQLAlchemy(app)
CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "*"}})

# JWT Secret
JWT_SECRET = os.environ.get('JWT_SECRET', app.config['SECRET_KEY'])
JWT_EXPIRY_DAYS = 30

# ══════════════════════════════════════════════════════════════
# JWT HELPERS
# ══════════════════════════════════════════════════════════════
import base64, hmac

def _b64encode(data):
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode()

def _b64decode(s):
    s += '=' * (4 - len(s) % 4)
    return base64.urlsafe_b64decode(s)

def create_jwt(payload):
    header = _b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload['exp'] = (datetime.now(timezone.utc) + timedelta(days=JWT_EXPIRY_DAYS)).isoformat()
    payload['iat'] = datetime.now(timezone.utc).isoformat()
    body = _b64encode(json.dumps(payload).encode())
    signature = _b64encode(hmac.new(JWT_SECRET.encode(), f"{header}.{body}".encode(), hashlib.sha256).digest())
    return f"{header}.{body}.{signature}"

def decode_jwt(token):
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        header, body, signature = parts
        expected_sig = _b64encode(hmac.new(JWT_SECRET.encode(), f"{header}.{body}".encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(signature, expected_sig):
            return None
        payload = json.loads(_b64decode(body))
        exp = datetime.fromisoformat(payload['exp'])
        if exp < datetime.now(timezone.utc):
            return None
        return payload
    except Exception:
        return None

def get_current_user():
    auth = request.headers.get('Authorization', '')
    if auth.startswith('Bearer '):
        payload = decode_jwt(auth[7:])
        if payload and 'user_id' in payload:
            return User.query.get(payload['user_id'])
    return None

def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({'success': False, 'error': 'Authentification requise'}), 401
        request.current_user = user
        return f(*args, **kwargs)
    return decorated

def jwt_optional(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        request.current_user = get_current_user()
        return f(*args, **kwargs)
    return decorated

# ══════════════════════════════════════════════════════════════
# RATE LIMITING (simple in-memory)
# ══════════════════════════════════════════════════════════════
_rate_limits = {}

def rate_limit(max_requests=100, window=60):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            ip = request.remote_addr
            key = f"{f.__name__}:{ip}"
            now = datetime.now(timezone.utc).timestamp()
            if key in _rate_limits:
                reqs = [t for t in _rate_limits[key] if now - t < window]
                if len(reqs) >= max_requests:
                    return jsonify({'success': False, 'error': 'Trop de requetes. Reessayez plus tard.'}), 429
                reqs.append(now)
                _rate_limits[key] = reqs
            else:
                _rate_limits[key] = [now]
            return f(*args, **kwargs)
        return decorated
    return decorator

# ══════════════════════════════════════════════════════════════
# DATABASE MODELS
# ══════════════════════════════════════════════════════════════

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    bio = db.Column(db.Text, default='')
    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(20), default='')
    country = db.Column(db.String(80), default='')
    city = db.Column(db.String(80), default='')
    phone = db.Column(db.String(30), default='')
    profile_picture = db.Column(db.String(500), default='')
    cover_photo = db.Column(db.String(500), default='')
    is_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    is_private = db.Column(db.Boolean, default=False)
    follower_count = db.Column(db.Integer, default=0)
    following_count = db.Column(db.Integer, default=0)
    post_count = db.Column(db.Integer, default=0)
    badge = db.Column(db.String(50), default='')
    language = db.Column(db.String(10), default='fr')
    dark_mode = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_seen = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self, include_email=False):
        d = {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'bio': self.bio or '',
            'country': self.country or '',
            'city': self.city or '',
            'profile_picture': self.profile_picture or '',
            'cover_photo': self.cover_photo or '',
            'is_verified': self.is_verified,
            'is_private': self.is_private,
            'follower_count': self.follower_count,
            'following_count': self.following_count,
            'post_count': self.post_count,
            'badge': self.badge or '',
            'created_at': self.created_at.isoformat() if self.created_at else '',
            'last_seen': self.last_seen.isoformat() if self.last_seen else '',
        }
        if include_email:
            d['email'] = self.email
            d['phone'] = self.phone or ''
            d['gender'] = self.gender or ''
            d['dark_mode'] = self.dark_mode
            d['language'] = self.language or 'fr'
        return d


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    images = db.Column(db.Text, default='[]')  # JSON array of URLs
    video_url = db.Column(db.String(500), default='')
    location = db.Column(db.String(200), default='')
    feeling = db.Column(db.String(50), default='')
    visibility = db.Column(db.String(20), default='public')  # public, friends, private
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=True)
    likes_count = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)
    shares_count = db.Column(db.Integer, default=0)
    views_count = db.Column(db.Integer, default=0)
    is_pinned = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    author = db.relationship('User', backref=db.backref('posts', lazy='dynamic'))

    def to_dict(self, current_user_id=None):
        author = User.query.get(self.user_id)
        images = []
        try:
            images = json.loads(self.images) if self.images else []
        except (json.JSONDecodeError, TypeError):
            pass

        user_reaction = None
        is_saved = False
        if current_user_id:
            like = Like.query.filter_by(post_id=self.id, user_id=current_user_id).first()
            if like:
                user_reaction = like.reaction_type
            save = SavedPost.query.filter_by(post_id=self.id, user_id=current_user_id).first()
            if save:
                is_saved = True

        return {
            'id': self.id,
            'user_id': self.user_id,
            'content': self.content,
            'images': images,
            'video_url': self.video_url or '',
            'location': self.location or '',
            'feeling': self.feeling or '',
            'visibility': self.visibility,
            'group_id': self.group_id,
            'likes_count': self.likes_count,
            'comments_count': self.comments_count,
            'shares_count': self.shares_count,
            'views_count': self.views_count,
            'is_pinned': self.is_pinned,
            'user_reaction': user_reaction,
            'is_saved': is_saved,
            'created_at': self.created_at.isoformat() if self.created_at else '',
            'author': {
                'id': author.id,
                'username': author.username,
                'full_name': author.full_name,
                'profile_picture': author.profile_picture or '',
                'is_verified': author.is_verified,
                'badge': author.badge or '',
            } if author else None
        }


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False, index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500), default='')
    likes_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    author = db.relationship('User', backref=db.backref('comments', lazy='dynamic'))
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')

    def to_dict(self):
        author = User.query.get(self.user_id)
        return {
            'id': self.id,
            'user_id': self.user_id,
            'post_id': self.post_id,
            'parent_id': self.parent_id,
            'content': self.content,
            'image_url': self.image_url or '',
            'likes_count': self.likes_count,
            'reply_count': self.replies.count(),
            'created_at': self.created_at.isoformat() if self.created_at else '',
            'author': {
                'id': author.id,
                'username': author.username,
                'full_name': author.full_name,
                'profile_picture': author.profile_picture or '',
                'is_verified': author.is_verified,
            } if author else None
        }


class Like(db.Model):
    __tablename__ = 'likes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False, index=True)
    reaction_type = db.Column(db.String(20), default='like')  # like, love, support, celebrate, think
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='uq_user_post_like'),)


class Follow(db.Model):
    __tablename__ = 'follows'
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    following_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    __table_args__ = (db.UniqueConstraint('follower_id', 'following_id', name='uq_follow'),)


class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    cover_photo = db.Column(db.String(500), default='')
    category = db.Column(db.String(100), default='')
    country = db.Column(db.String(80), default='')
    privacy = db.Column(db.String(20), default='public')
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    member_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    creator = db.relationship('User', backref=db.backref('created_groups', lazy='dynamic'))

    def to_dict(self, current_user_id=None):
        is_member = False
        user_role = None
        if current_user_id:
            membership = GroupMember.query.filter_by(group_id=self.id, user_id=current_user_id).first()
            if membership:
                is_member = True
                user_role = membership.role
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description or '',
            'cover_photo': self.cover_photo or '',
            'category': self.category or '',
            'country': self.country or '',
            'privacy': self.privacy,
            'creator_id': self.creator_id,
            'member_count': self.member_count,
            'is_member': is_member,
            'user_role': user_role,
            'created_at': self.created_at.isoformat() if self.created_at else '',
        }


class GroupMember(db.Model):
    __tablename__ = 'group_members'
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(20), default='member')  # admin, moderator, member
    joined_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    __table_args__ = (db.UniqueConstraint('group_id', 'user_id', name='uq_group_member'),)


class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.String(100), nullable=False, index=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500), default='')
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    sender = db.relationship('User', backref=db.backref('sent_messages', lazy='dynamic'))


class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    actor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    type = db.Column(db.String(50), nullable=False)  # like, comment, follow, mention, message, group
    content = db.Column(db.Text, default='')
    link = db.Column(db.String(200), default='')
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    actor = db.relationship('User', foreign_keys=[actor_id])

    def to_dict(self):
        actor = User.query.get(self.actor_id) if self.actor_id else None
        return {
            'id': self.id,
            'type': self.type,
            'content': self.content,
            'link': self.link or '',
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else '',
            'actor': {
                'id': actor.id,
                'username': actor.username,
                'full_name': actor.full_name,
                'profile_picture': actor.profile_picture or '',
            } if actor else None
        }


class SavedPost(db.Model):
    __tablename__ = 'saved_posts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='uq_saved_post'),)


class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    target_type = db.Column(db.String(20), nullable=False)  # post, comment, user
    target_id = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text, default='')
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class Block(db.Model):
    __tablename__ = 'blocks'
    id = db.Column(db.Integer, primary_key=True)
    blocker_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    blocked_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    __table_args__ = (db.UniqueConstraint('blocker_id', 'blocked_id', name='uq_block'),)


# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════

def create_notification(user_id, actor_id, ntype, content, link=''):
    if user_id == actor_id:
        return
    notif = Notification(user_id=user_id, actor_id=actor_id, type=ntype, content=content, link=link)
    db.session.add(notif)

def get_conversation_id(user1_id, user2_id):
    return f"conv_{min(user1_id, user2_id)}_{max(user1_id, user2_id)}"

def sanitize_input(text, max_length=5000):
    if not text:
        return ''
    text = text.strip()[:max_length]
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '', text)
    return text

def validate_email(email):
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email) is not None

def validate_password(password):
    if len(password) < 8:
        return False, "Le mot de passe doit contenir au moins 8 caracteres"
    if not re.search(r'[A-Z]', password):
        return False, "Le mot de passe doit contenir au moins une majuscule"
    if not re.search(r'[0-9]', password):
        return False, "Le mot de passe doit contenir au moins un chiffre"
    return True, ""


# ══════════════════════════════════════════════════════════════
# PROVERBS & CULTURAL DATA
# ══════════════════════════════════════════════════════════════

SAHEL_PROVERBS = [
    {"text": "L'union fait la force, la division fait la faiblesse.", "origin": "Proverbe Bambara"},
    {"text": "Celui qui a ete mordu par un serpent se mefie d'une corde.", "origin": "Proverbe Mossi"},
    {"text": "La patience est un arbre dont la racine est amere mais le fruit tres doux.", "origin": "Proverbe Haoussa"},
    {"text": "Un seul doigt ne peut pas ramasser un caillou.", "origin": "Proverbe Bambara"},
    {"text": "Le mensonge donne des fleurs mais pas de fruits.", "origin": "Proverbe Peul"},
    {"text": "Quand on ne sait pas ou l'on va, qu'on sache au moins d'ou l'on vient.", "origin": "Proverbe Bambara"},
    {"text": "La bouche qui mange ne parle pas.", "origin": "Proverbe Mossi"},
    {"text": "Le bois a beau rester dans l'eau, il ne deviendra jamais crocodile.", "origin": "Proverbe Bambara"},
    {"text": "Celui qui ne sait pas d'ou il vient ne sait pas ou il va.", "origin": "Proverbe Peul"},
    {"text": "La verite est comme le soleil, elle finit toujours par briller.", "origin": "Proverbe Haoussa"},
    {"text": "Un vieil homme assis voit plus loin qu'un jeune homme debout.", "origin": "Proverbe Mossi"},
    {"text": "Le fleuve fait des detours car personne ne lui montre le chemin.", "origin": "Proverbe Bambara"},
    {"text": "L'etranger a de grands yeux mais ne voit rien.", "origin": "Proverbe Peul"},
    {"text": "Si tu veux aller vite, marche seul. Si tu veux aller loin, marchons ensemble.", "origin": "Proverbe Africain"},
    {"text": "L'arbre ne tombe pas au premier coup de hache.", "origin": "Proverbe Bambara"},
    {"text": "La parole est comme l'eau : une fois versee, elle ne se ramasse plus.", "origin": "Proverbe Mossi"},
    {"text": "Qui seme le vent recolte la tempete.", "origin": "Proverbe Haoussa"},
    {"text": "Le cameleon ne quitte pas un arbre avant d'en tenir un autre.", "origin": "Proverbe Peul"},
    {"text": "La sagesse est comme un baobab : seul on ne peut l'embrasser.", "origin": "Proverbe Africain"},
    {"text": "Le lezard qui tombe du fromager dit : si personne ne le felicite, lui-meme se felicite.", "origin": "Proverbe Bambara"},
    {"text": "La nuit a beau durer, le jour finit par se lever.", "origin": "Proverbe Mossi"},
    {"text": "Celui qui est porte ne connait pas la longueur du chemin.", "origin": "Proverbe Haoussa"},
    {"text": "Quand les elephants se battent, c'est l'herbe qui souffre.", "origin": "Proverbe Peul"},
    {"text": "L'oiseau pris au piege chante plus fort que l'oiseau libre.", "origin": "Proverbe Bambara"},
    {"text": "On ne peut pas empecher l'oiseau de voler au-dessus de sa tete.", "origin": "Proverbe Mossi"},
    {"text": "Le griot ne chante bien que lorsqu'il est inspire.", "origin": "Proverbe Bambara"},
    {"text": "L'oeil du maitre engraisse le cheval.", "origin": "Proverbe Peul"},
    {"text": "Ce n'est pas en tirant sur la tige qu'on fait pousser le mil.", "origin": "Proverbe Mossi"},
    {"text": "La hyene dit : meme si mon pelage est raye, mon coeur reste entier.", "origin": "Proverbe Haoussa"},
    {"text": "Le sel ne dit pas de lui-meme qu'il est sale.", "origin": "Proverbe Bambara"},
]

CULTURAL_EVENTS = [
    {"date": "01-01", "title": "Nouvel An", "country": "AES", "emoji": "🎉"},
    {"date": "01-20", "title": "Fete de l'Armee - Mali", "country": "Mali", "emoji": "🇲🇱"},
    {"date": "03-08", "title": "Journee Internationale de la Femme", "country": "AES", "emoji": "👩"},
    {"date": "04-04", "title": "Fete de la Jeunesse - Niger", "country": "Niger", "emoji": "🇳🇪"},
    {"date": "05-01", "title": "Fete du Travail", "country": "AES", "emoji": "✊"},
    {"date": "05-25", "title": "Journee de l'Afrique", "country": "AES", "emoji": "🌍"},
    {"date": "08-03", "title": "Fete de l'Independance - Niger", "country": "Niger", "emoji": "🇳🇪"},
    {"date": "08-05", "title": "Fete Nationale - Burkina Faso", "country": "Burkina Faso", "emoji": "🇧🇫"},
    {"date": "09-16", "title": "Journee de l'AES", "country": "AES", "emoji": "🤝"},
    {"date": "09-22", "title": "Fete de l'Independance - Mali", "country": "Mali", "emoji": "🇲🇱"},
    {"date": "10-15", "title": "Anniversaire Thomas Sankara", "country": "Burkina Faso", "emoji": "✊"},
    {"date": "11-01", "title": "Toussaint", "country": "AES", "emoji": "🕯️"},
    {"date": "12-11", "title": "Fete Nationale - Burkina Faso", "country": "Burkina Faso", "emoji": "🇧🇫"},
    {"date": "12-18", "title": "Fete de la Republique - Niger", "country": "Niger", "emoji": "🇳🇪"},
    {"date": "12-25", "title": "Noel", "country": "AES", "emoji": "🎄"},
]

DEFAULT_GROUPS = [
    {"name": "Maliens du Monde", "description": "Communaute des Maliens partout dans le monde. Echanges, culture et solidarite.", "category": "Communaute", "country": "Mali"},
    {"name": "Burkina Faso Ensemble", "description": "Le groupe de tous les Burkinabe. Actualites, culture et fraternite.", "category": "Communaute", "country": "Burkina Faso"},
    {"name": "Niger Solidaire", "description": "Espace d'echange et de solidarite pour tous les Nigeriens.", "category": "Communaute", "country": "Niger"},
    {"name": "Alliance AES", "description": "L'union sacree du Mali, du Burkina Faso et du Niger. Ensemble nous sommes plus forts!", "category": "Politique", "country": "AES"},
    {"name": "Etudiants de l'AES", "description": "Etudiants maliens, burkinabe et nigeriens. Entraide academique et opportunites.", "category": "Education", "country": "AES"},
    {"name": "Entrepreneurs du Sahel", "description": "Business, startups et opportunites economiques dans l'espace AES.", "category": "Business", "country": "AES"},
    {"name": "Arts et Culture AES", "description": "Musique, danse, cinema, litterature et artisanat du Sahel.", "category": "Culture", "country": "AES"},
    {"name": "Sport AES", "description": "Football, basketball et tous les sports dans l'espace AES.", "category": "Sport", "country": "AES"},
    {"name": "Cuisine du Sahel", "description": "Recettes, astuces et partage culinaire. Tigadeguena, riz gras, dambou...", "category": "Gastronomie", "country": "AES"},
    {"name": "Actualites AES", "description": "Suivi de l'actualite dans l'espace AES. Informations verifiees.", "category": "Actualites", "country": "AES"},
]

# ══════════════════════════════════════════════════════════════
# PAGE ROUTES
# ══════════════════════════════════════════════════════════════

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')

@app.route('/sw.js')
def service_worker():
    resp = make_response(send_from_directory('static/js', 'sw.js'))
    resp.headers['Service-Worker-Allowed'] = '/'
    resp.headers['Content-Type'] = 'application/javascript'
    return resp

# ══════════════════════════════════════════════════════════════
# AUTH API
# ══════════════════════════════════════════════════════════════

@app.route('/api/auth/register', methods=['POST'])
@rate_limit(max_requests=10, window=60)
def register():
    data = request.get_json() or {}
    username = sanitize_input(data.get('username', ''), 80).lower().replace(' ', '_')
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    full_name = sanitize_input(data.get('full_name', ''), 120)
    country = sanitize_input(data.get('country', ''), 80)

    if not all([username, email, password, full_name]):
        return jsonify({'success': False, 'error': 'Tous les champs sont requis'}), 400

    if len(username) < 3:
        return jsonify({'success': False, 'error': "Le nom d'utilisateur doit avoir au moins 3 caracteres"}), 400

    if not re.match(r'^[a-z0-9_]+$', username):
        return jsonify({'success': False, 'error': "Le nom d'utilisateur ne peut contenir que lettres, chiffres et underscores"}), 400

    if not validate_email(email):
        return jsonify({'success': False, 'error': 'Adresse email invalide'}), 400

    valid, msg = validate_password(password)
    if not valid:
        return jsonify({'success': False, 'error': msg}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'success': False, 'error': "Ce nom d'utilisateur est deja pris"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'error': 'Cet email est deja utilise'}), 400

    user = User(username=username, email=email, full_name=full_name, country=country)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    # Auto-join country group
    for gdata in DEFAULT_GROUPS:
        if gdata['country'] == country or gdata['country'] == 'AES':
            group = Group.query.filter_by(name=gdata['name']).first()
            if group:
                existing = GroupMember.query.filter_by(group_id=group.id, user_id=user.id).first()
                if not existing:
                    member = GroupMember(group_id=group.id, user_id=user.id, role='member')
                    db.session.add(member)
                    group.member_count = GroupMember.query.filter_by(group_id=group.id).count() + 1
    db.session.commit()

    token = create_jwt({'user_id': user.id, 'username': user.username})
    return jsonify({'success': True, 'token': token, 'user': user.to_dict(include_email=True)}), 201


@app.route('/api/auth/login', methods=['POST'])
@rate_limit(max_requests=20, window=60)
def login():
    data = request.get_json() or {}
    login_id = data.get('login', '').strip().lower()
    password = data.get('password', '')

    if not login_id or not password:
        return jsonify({'success': False, 'error': 'Identifiant et mot de passe requis'}), 400

    user = User.query.filter(or_(User.username == login_id, User.email == login_id)).first()

    if not user or not user.check_password(password):
        return jsonify({'success': False, 'error': 'Identifiants incorrects'}), 401

    if not user.is_active:
        return jsonify({'success': False, 'error': 'Compte desactive'}), 403

    user.last_seen = datetime.now(timezone.utc)
    db.session.commit()

    token = create_jwt({'user_id': user.id, 'username': user.username})
    return jsonify({'success': True, 'token': token, 'user': user.to_dict(include_email=True)})


@app.route('/api/auth/me', methods=['GET'])
@jwt_required
def get_me():
    user = request.current_user
    user.last_seen = datetime.now(timezone.utc)
    db.session.commit()
    return jsonify({'success': True, 'user': user.to_dict(include_email=True)})


# ══════════════════════════════════════════════════════════════
# USER PROFILE API
# ══════════════════════════════════════════════════════════════

@app.route('/api/users/<username>', methods=['GET'])
@jwt_optional
def get_user_profile(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'success': False, 'error': 'Utilisateur non trouve'}), 404

    is_following = False
    is_blocked = False
    current = request.current_user
    if current:
        is_following = Follow.query.filter_by(follower_id=current.id, following_id=user.id).first() is not None
        is_blocked = Block.query.filter_by(blocker_id=current.id, blocked_id=user.id).first() is not None

    data = user.to_dict(include_email=(current and current.id == user.id))
    data['is_following'] = is_following
    data['is_blocked'] = is_blocked
    data['is_own_profile'] = current and current.id == user.id
    return jsonify({'success': True, 'user': data})


@app.route('/api/users/profile', methods=['PUT'])
@jwt_required
def update_profile():
    user = request.current_user
    data = request.get_json() or {}

    if 'full_name' in data:
        user.full_name = sanitize_input(data['full_name'], 120)
    if 'bio' in data:
        user.bio = sanitize_input(data['bio'], 500)
    if 'country' in data:
        user.country = sanitize_input(data['country'], 80)
    if 'city' in data:
        user.city = sanitize_input(data['city'], 80)
    if 'phone' in data:
        user.phone = sanitize_input(data['phone'], 30)
    if 'gender' in data:
        user.gender = sanitize_input(data['gender'], 20)
    if 'profile_picture' in data:
        user.profile_picture = data['profile_picture'][:500]
    if 'cover_photo' in data:
        user.cover_photo = data['cover_photo'][:500]
    if 'is_private' in data:
        user.is_private = bool(data['is_private'])
    if 'dark_mode' in data:
        user.dark_mode = bool(data['dark_mode'])
    if 'language' in data:
        user.language = data['language'][:10]

    user.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return jsonify({'success': True, 'user': user.to_dict(include_email=True)})


@app.route('/api/users/<int:user_id>/posts', methods=['GET'])
@jwt_optional
def get_user_posts(user_id):
    page = request.args.get('page', 1, type=int)
    per_page = 20
    current = request.current_user

    posts = Post.query.filter_by(user_id=user_id, group_id=None)\
        .order_by(Post.is_pinned.desc(), Post.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'success': True,
        'posts': [p.to_dict(current.id if current else None) for p in posts.items],
        'has_next': posts.has_next,
        'total': posts.total
    })


# ══════════════════════════════════════════════════════════════
# FOLLOW API
# ══════════════════════════════════════════════════════════════

@app.route('/api/users/<int:user_id>/follow', methods=['POST'])
@jwt_required
def toggle_follow(user_id):
    current = request.current_user
    if current.id == user_id:
        return jsonify({'success': False, 'error': 'Vous ne pouvez pas vous suivre vous-meme'}), 400

    target = User.query.get(user_id)
    if not target:
        return jsonify({'success': False, 'error': 'Utilisateur non trouve'}), 404

    existing = Follow.query.filter_by(follower_id=current.id, following_id=user_id).first()
    if existing:
        db.session.delete(existing)
        target.follower_count = max(0, target.follower_count - 1)
        current.following_count = max(0, current.following_count - 1)
        db.session.commit()
        return jsonify({'success': True, 'following': False, 'follower_count': target.follower_count})
    else:
        follow = Follow(follower_id=current.id, following_id=user_id)
        db.session.add(follow)
        target.follower_count += 1
        current.following_count += 1
        create_notification(user_id, current.id, 'follow', f'{current.full_name} vous suit maintenant')
        db.session.commit()
        return jsonify({'success': True, 'following': True, 'follower_count': target.follower_count})


@app.route('/api/users/<int:user_id>/followers', methods=['GET'])
@jwt_optional
def get_followers(user_id):
    page = request.args.get('page', 1, type=int)
    follows = Follow.query.filter_by(following_id=user_id)\
        .order_by(Follow.created_at.desc())\
        .paginate(page=page, per_page=20, error_out=False)

    users = []
    for f in follows.items:
        u = User.query.get(f.follower_id)
        if u:
            users.append(u.to_dict())
    return jsonify({'success': True, 'users': users, 'has_next': follows.has_next})


@app.route('/api/users/<int:user_id>/following', methods=['GET'])
@jwt_optional
def get_following(user_id):
    page = request.args.get('page', 1, type=int)
    follows = Follow.query.filter_by(follower_id=user_id)\
        .order_by(Follow.created_at.desc())\
        .paginate(page=page, per_page=20, error_out=False)

    users = []
    for f in follows.items:
        u = User.query.get(f.following_id)
        if u:
            users.append(u.to_dict())
    return jsonify({'success': True, 'users': users, 'has_next': follows.has_next})


# ══════════════════════════════════════════════════════════════
# POSTS API
# ══════════════════════════════════════════════════════════════

@app.route('/api/posts', methods=['GET'])
@jwt_required
def get_feed():
    current = request.current_user
    page = request.args.get('page', 1, type=int)
    per_page = 20

    # Get IDs of users I follow
    following_ids = [f.following_id for f in Follow.query.filter_by(follower_id=current.id).all()]
    following_ids.append(current.id)

    posts = Post.query.filter(
        Post.user_id.in_(following_ids),
        Post.group_id == None,
        Post.visibility != 'private'
    ).order_by(Post.created_at.desc())\
     .paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'success': True,
        'posts': [p.to_dict(current.id) for p in posts.items],
        'has_next': posts.has_next,
        'page': page
    })


@app.route('/api/posts/explore', methods=['GET'])
@jwt_required
def get_explore():
    current = request.current_user
    page = request.args.get('page', 1, type=int)
    per_page = 20

    posts = Post.query.filter(
        Post.group_id == None,
        Post.visibility == 'public'
    ).order_by(Post.created_at.desc())\
     .paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'success': True,
        'posts': [p.to_dict(current.id) for p in posts.items],
        'has_next': posts.has_next
    })


@app.route('/api/posts', methods=['POST'])
@jwt_required
@rate_limit(max_requests=30, window=60)
def create_post():
    current = request.current_user
    data = request.get_json() or {}
    content = sanitize_input(data.get('content', ''))
    images = data.get('images', [])
    if isinstance(images, list):
        images = images[:10]
    else:
        images = []

    if not content and not images:
        return jsonify({'success': False, 'error': 'Contenu ou image requis'}), 400

    post = Post(
        user_id=current.id,
        content=content,
        images=json.dumps(images),
        video_url=data.get('video_url', '')[:500],
        location=sanitize_input(data.get('location', ''), 200),
        feeling=sanitize_input(data.get('feeling', ''), 50),
        visibility=data.get('visibility', 'public'),
        group_id=data.get('group_id')
    )
    db.session.add(post)
    current.post_count += 1
    db.session.commit()

    # Handle hashtags & mentions
    mentions = re.findall(r'@(\w+)', content)
    for uname in mentions:
        mentioned = User.query.filter_by(username=uname.lower()).first()
        if mentioned:
            create_notification(mentioned.id, current.id, 'mention',
                              f'{current.full_name} vous a mentionne dans un post', f'/post/{post.id}')
    db.session.commit()

    return jsonify({'success': True, 'post': post.to_dict(current.id)}), 201


@app.route('/api/posts/<int:post_id>', methods=['GET'])
@jwt_optional
def get_post(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'success': False, 'error': 'Post non trouve'}), 404
    current = request.current_user
    post.views_count += 1
    db.session.commit()
    return jsonify({'success': True, 'post': post.to_dict(current.id if current else None)})


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
@jwt_required
def delete_post(post_id):
    current = request.current_user
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'success': False, 'error': 'Post non trouve'}), 404
    if post.user_id != current.id:
        return jsonify({'success': False, 'error': 'Non autorise'}), 403

    Like.query.filter_by(post_id=post_id).delete()
    Comment.query.filter_by(post_id=post_id).delete()
    SavedPost.query.filter_by(post_id=post_id).delete()
    db.session.delete(post)
    current.post_count = max(0, current.post_count - 1)
    db.session.commit()
    return jsonify({'success': True})


# ══════════════════════════════════════════════════════════════
# LIKES API
# ══════════════════════════════════════════════════════════════

@app.route('/api/posts/<int:post_id>/like', methods=['POST'])
@jwt_required
def toggle_like(post_id):
    current = request.current_user
    data = request.get_json() or {}
    reaction = data.get('reaction', 'like')

    post = Post.query.get(post_id)
    if not post:
        return jsonify({'success': False, 'error': 'Post non trouve'}), 404

    existing = Like.query.filter_by(user_id=current.id, post_id=post_id).first()
    if existing:
        if existing.reaction_type == reaction:
            db.session.delete(existing)
            post.likes_count = max(0, post.likes_count - 1)
            db.session.commit()
            return jsonify({'success': True, 'liked': False, 'likes_count': post.likes_count})
        else:
            existing.reaction_type = reaction
            db.session.commit()
            return jsonify({'success': True, 'liked': True, 'reaction': reaction, 'likes_count': post.likes_count})
    else:
        like = Like(user_id=current.id, post_id=post_id, reaction_type=reaction)
        db.session.add(like)
        post.likes_count += 1
        if post.user_id != current.id:
            reactions_map = {'like': '❤️', 'love': '💕', 'support': '🙏', 'celebrate': '🎉', 'think': '🤔'}
            emoji = reactions_map.get(reaction, '❤️')
            create_notification(post.user_id, current.id, 'like',
                              f'{current.full_name} {emoji} votre publication')
        db.session.commit()
        return jsonify({'success': True, 'liked': True, 'reaction': reaction, 'likes_count': post.likes_count})


# ══════════════════════════════════════════════════════════════
# COMMENTS API
# ══════════════════════════════════════════════════════════════

@app.route('/api/posts/<int:post_id>/comments', methods=['GET'])
@jwt_optional
def get_comments(post_id):
    page = request.args.get('page', 1, type=int)
    comments = Comment.query.filter_by(post_id=post_id, parent_id=None)\
        .order_by(Comment.created_at.desc())\
        .paginate(page=page, per_page=20, error_out=False)

    return jsonify({
        'success': True,
        'comments': [c.to_dict() for c in comments.items],
        'has_next': comments.has_next
    })


@app.route('/api/posts/<int:post_id>/comments', methods=['POST'])
@jwt_required
def add_comment(post_id):
    current = request.current_user
    data = request.get_json() or {}
    content = sanitize_input(data.get('content', ''))

    if not content:
        return jsonify({'success': False, 'error': 'Contenu requis'}), 400

    post = Post.query.get(post_id)
    if not post:
        return jsonify({'success': False, 'error': 'Post non trouve'}), 404

    comment = Comment(
        user_id=current.id,
        post_id=post_id,
        parent_id=data.get('parent_id'),
        content=content,
        image_url=data.get('image_url', '')[:500]
    )
    db.session.add(comment)
    post.comments_count += 1

    if post.user_id != current.id:
        create_notification(post.user_id, current.id, 'comment',
                          f'{current.full_name} a commente votre publication')

    if data.get('parent_id'):
        parent = Comment.query.get(data['parent_id'])
        if parent and parent.user_id != current.id:
            create_notification(parent.user_id, current.id, 'comment',
                              f'{current.full_name} a repondu a votre commentaire')

    db.session.commit()
    return jsonify({'success': True, 'comment': comment.to_dict()}), 201


@app.route('/api/comments/<int:comment_id>/replies', methods=['GET'])
@jwt_optional
def get_replies(comment_id):
    replies = Comment.query.filter_by(parent_id=comment_id)\
        .order_by(Comment.created_at.asc()).all()
    return jsonify({'success': True, 'replies': [r.to_dict() for r in replies]})


# ══════════════════════════════════════════════════════════════
# SAVED POSTS API
# ══════════════════════════════════════════════════════════════

@app.route('/api/posts/<int:post_id>/save', methods=['POST'])
@jwt_required
def toggle_save(post_id):
    current = request.current_user
    existing = SavedPost.query.filter_by(user_id=current.id, post_id=post_id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({'success': True, 'saved': False})
    else:
        save = SavedPost(user_id=current.id, post_id=post_id)
        db.session.add(save)
        db.session.commit()
        return jsonify({'success': True, 'saved': True})


@app.route('/api/saved', methods=['GET'])
@jwt_required
def get_saved():
    current = request.current_user
    page = request.args.get('page', 1, type=int)
    saved = SavedPost.query.filter_by(user_id=current.id)\
        .order_by(SavedPost.created_at.desc())\
        .paginate(page=page, per_page=20, error_out=False)

    posts = []
    for s in saved.items:
        p = Post.query.get(s.post_id)
        if p:
            posts.append(p.to_dict(current.id))

    return jsonify({'success': True, 'posts': posts, 'has_next': saved.has_next})


# ══════════════════════════════════════════════════════════════
# GROUPS API
# ══════════════════════════════════════════════════════════════

@app.route('/api/groups', methods=['GET'])
@jwt_required
def get_groups():
    current = request.current_user
    category = request.args.get('category')
    q = request.args.get('q')

    query = Group.query
    if category:
        query = query.filter_by(category=category)
    if q:
        query = query.filter(Group.name.ilike(f'%{q}%'))

    groups = query.order_by(Group.member_count.desc()).all()
    return jsonify({'success': True, 'groups': [g.to_dict(current.id) for g in groups]})


@app.route('/api/groups', methods=['POST'])
@jwt_required
def create_group():
    current = request.current_user
    data = request.get_json() or {}
    name = sanitize_input(data.get('name', ''), 200)

    if not name:
        return jsonify({'success': False, 'error': 'Nom du groupe requis'}), 400

    group = Group(
        name=name,
        description=sanitize_input(data.get('description', ''), 1000),
        cover_photo=data.get('cover_photo', '')[:500],
        category=sanitize_input(data.get('category', ''), 100),
        country=sanitize_input(data.get('country', ''), 80),
        privacy=data.get('privacy', 'public'),
        creator_id=current.id,
        member_count=1
    )
    db.session.add(group)
    db.session.flush()

    member = GroupMember(group_id=group.id, user_id=current.id, role='admin')
    db.session.add(member)
    db.session.commit()

    return jsonify({'success': True, 'group': group.to_dict(current.id)}), 201


@app.route('/api/groups/<int:group_id>', methods=['GET'])
@jwt_required
def get_group(group_id):
    current = request.current_user
    group = Group.query.get(group_id)
    if not group:
        return jsonify({'success': False, 'error': 'Groupe non trouve'}), 404
    return jsonify({'success': True, 'group': group.to_dict(current.id)})


@app.route('/api/groups/<int:group_id>/join', methods=['POST'])
@jwt_required
def join_group(group_id):
    current = request.current_user
    group = Group.query.get(group_id)
    if not group:
        return jsonify({'success': False, 'error': 'Groupe non trouve'}), 404

    existing = GroupMember.query.filter_by(group_id=group_id, user_id=current.id).first()
    if existing:
        db.session.delete(existing)
        group.member_count = max(0, group.member_count - 1)
        db.session.commit()
        return jsonify({'success': True, 'joined': False, 'member_count': group.member_count})
    else:
        member = GroupMember(group_id=group_id, user_id=current.id, role='member')
        db.session.add(member)
        group.member_count += 1
        db.session.commit()
        return jsonify({'success': True, 'joined': True, 'member_count': group.member_count})


@app.route('/api/groups/<int:group_id>/posts', methods=['GET'])
@jwt_required
def get_group_posts(group_id):
    current = request.current_user
    page = request.args.get('page', 1, type=int)

    posts = Post.query.filter_by(group_id=group_id)\
        .order_by(Post.created_at.desc())\
        .paginate(page=page, per_page=20, error_out=False)

    return jsonify({
        'success': True,
        'posts': [p.to_dict(current.id) for p in posts.items],
        'has_next': posts.has_next
    })


@app.route('/api/groups/<int:group_id>/members', methods=['GET'])
@jwt_required
def get_group_members(group_id):
    members = GroupMember.query.filter_by(group_id=group_id)\
        .order_by(GroupMember.role.asc()).all()

    result = []
    for m in members:
        u = User.query.get(m.user_id)
        if u:
            d = u.to_dict()
            d['role'] = m.role
            d['joined_at'] = m.joined_at.isoformat() if m.joined_at else ''
            result.append(d)

    return jsonify({'success': True, 'members': result})


# ══════════════════════════════════════════════════════════════
# MESSAGES API
# ══════════════════════════════════════════════════════════════

@app.route('/api/conversations', methods=['GET'])
@jwt_required
def get_conversations():
    current = request.current_user

    # Get distinct conversation IDs
    convos = db.session.query(Message.conversation_id)\
        .filter(Message.conversation_id.like(f'conv_%'))\
        .filter(or_(
            Message.conversation_id.like(f'conv_{current.id}_%'),
            Message.conversation_id.like(f'conv_%_{current.id}')
        ))\
        .distinct().all()

    result = []
    for (conv_id,) in convos:
        parts = conv_id.split('_')
        if len(parts) == 3:
            other_id = int(parts[1]) if int(parts[2]) == current.id else int(parts[2])
            other_user = User.query.get(other_id)
            if not other_user:
                continue

            last_msg = Message.query.filter_by(conversation_id=conv_id)\
                .order_by(Message.created_at.desc()).first()

            unread = Message.query.filter_by(
                conversation_id=conv_id, is_read=False
            ).filter(Message.sender_id != current.id).count()

            result.append({
                'conversation_id': conv_id,
                'user': other_user.to_dict(),
                'last_message': {
                    'content': last_msg.content if last_msg else '',
                    'created_at': last_msg.created_at.isoformat() if last_msg else '',
                    'sender_id': last_msg.sender_id if last_msg else None,
                },
                'unread_count': unread
            })

    result.sort(key=lambda x: x['last_message']['created_at'], reverse=True)
    return jsonify({'success': True, 'conversations': result})


@app.route('/api/messages/<int:user_id>', methods=['GET'])
@jwt_required
def get_messages(user_id):
    current = request.current_user
    conv_id = get_conversation_id(current.id, user_id)
    page = request.args.get('page', 1, type=int)

    messages = Message.query.filter_by(conversation_id=conv_id)\
        .order_by(Message.created_at.desc())\
        .paginate(page=page, per_page=50, error_out=False)

    # Mark as read
    Message.query.filter_by(conversation_id=conv_id, is_read=False)\
        .filter(Message.sender_id != current.id)\
        .update({Message.is_read: True})
    db.session.commit()

    return jsonify({
        'success': True,
        'messages': [{
            'id': m.id,
            'sender_id': m.sender_id,
            'content': m.content,
            'image_url': m.image_url or '',
            'is_read': m.is_read,
            'created_at': m.created_at.isoformat()
        } for m in reversed(messages.items)],
        'has_next': messages.has_next
    })


@app.route('/api/messages/<int:user_id>', methods=['POST'])
@jwt_required
def send_message(user_id):
    current = request.current_user
    data = request.get_json() or {}
    content = sanitize_input(data.get('content', ''))

    if not content:
        return jsonify({'success': False, 'error': 'Message vide'}), 400

    target = User.query.get(user_id)
    if not target:
        return jsonify({'success': False, 'error': 'Utilisateur non trouve'}), 404

    # Check if blocked
    if Block.query.filter_by(blocker_id=user_id, blocked_id=current.id).first():
        return jsonify({'success': False, 'error': 'Impossible d\'envoyer ce message'}), 403

    conv_id = get_conversation_id(current.id, user_id)
    msg = Message(
        conversation_id=conv_id,
        sender_id=current.id,
        content=content,
        image_url=data.get('image_url', '')[:500]
    )
    db.session.add(msg)
    create_notification(user_id, current.id, 'message', f'{current.full_name} vous a envoye un message')
    db.session.commit()

    return jsonify({
        'success': True,
        'message': {
            'id': msg.id,
            'sender_id': msg.sender_id,
            'content': msg.content,
            'image_url': msg.image_url or '',
            'is_read': msg.is_read,
            'created_at': msg.created_at.isoformat()
        }
    }), 201


@app.route('/api/messages/unread-count', methods=['GET'])
@jwt_required
def unread_message_count():
    current = request.current_user
    count = Message.query.filter(
        Message.is_read == False,
        Message.sender_id != current.id,
        or_(
            Message.conversation_id.like(f'conv_{current.id}_%'),
            Message.conversation_id.like(f'conv_%_{current.id}')
        )
    ).count()
    return jsonify({'success': True, 'count': count})


# ══════════════════════════════════════════════════════════════
# NOTIFICATIONS API
# ══════════════════════════════════════════════════════════════

@app.route('/api/notifications', methods=['GET'])
@jwt_required
def get_notifications():
    current = request.current_user
    page = request.args.get('page', 1, type=int)

    notifs = Notification.query.filter_by(user_id=current.id)\
        .order_by(Notification.created_at.desc())\
        .paginate(page=page, per_page=30, error_out=False)

    return jsonify({
        'success': True,
        'notifications': [n.to_dict() for n in notifs.items],
        'has_next': notifs.has_next
    })


@app.route('/api/notifications/unread-count', methods=['GET'])
@jwt_required
def unread_notification_count():
    current = request.current_user
    count = Notification.query.filter_by(user_id=current.id, is_read=False).count()
    return jsonify({'success': True, 'count': count})


@app.route('/api/notifications/read', methods=['POST'])
@jwt_required
def mark_notifications_read():
    current = request.current_user
    data = request.get_json() or {}
    notif_id = data.get('id')

    if notif_id:
        notif = Notification.query.filter_by(id=notif_id, user_id=current.id).first()
        if notif:
            notif.is_read = True
    else:
        Notification.query.filter_by(user_id=current.id, is_read=False)\
            .update({Notification.is_read: True})

    db.session.commit()
    return jsonify({'success': True})


# ══════════════════════════════════════════════════════════════
# SEARCH API
# ══════════════════════════════════════════════════════════════

@app.route('/api/search', methods=['GET'])
@jwt_required
def search():
    current = request.current_user
    q = request.args.get('q', '').strip()
    search_type = request.args.get('type', 'all')

    if not q or len(q) < 2:
        return jsonify({'success': True, 'users': [], 'posts': [], 'groups': []})

    result = {'users': [], 'posts': [], 'groups': []}

    if search_type in ('all', 'users'):
        users = User.query.filter(
            or_(User.username.ilike(f'%{q}%'), User.full_name.ilike(f'%{q}%'))
        ).limit(10).all()
        result['users'] = [u.to_dict() for u in users]

    if search_type in ('all', 'posts'):
        posts = Post.query.filter(
            Post.content.ilike(f'%{q}%'),
            Post.visibility == 'public'
        ).order_by(Post.created_at.desc()).limit(20).all()
        result['posts'] = [p.to_dict(current.id) for p in posts]

    if search_type in ('all', 'groups'):
        groups = Group.query.filter(
            or_(Group.name.ilike(f'%{q}%'), Group.description.ilike(f'%{q}%'))
        ).limit(10).all()
        result['groups'] = [g.to_dict(current.id) for g in groups]

    return jsonify({'success': True, **result})


@app.route('/api/discover', methods=['GET'])
@jwt_required
def discover():
    current = request.current_user

    # Suggested users (not following yet)
    following_ids = [f.following_id for f in Follow.query.filter_by(follower_id=current.id).all()]
    following_ids.append(current.id)
    suggested_users = User.query.filter(
        ~User.id.in_(following_ids),
        User.is_active == True
    ).order_by(User.follower_count.desc()).limit(10).all()

    # Trending posts
    trending = Post.query.filter(
        Post.visibility == 'public',
        Post.created_at >= datetime.now(timezone.utc) - timedelta(days=7)
    ).order_by((Post.likes_count + Post.comments_count * 2).desc()).limit(20).all()

    # Suggested groups
    member_group_ids = [m.group_id for m in GroupMember.query.filter_by(user_id=current.id).all()]
    suggested_groups = Group.query.filter(
        ~Group.id.in_(member_group_ids) if member_group_ids else True
    ).order_by(Group.member_count.desc()).limit(10).all()

    # Trending hashtags
    all_posts = Post.query.filter(
        Post.created_at >= datetime.now(timezone.utc) - timedelta(days=7),
        Post.visibility == 'public'
    ).all()
    hashtag_counts = {}
    for p in all_posts:
        tags = re.findall(r'#(\w+)', p.content)
        for t in tags:
            hashtag_counts[t.lower()] = hashtag_counts.get(t.lower(), 0) + 1
    trending_hashtags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    return jsonify({
        'success': True,
        'suggested_users': [u.to_dict() for u in suggested_users],
        'trending_posts': [p.to_dict(current.id) for p in trending],
        'suggested_groups': [g.to_dict(current.id) for g in suggested_groups],
        'trending_hashtags': [{'tag': t, 'count': c} for t, c in trending_hashtags],
    })


# ══════════════════════════════════════════════════════════════
# BLOCK & REPORT API
# ══════════════════════════════════════════════════════════════

@app.route('/api/users/<int:user_id>/block', methods=['POST'])
@jwt_required
def toggle_block(user_id):
    current = request.current_user
    if current.id == user_id:
        return jsonify({'success': False, 'error': 'Action impossible'}), 400

    existing = Block.query.filter_by(blocker_id=current.id, blocked_id=user_id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({'success': True, 'blocked': False})
    else:
        block = Block(blocker_id=current.id, blocked_id=user_id)
        db.session.add(block)
        # Also unfollow
        Follow.query.filter_by(follower_id=current.id, following_id=user_id).delete()
        Follow.query.filter_by(follower_id=user_id, following_id=current.id).delete()
        db.session.commit()
        return jsonify({'success': True, 'blocked': True})


@app.route('/api/report', methods=['POST'])
@jwt_required
def report_content():
    current = request.current_user
    data = request.get_json() or {}

    report = Report(
        reporter_id=current.id,
        target_type=sanitize_input(data.get('target_type', ''), 20),
        target_id=data.get('target_id', 0),
        reason=sanitize_input(data.get('reason', ''), 100),
        details=sanitize_input(data.get('details', ''), 500)
    )
    db.session.add(report)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Signalement envoye. Merci.'})


# ══════════════════════════════════════════════════════════════
# CULTURAL CONTENT API
# ══════════════════════════════════════════════════════════════

@app.route('/api/proverb', methods=['GET'])
@jwt_optional
def get_proverb():
    day = datetime.now(timezone.utc).timetuple().tm_yday
    proverb = SAHEL_PROVERBS[day % len(SAHEL_PROVERBS)]
    return jsonify({'success': True, 'proverb': proverb})


@app.route('/api/events', methods=['GET'])
@jwt_optional
def get_events():
    country = request.args.get('country')
    events = CULTURAL_EVENTS
    if country:
        events = [e for e in events if e['country'] in (country, 'AES')]
    return jsonify({'success': True, 'events': events})


# ══════════════════════════════════════════════════════════════
# UPLOAD API (Cloudinary placeholder)
# ══════════════════════════════════════════════════════════════

@app.route('/api/upload', methods=['POST'])
@jwt_required
def upload_image():
    """Upload image - uses Cloudinary if configured, otherwise base64 data URI"""
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'Aucune image fournie'}), 400

    file = request.files['image']
    if not file.filename:
        return jsonify({'success': False, 'error': 'Fichier invalide'}), 400

    allowed = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in allowed:
        return jsonify({'success': False, 'error': 'Format non supporte. Utilisez PNG, JPG, GIF ou WebP'}), 400

    # Try Cloudinary
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
    api_key = os.environ.get('CLOUDINARY_API_KEY')
    api_secret = os.environ.get('CLOUDINARY_API_SECRET')

    if cloud_name and api_key and api_secret:
        try:
            import cloudinary
            import cloudinary.uploader
            cloudinary.config(cloud_name=cloud_name, api_key=api_key, api_secret=api_secret)
            result = cloudinary.uploader.upload(
                file,
                transformation=[
                    {'width': 1200, 'height': 1200, 'crop': 'limit'},
                    {'quality': 'auto:good'}
                ]
            )
            return jsonify({'success': True, 'url': result['secure_url']})
        except Exception as e:
            return jsonify({'success': False, 'error': f'Erreur upload: {str(e)}'}), 500

    # Fallback: base64 data URI
    import base64
    data = file.read()
    if len(data) > 5 * 1024 * 1024:
        return jsonify({'success': False, 'error': 'Image trop volumineuse (max 5MB)'}), 400
    mime = f"image/{ext}" if ext != 'jpg' else 'image/jpeg'
    b64 = base64.b64encode(data).decode()
    url = f"data:{mime};base64,{b64}"
    return jsonify({'success': True, 'url': url})


# ══════════════════════════════════════════════════════════════
# HEALTH & API INFO
# ══════════════════════════════════════════════════════════════

@app.route('/api/health', methods=['GET'])
def health():
    try:
        db.session.execute(text('SELECT 1'))
        db_ok = True
    except Exception:
        db_ok = False

    user_count = User.query.count()
    post_count = Post.query.count()

    return jsonify({
        'status': 'healthy' if db_ok else 'degraded',
        'service': 'AES Connect',
        'database': 'connected' if db_ok else 'error',
        'stats': {'users': user_count, 'posts': post_count},
        'motto': 'Notre voix, notre espace, notre Sahel'
    })


@app.route('/api/stats', methods=['GET'])
@jwt_optional
def get_stats():
    return jsonify({
        'success': True,
        'stats': {
            'total_users': User.query.count(),
            'total_posts': Post.query.count(),
            'total_groups': Group.query.count(),
            'active_today': User.query.filter(
                User.last_seen >= datetime.now(timezone.utc) - timedelta(days=1)
            ).count()
        }
    })


# ══════════════════════════════════════════════════════════════
# ERROR HANDLERS
# ══════════════════════════════════════════════════════════════

@app.errorhandler(404)
def not_found(e):
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'error': 'Endpoint non trouve'}), 404
    return render_template('index.html')

@app.errorhandler(500)
def server_error(e):
    return jsonify({'success': False, 'error': 'Erreur serveur interne'}), 500

@app.after_request
def add_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    if request.path.endswith('.js'):
        response.headers['Content-Type'] = 'application/javascript'
    return response


# ══════════════════════════════════════════════════════════════
# INITIALIZATION
# ══════════════════════════════════════════════════════════════

def seed_data():
    """Create default groups if they don't exist"""
    for gdata in DEFAULT_GROUPS:
        if not Group.query.filter_by(name=gdata['name']).first():
            group = Group(
                name=gdata['name'],
                description=gdata['description'],
                category=gdata['category'],
                country=gdata['country'],
                privacy='public',
                creator_id=1,
                member_count=0
            )
            db.session.add(group)
    db.session.commit()

with app.app_context():
    db.create_all()
    try:
        seed_data()
    except Exception:
        pass
    print("AES Connect ready!")


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
