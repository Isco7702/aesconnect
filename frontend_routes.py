"""
Routes de compatibilité pour le frontend
Ces routes permettent au frontend d'utiliser des URLs simples comme /login, /posts, etc.
"""
from flask import request, jsonify, session, current_app
from models import db, User, Post, Group, Message, Like, Comment, GroupMember, Notification
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import or_, and_
from datetime import datetime

def require_login(f):
    """Decorator to require user login"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def register_frontend_routes(app):
    """Register all frontend compatibility routes"""
    
    # AUTH ROUTES
    @app.route('/login', methods=['POST'])
    def login():
        """Login route"""
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'error': 'Username and password required'})
        
        user = User.query.filter(
            or_(User.username == username, User.email == username)
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
    
    @app.route('/register', methods=['POST'])
    def register():
        """Register route"""
        data = request.get_json()
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        full_name = data.get('full_name')
        
        if not all([username, email, password, full_name]):
            return jsonify({'success': False, 'error': 'All fields are required'})
        
        # Check if user exists
        existing_user = User.query.filter(
            or_(User.username == username, User.email == email)
        ).first()
        
        if existing_user:
            return jsonify({'success': False, 'error': 'Username or email already exists'})
        
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
    
    @app.route('/logout', methods=['POST'])
    def logout():
        """Logout route"""
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
        return jsonify({'success': False, 'error': 'User not found'})
    
    # POSTS ROUTES
    @app.route('/posts', methods=['GET', 'POST'])
    @require_login
    def posts():
        """Get all posts or create a new post"""
        if request.method == 'GET':
            # Get all posts
            posts = db.session.query(
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
            } for post in posts]
            
            return jsonify({'success': True, 'posts': posts_list})
        
        elif request.method == 'POST':
            # Create new post
            data = request.get_json()
            content = data.get('content')
            
            if not content:
                return jsonify({'success': False, 'error': 'Content required'})
            
            new_post = Post(
                content=content,
                author_id=session['user_id'],
                image_url=data.get('image_url', '')
            )
            
            db.session.add(new_post)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Post created', 'post_id': new_post.id})
    
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
    
    # GROUPS ROUTES
    @app.route('/groups', methods=['GET', 'POST'])
    @require_login
    def groups():
        """Get all groups or create a new group"""
        if request.method == 'GET':
            # Get all groups
            groups = db.session.query(
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
            } for group in groups]
            
            return jsonify({'success': True, 'groups': groups_list})
        
        elif request.method == 'POST':
            # Create new group
            data = request.get_json()
            name = data.get('name')
            
            if not name:
                return jsonify({'success': False, 'error': 'Group name required'})
            
            new_group = Group(
                name=name,
                description=data.get('description', ''),
                is_private=data.get('is_private', False),
                created_by=session['user_id']
            )
            
            db.session.add(new_group)
            db.session.commit()
            
            # Add creator as member
            member = GroupMember(
                group_id=new_group.id,
                user_id=session['user_id'],
                role='admin'
            )
            db.session.add(member)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Group created', 'group_id': new_group.id})
    
    # MESSAGES ROUTES
    @app.route('/messages', methods=['GET', 'POST'])
    @require_login
    def messages():
        """Get all messages or send a new message"""
        if request.method == 'GET':
            # Get all messages for current user
            messages = db.session.query(
                Message,
                User.full_name.label('sender_name'),
                db.func.max(
                    db.case(
                        (User.id == Message.receiver_id, User.full_name),
                        else_=None
                    )
                ).label('receiver_name')
            ).join(User, Message.sender_id == User.id)\
            .filter(
                or_(
                    Message.sender_id == session['user_id'],
                    Message.receiver_id == session['user_id']
                )
            ).group_by(Message.id)\
            .order_by(Message.created_at.desc())\
            .all()
            
            # Get receiver names
            messages_list = []
            for msg in messages:
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
                return jsonify({'success': False, 'error': 'Receiver and content required'})
            
            new_message = Message(
                sender_id=session['user_id'],
                receiver_id=receiver_id,
                content=content
            )
            
            db.session.add(new_message)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Message sent', 'message_id': new_message.id})
    
    # USERS ROUTES
    @app.route('/users/search', methods=['GET'])
    @require_login
    def search_users():
        """Search users"""
        query = request.args.get('q', '')
        
        if not query:
            return jsonify({'success': True, 'users': []})
        
        users = User.query.filter(
            or_(
                User.username.like(f'%{query}%'),
                User.full_name.like(f'%{query}%')
            )
        ).filter(User.id != session['user_id']).limit(10).all()
        
        users_list = [{
            'id': user.id,
            'username': user.username,
            'full_name': user.full_name,
            'avatar_url': user.avatar_url
        } for user in users]
        
        return jsonify({'success': True, 'users': users_list})
