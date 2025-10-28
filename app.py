from flask import Flask, request, jsonify, render_template, session, redirect, url_for, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import sqlite3
import os
import secrets
import html
import re

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
CORS(app, supports_credentials=True)

# Database configuration
DATABASE_PATH = os.environ.get('DATABASE_PATH', 
    '/opt/render/project/src/social_network.db' if os.environ.get('RENDER') else './social_network.db')

# Database initialization
def init_db():
    """Initialize SQLite database with all required tables"""
    # Ensure directory exists
    db_dir = os.path.dirname(DATABASE_PATH)
    if db_dir and not os.path.exists(db_dir):
        try:
            os.makedirs(db_dir, exist_ok=True)
        except PermissionError as e:
            print(f"Warning: Cannot create directory {db_dir}: {e}")
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            bio TEXT DEFAULT '',
            avatar_url TEXT DEFAULT '',
            country TEXT DEFAULT '',
            city TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Posts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            image_url TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            likes_count INTEGER DEFAULT 0,
            comments_count INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Comments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Likes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(post_id, user_id),
            FOREIGN KEY (post_id) REFERENCES posts (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Groups table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            creator_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_private BOOLEAN DEFAULT 0,
            members_count INTEGER DEFAULT 1,
            FOREIGN KEY (creator_id) REFERENCES users (id)
        )
    ''')
    
    # Group members table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS group_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_admin BOOLEAN DEFAULT 0,
            UNIQUE(group_id, user_id),
            FOREIGN KEY (group_id) REFERENCES groups (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_read BOOLEAN DEFAULT 0,
            FOREIGN KEY (sender_id) REFERENCES users (id),
            FOREIGN KEY (receiver_id) REFERENCES users (id)
        )
    ''')
    
    # Friendships table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS friendships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user1_id INTEGER NOT NULL,
            user2_id INTEGER NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user1_id, user2_id),
            FOREIGN KEY (user1_id) REFERENCES users (id),
            FOREIGN KEY (user2_id) REFERENCES users (id)
        )
    ''')
    
    # Reports table for moderation
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reporter_id INTEGER NOT NULL,
            reported_user_id INTEGER,
            reported_post_id INTEGER,
            reason TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (reporter_id) REFERENCES users (id),
            FOREIGN KEY (reported_user_id) REFERENCES users (id),
            FOREIGN KEY (reported_post_id) REFERENCES posts (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def require_login(f):
    """Decorator to require user login"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def sanitize_html(text):
    """Sanitize HTML to prevent XSS attacks"""
    if not text:
        return text
    # Escape HTML characters
    text = html.escape(text)
    return text

def validate_text_length(text, min_len=1, max_len=5000):
    """Validate text length"""
    if not text or len(text.strip()) < min_len:
        return False, f'Le texte doit contenir au moins {min_len} caractère(s)'
    if len(text) > max_len:
        return False, f'Le texte ne peut pas dépasser {max_len} caractères'
    return True, None

def is_safe_url(url):
    """Check if URL is safe"""
    if not url:
        return True
    # Only allow http and https protocols
    allowed_protocols = ['http://', 'https://']
    return any(url.startswith(protocol) for protocol in allowed_protocols)

# Initialize database on startup
try:
    init_db()
    print("Database initialized successfully")
    
    # Verify tables exist
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    table_names = [table[0] for table in tables]
    print(f"Tables created: {table_names}")
    
    # Check if users table exists and has expected structure
    cursor.execute("PRAGMA table_info(users);")
    columns = cursor.fetchall()
    print(f"Users table columns: {[col[1] for col in columns]}")
    conn.close()
    
except Exception as e:
    print(f"Warning: Database initialization failed: {e}")
    import traceback
    traceback.print_exc()

# Routes
@app.route('/')
def index():
    """Serve the main page - landing or app"""
    # Check if user is logged in
    if 'user_id' in session:
        return render_template('index.html')
    else:
        return render_template('landing.html')

@app.route('/app')
def app_page():
    """Serve the app page for logged in users"""
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    """Serve favicon"""
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.svg', mimetype='image/svg+xml')

@app.route('/manifest.json')
def manifest():
    """Serve PWA manifest"""
    return send_from_directory(os.path.join(app.root_path, 'static'), 'manifest.json', mimetype='application/json')

# Authentication routes
@app.route('/register', methods=['POST'])
def register():
    """User registration"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        full_name = data.get('full_name', '').strip()
        country = data.get('country', '').strip()
        city = data.get('city', '').strip()
        avatar_url = data.get('avatar_url', '').strip()
        
        if not all([username, email, password, full_name]):
            return jsonify({'success': False, 'error': 'Tous les champs obligatoires sont requis'}), 400
        
        if len(password) < 6:
            return jsonify({'success': False, 'error': 'Le mot de passe doit contenir au moins 6 caractères'}), 400
        
        conn = get_db_connection()
        
        # Check if username or email already exists
        existing = conn.execute(
            'SELECT id FROM users WHERE username = ? OR email = ?',
            (username, email)
        ).fetchone()
        
        if existing:
            conn.close()
            return jsonify({'success': False, 'error': 'Nom d\'utilisateur ou email déjà utilisé'}), 400
        
        # Create new user
        password_hash = generate_password_hash(password)
        cursor = conn.execute(
            'INSERT INTO users (username, email, password_hash, full_name, country, city, avatar_url) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (username, email, password_hash, full_name, country, city, avatar_url)
        )
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Log in the user
        session['user_id'] = user_id
        session['username'] = username
        
        return jsonify({
            'success': True,
            'message': 'Compte créé avec succès',
            'user': {'id': user_id, 'username': username, 'full_name': full_name, 'country': country, 'city': city}
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'success': False, 'error': 'Nom d\'utilisateur et mot de passe requis'}), 400
        
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ? OR email = ?',
            (username, username)
        ).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            
            return jsonify({
                'success': True,
                'message': 'Connexion réussie',
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'full_name': user['full_name'],
                    'email': user['email'],
                    'bio': user['bio']
                }
            })
        else:
            return jsonify({'success': False, 'error': 'Nom d\'utilisateur ou mot de passe incorrect'}), 401
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/logout', methods=['POST'])
def logout():
    """User logout"""
    session.clear()
    return jsonify({'success': True, 'message': 'Déconnexion réussie'})

@app.route('/profile', methods=['GET'])
@require_login
def get_profile():
    """Get user profile"""
    try:
        user_id = request.args.get('user_id', session['user_id'])
        
        conn = get_db_connection()
        user = conn.execute(
            'SELECT id, username, email, full_name, bio, avatar_url, country, city, created_at FROM users WHERE id = ?',
            (user_id,)
        ).fetchone()
        
        if not user:
            conn.close()
            return jsonify({'success': False, 'error': 'Utilisateur non trouvé'}), 404
        
        # Get user stats
        posts_count = conn.execute('SELECT COUNT(*) as count FROM posts WHERE user_id = ?', (user_id,)).fetchone()['count']
        
        followers_count = conn.execute('''
            SELECT COUNT(*) as count FROM friendships 
            WHERE user2_id = ? AND status = 'accepted'
        ''', (user_id,)).fetchone()['count']
        
        following_count = conn.execute('''
            SELECT COUNT(*) as count FROM friendships 
            WHERE user1_id = ? AND status = 'accepted'
        ''', (user_id,)).fetchone()['count']
        
        conn.close()
        
        user_data = dict(user)
        user_data['posts_count'] = posts_count
        user_data['followers_count'] = followers_count
        user_data['following_count'] = following_count
        user_data['is_own_profile'] = (int(user_id) == session['user_id'])
        
        return jsonify({
            'success': True,
            'user': user_data
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/profile', methods=['PUT'])
@require_login
def update_profile():
    """Update user profile"""
    try:
        data = request.get_json()
        
        # Champs autorisés à être modifiés
        allowed_fields = ['full_name', 'bio', 'avatar_url', 'country', 'city']
        updates = {}
        
        for field in allowed_fields:
            if field in data:
                updates[field] = data[field]
        
        if not updates:
            return jsonify({'success': False, 'error': 'Aucune donnée à mettre à jour'}), 400
        
        # Construire la requête SQL dynamiquement
        set_clause = ', '.join([f'{field} = ?' for field in updates.keys()])
        values = list(updates.values())
        values.append(session['user_id'])
        
        conn = get_db_connection()
        conn.execute(
            f'UPDATE users SET {set_clause} WHERE id = ?',
            values
        )
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Profil mis à jour avec succès'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Posts routes
@app.route('/posts', methods=['GET'])
@require_login
def get_posts():
    """Get all posts (feed)"""
    try:
        conn = get_db_connection()
        posts = conn.execute('''
            SELECT p.*, u.username, u.full_name, u.avatar_url,
                   (SELECT COUNT(*) FROM likes WHERE post_id = p.id) as likes_count,
                   (SELECT COUNT(*) FROM comments WHERE post_id = p.id) as comments_count,
                   (SELECT COUNT(*) FROM likes WHERE post_id = p.id AND user_id = ?) as user_liked
            FROM posts p
            JOIN users u ON p.user_id = u.id
            ORDER BY p.created_at DESC
            LIMIT 50
        ''', (session['user_id'],)).fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'posts': [dict(post) for post in posts]
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/posts', methods=['POST'])
@require_login
def create_post():
    """Create a new post"""
    try:
        data = request.get_json()
        content = data.get('content', '').strip()
        image_url = data.get('image_url', '').strip()
        
        # Validate content
        is_valid, error_msg = validate_text_length(content, min_len=1, max_len=5000)
        if not is_valid:
            return jsonify({'success': False, 'error': error_msg}), 400
        
        # Sanitize content to prevent XSS
        content = sanitize_html(content)
        
        # Validate image URL if provided
        if image_url and not is_safe_url(image_url):
            return jsonify({'success': False, 'error': 'URL d\'image invalide'}), 400
        
        conn = get_db_connection()
        cursor = conn.execute(
            'INSERT INTO posts (user_id, content, image_url) VALUES (?, ?, ?)',
            (session['user_id'], content, image_url)
        )
        post_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Post créé avec succès',
            'post_id': post_id
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/posts/<int:post_id>/like', methods=['POST'])
@require_login
def toggle_like(post_id):
    """Toggle like on a post"""
    try:
        conn = get_db_connection()
        
        # Check if already liked
        existing_like = conn.execute(
            'SELECT id FROM likes WHERE post_id = ? AND user_id = ?',
            (post_id, session['user_id'])
        ).fetchone()
        
        if existing_like:
            # Unlike
            conn.execute(
                'DELETE FROM likes WHERE post_id = ? AND user_id = ?',
                (post_id, session['user_id'])
            )
            liked = False
        else:
            # Like
            conn.execute(
                'INSERT INTO likes (post_id, user_id) VALUES (?, ?)',
                (post_id, session['user_id'])
            )
            liked = True
        
        conn.commit()
        
        # Get updated like count
        like_count = conn.execute(
            'SELECT COUNT(*) as count FROM likes WHERE post_id = ?',
            (post_id,)
        ).fetchone()['count']
        
        conn.close()
        
        return jsonify({
            'success': True,
            'liked': liked,
            'likes_count': like_count
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/posts/<int:post_id>/comments', methods=['GET'])
@require_login
def get_comments(post_id):
    """Get comments for a post"""
    try:
        conn = get_db_connection()
        comments = conn.execute('''
            SELECT c.*, u.username, u.full_name, u.avatar_url
            FROM comments c
            JOIN users u ON c.user_id = u.id
            WHERE c.post_id = ?
            ORDER BY c.created_at ASC
        ''', (post_id,)).fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'comments': [dict(comment) for comment in comments]
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/posts/<int:post_id>/comments', methods=['POST'])
@require_login
def add_comment(post_id):
    """Add a comment to a post"""
    try:
        data = request.get_json()
        content = data.get('content', '').strip()
        
        # Validate content
        is_valid, error_msg = validate_text_length(content, min_len=1, max_len=1000)
        if not is_valid:
            return jsonify({'success': False, 'error': error_msg}), 400
        
        # Sanitize content to prevent XSS
        content = sanitize_html(content)
        
        conn = get_db_connection()
        cursor = conn.execute(
            'INSERT INTO comments (post_id, user_id, content) VALUES (?, ?, ?)',
            (post_id, session['user_id'], content)
        )
        comment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Commentaire ajouté',
            'comment_id': comment_id
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Groups routes
@app.route('/groups', methods=['GET'])
@require_login
def get_groups():
    """Get all groups"""
    try:
        conn = get_db_connection()
        groups = conn.execute('''
            SELECT g.*, u.username as creator_username,
                   (SELECT COUNT(*) FROM group_members WHERE group_id = g.id) as members_count,
                   (SELECT COUNT(*) FROM group_members WHERE group_id = g.id AND user_id = ?) as is_member
            FROM groups g
            JOIN users u ON g.creator_id = u.id
            ORDER BY g.created_at DESC
        ''', (session['user_id'],)).fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'groups': [dict(group) for group in groups]
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/groups', methods=['POST'])
@require_login
def create_group():
    """Create a new group"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        is_private = data.get('is_private', False)
        
        if not name:
            return jsonify({'success': False, 'error': 'Le nom du groupe est requis'}), 400
        
        conn = get_db_connection()
        cursor = conn.execute(
            'INSERT INTO groups (name, description, creator_id, is_private) VALUES (?, ?, ?, ?)',
            (name, description, session['user_id'], is_private)
        )
        group_id = cursor.lastrowid
        
        # Add creator as admin member
        conn.execute(
            'INSERT INTO group_members (group_id, user_id, is_admin) VALUES (?, ?, 1)',
            (group_id, session['user_id'])
        )
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Groupe créé avec succès',
            'group_id': group_id
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Messages routes
@app.route('/messages', methods=['GET'])
@require_login
def get_messages():
    """Get user's messages"""
    try:
        conn = get_db_connection()
        messages = conn.execute('''
            SELECT m.*, 
                   u1.username as sender_username, u1.full_name as sender_name,
                   u2.username as receiver_username, u2.full_name as receiver_name
            FROM messages m
            JOIN users u1 ON m.sender_id = u1.id
            JOIN users u2 ON m.receiver_id = u2.id
            WHERE m.sender_id = ? OR m.receiver_id = ?
            ORDER BY m.created_at DESC
            LIMIT 50
        ''', (session['user_id'], session['user_id'])).fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'messages': [dict(message) for message in messages]
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/messages', methods=['POST'])
@require_login
def send_message():
    """Send a message"""
    try:
        data = request.get_json()
        receiver_id = data.get('receiver_id')
        content = data.get('content', '').strip()
        
        if not receiver_id or not content:
            return jsonify({'success': False, 'error': 'Destinataire et contenu requis'}), 400
        
        conn = get_db_connection()
        cursor = conn.execute(
            'INSERT INTO messages (sender_id, receiver_id, content) VALUES (?, ?, ?)',
            (session['user_id'], receiver_id, content)
        )
        message_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Message envoyé',
            'message_id': message_id
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/users/search', methods=['GET'])
@require_login
def search_users():
    """Search users"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'success': True, 'users': []})
        
        conn = get_db_connection()
        users = conn.execute('''
            SELECT id, username, full_name, avatar_url, country, city
            FROM users
            WHERE (username LIKE ? OR full_name LIKE ? OR country LIKE ? OR city LIKE ?)
            AND id != ?
            LIMIT 20
        ''', (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%', session['user_id'])).fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'users': [dict(user) for user in users]
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/search', methods=['GET'])
@require_login
def global_search():
    """Global search for users, posts, and groups"""
    try:
        query = request.args.get('q', '').strip()
        search_type = request.args.get('type', 'all')
        
        if not query:
            return jsonify({
                'success': True,
                'users': [],
                'posts': [],
                'groups': []
            })
        
        conn = get_db_connection()
        results = {
            'success': True,
            'users': [],
            'posts': [],
            'groups': []
        }
        
        # Search users
        if search_type in ['all', 'users']:
            users = conn.execute('''
                SELECT id, username, full_name, avatar_url, country, city, bio
                FROM users
                WHERE (username LIKE ? OR full_name LIKE ? OR country LIKE ? OR city LIKE ?)
                AND id != ?
                LIMIT 10
            ''', (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%', session['user_id'])).fetchall()
            results['users'] = [dict(user) for user in users]
        
        # Search posts
        if search_type in ['all', 'posts']:
            posts = conn.execute('''
                SELECT p.*, u.username, u.full_name, u.avatar_url
                FROM posts p
                JOIN users u ON p.user_id = u.id
                WHERE p.content LIKE ?
                ORDER BY p.created_at DESC
                LIMIT 10
            ''', (f'%{query}%',)).fetchall()
            results['posts'] = [dict(post) for post in posts]
        
        # Search groups
        if search_type in ['all', 'groups']:
            groups = conn.execute('''
                SELECT g.*, u.username as creator_username,
                       (SELECT COUNT(*) FROM group_members WHERE group_id = g.id) as members_count
                FROM groups g
                JOIN users u ON g.creator_id = u.id
                WHERE g.name LIKE ? OR g.description LIKE ?
                LIMIT 10
            ''', (f'%{query}%', f'%{query}%')).fetchall()
            results['groups'] = [dict(group) for group in groups]
        
        conn.close()
        
        return jsonify(results)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/report', methods=['POST'])
@require_login
def report_content():
    """Report inappropriate content or user"""
    try:
        data = request.get_json()
        reported_user_id = data.get('reported_user_id')
        reported_post_id = data.get('reported_post_id')
        reason = data.get('reason', '').strip()
        
        if not reason:
            return jsonify({'success': False, 'error': 'Raison du signalement requise'}), 400
        
        if not reported_user_id and not reported_post_id:
            return jsonify({'success': False, 'error': 'Vous devez signaler un utilisateur ou un post'}), 400
        
        conn = get_db_connection()
        cursor = conn.execute(
            'INSERT INTO reports (reporter_id, reported_user_id, reported_post_id, reason) VALUES (?, ?, ?, ?)',
            (session['user_id'], reported_user_id, reported_post_id, reason)
        )
        report_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Signalement envoyé à la modération',
            'report_id': report_id
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/charter')
def get_charter():
    """Get the charter document"""
    try:
        with open('CHARTE_UTILISATION.md', 'r', encoding='utf-8') as f:
            content = f.read()
        return jsonify({'success': True, 'content': content})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        conn = get_db_connection()
        conn.execute('SELECT 1')
        conn.close()
        db_status = 'connected'
    except Exception as e:
        db_status = f'error: {str(e)}'
    
    return jsonify({
        'status': 'healthy',
        'service': 'Social Network API',
        'database': db_status
    })

@app.route('/init-db', methods=['POST'])
def init_database():
    """Initialize database manually"""
    try:
        init_db()
        return jsonify({
            'success': True,
            'message': 'Database initialized successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Database initialization failed: {str(e)}'
        }), 500

@app.route('/users/<int:user_id>/block', methods=['POST'])
@require_login
def block_user(user_id):
    """Block a user"""
    try:
        if user_id == session['user_id']:
            return jsonify({'success': False, 'error': 'Vous ne pouvez pas vous bloquer vous-même'}), 400
        
        conn = get_db_connection()
        
        # Check if already blocked
        existing = conn.execute('''
            SELECT id FROM friendships 
            WHERE user1_id = ? AND user2_id = ? AND status = 'blocked'
        ''', (session['user_id'], user_id)).fetchone()
        
        if existing:
            conn.close()
            return jsonify({'success': False, 'error': 'Utilisateur déjà bloqué'}), 400
        
        # Delete existing friendship if any
        conn.execute('''
            DELETE FROM friendships 
            WHERE (user1_id = ? AND user2_id = ?) OR (user1_id = ? AND user2_id = ?)
        ''', (session['user_id'], user_id, user_id, session['user_id']))
        
        # Add block record
        conn.execute('''
            INSERT INTO friendships (user1_id, user2_id, status) 
            VALUES (?, ?, 'blocked')
        ''', (session['user_id'], user_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Utilisateur bloqué avec succès'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/users/<int:user_id>/unblock', methods=['POST'])
@require_login
def unblock_user(user_id):
    """Unblock a user"""
    try:
        conn = get_db_connection()
        
        conn.execute('''
            DELETE FROM friendships 
            WHERE user1_id = ? AND user2_id = ? AND status = 'blocked'
        ''', (session['user_id'], user_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Utilisateur débloqué avec succès'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/users/<int:user_id>/follow', methods=['POST'])
@require_login
def follow_user(user_id):
    """Follow/Unfollow a user"""
    try:
        if user_id == session['user_id']:
            return jsonify({'success': False, 'error': 'Vous ne pouvez pas vous suivre vous-même'}), 400
        
        conn = get_db_connection()
        
        # Check if already following
        existing = conn.execute('''
            SELECT id, status FROM friendships 
            WHERE user1_id = ? AND user2_id = ?
        ''', (session['user_id'], user_id)).fetchone()
        
        if existing:
            if existing['status'] == 'accepted':
                # Unfollow
                conn.execute('''
                    DELETE FROM friendships 
                    WHERE user1_id = ? AND user2_id = ?
                ''', (session['user_id'], user_id))
                conn.commit()
                conn.close()
                return jsonify({
                    'success': True,
                    'following': False,
                    'message': 'Vous ne suivez plus cet utilisateur'
                })
        
        # Follow
        if existing:
            conn.execute('''
                UPDATE friendships SET status = 'accepted'
                WHERE user1_id = ? AND user2_id = ?
            ''', (session['user_id'], user_id))
        else:
            conn.execute('''
                INSERT INTO friendships (user1_id, user2_id, status) 
                VALUES (?, ?, 'accepted')
            ''', (session['user_id'], user_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'following': True,
            'message': 'Vous suivez maintenant cet utilisateur'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    init_db()  # Initialize database on startup
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)