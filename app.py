from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import sqlite3
import os
import secrets

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
CORS(app, supports_credentials=True)

# Database initialization
def init_db():
    """Initialize SQLite database with all required tables"""
    conn = sqlite3.connect('social_network.db')
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
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect('social_network.db')
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

# Routes
@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

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
        
        if not all([username, email, password, full_name]):
            return jsonify({'success': False, 'error': 'Tous les champs sont requis'}), 400
        
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
            'INSERT INTO users (username, email, password_hash, full_name) VALUES (?, ?, ?, ?)',
            (username, email, password_hash, full_name)
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
            'user': {'id': user_id, 'username': username, 'full_name': full_name}
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
        conn = get_db_connection()
        user = conn.execute(
            'SELECT id, username, email, full_name, bio, avatar_url, created_at FROM users WHERE id = ?',
            (session['user_id'],)
        ).fetchone()
        conn.close()
        
        if user:
            return jsonify({
                'success': True,
                'user': dict(user)
            })
        else:
            return jsonify({'success': False, 'error': 'Utilisateur non trouvé'}), 404
    
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
        
        if not content:
            return jsonify({'success': False, 'error': 'Le contenu est requis'}), 400
        
        conn = get_db_connection()
        cursor = conn.execute(
            'INSERT INTO posts (user_id, content) VALUES (?, ?)',
            (session['user_id'], content)
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
        
        if not content:
            return jsonify({'success': False, 'error': 'Le contenu du commentaire est requis'}), 400
        
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
            SELECT id, username, full_name, avatar_url
            FROM users
            WHERE username LIKE ? OR full_name LIKE ?
            AND id != ?
            LIMIT 20
        ''', (f'%{query}%', f'%{query}%', session['user_id'])).fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'users': [dict(user) for user in users]
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Social Network API'
    })

if __name__ == '__main__':
    init_db()  # Initialize database on startup
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)