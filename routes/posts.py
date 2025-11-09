from flask_smorest import Blueprint, abort
from flask import request, jsonify, session, current_app
from utils.notifications import create_notification
from models import db, Post, User, Like, Comment
# # from database import get_raw_db_connection # Fonctions SQLite brutes (obsolète) (obsolète)
from routes.auth import require_login # Décorateur d'authentification

posts_bp = Blueprint('posts', __name__, url_prefix='/posts')

# Posts routes
@posts_bp.route('/posts', methods=['GET'])
@require_login
def get_posts():
    """Get all posts (feed)"""
    try:
        user_id = session['user_id']
        
        # Sous-requête pour compter les likes
        likes_count_subquery = db.session.query(
            Like.post_id,
            db.func.count(Like.id).label('likes_count')
        ).group_by(Like.post_id).subquery()

        # Sous-requête pour compter les commentaires
        comments_count_subquery = db.session.query(
            Comment.post_id,
            db.func.count(Comment.id).label('comments_count')
        ).group_by(Comment.post_id).subquery()

        # Sous-requête pour vérifier si l'utilisateur a aimé
        user_liked_subquery = db.session.query(
            Like.post_id,
            db.literal(1).label('user_liked')
        ).filter(Like.user_id == user_id).subquery()

        # Requête principale
        posts_query = db.session.query(
            Post,
            User.username,
            User.full_name,
            User.avatar_url,
            db.func.coalesce(likes_count_subquery.c.likes_count, 0).label('likes_count'),
            db.func.coalesce(comments_count_subquery.c.comments_count, 0).label('comments_count'),
            db.func.coalesce(user_liked_subquery.c.user_liked, 0).label('user_liked')
        ).join(User, Post.user_id == User.id
        ).outerjoin(likes_count_subquery, Post.id == likes_count_subquery.c.post_id
        ).outerjoin(comments_count_subquery, Post.id == comments_count_subquery.c.post_id
        ).outerjoin(user_liked_subquery, Post.id == user_liked_subquery.c.post_id
        ).order_by(Post.created_at.desc()).limit(50).all()

        # Formater les résultats
        posts_list = []
        for post, username, full_name, avatar_url, likes_count, comments_count, user_liked in posts_query:
            post_dict = post.to_dict()
            post_dict.update({
                'username': username,
                'full_name': full_name,
                'avatar_url': avatar_url,
                'likes_count': likes_count,
                'comments_count': comments_count,
                'user_liked': bool(user_liked)
            })
            posts_list.append(post_dict)
        
        return jsonify({
            'success': True,
            'posts': posts_list
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@posts_bp.route('/posts', methods=['POST'])
@require_login
def create_post():
    """Create a new post with optional image upload"""
    try:
        content = request.form.get('content', '').strip()
        image_file = request.files.get('image')
        image_url = None

        if not content and not image_file:
            abort(400, message='Le contenu ou une image est requis')
        
        if image_file:
            # Upload vers Cloudinary
            upload_result = upload(image_file, folder="aesconnect_posts")
            image_url = upload_result.get('secure_url')
            
            if not image_url:
                abort(500, message="Échec de l'upload de l'image")        
        new_post = Post(
            user_id=session['user_id'],
            content=content,
            image_url=image_url
        )
        
        db.session.add(new_post)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Post créé avec succès',
            'post_id': new_post.id,
            'image_url': image_url
        })
    
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la création du post: {e}")
        db.session.rollback()
        abort(500, message=str(e))

@posts_bp.route('/posts/<int:post_id>/like', methods=['POST'])
@require_login
def toggle_like(post_id):
    """Toggle like on a post"""
    try:
        user_id = session['user_id']
        
        # Récupérer le post
        post = Post.query.get(post_id)
        if not post:
            abort(404, message="Post non trouvé")
            
        # Check if already liked
        existing_like = Like.query.filter_by(post_id=post_id, user_id=user_id).first()
        
        if existing_like:
            # Unlike
            db.session.delete(existing_like)
            post.likes_count -= 1
            liked = False
        else:
            # Like
            new_like = Like(post_id=post_id, user_id=user_id)
            db.session.add(new_like)
            post.likes_count += 1
            liked = True
            
            # --- Création de la notification ---
            if post.user_id != session['user_id']:
                message = f"@{session['username']} a aimé votre post."
                create_notification(
                    user_id=post.user_id,
                    message=message,
                    entity_type='post',
                    entity_id=post.id
                )
            # --- Fin de la création de la notification ---
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'liked': liked,
            'likes_count': post.likes_count
        })
    
    except Exception as e:
        current_app.logger.error(f"Erreur lors du like/unlike: {e}")
        db.session.rollback()
        abort(500, message=str(e))

@posts_bp.route('/posts/<int:post_id>/comments', methods=['GET'])
@require_login
def get_comments(post_id):
    """Get comments for a post"""
    try:
        comments = db.session.query(
            Comment,
            User.username,
            User.full_name,
            User.avatar_url
        ).join(User, Comment.user_id == User.id
        ).filter(Comment.post_id == post_id
        ).order_by(Comment.created_at.asc()).all()
        
        comments_list = []
        for comment, username, full_name, avatar_url in comments:
            comment_dict = comment.to_dict()
            comment_dict.update({
                'username': username,
                'full_name': full_name,
                'avatar_url': avatar_url
            })
            comments_list.append(comment_dict)
        
        return jsonify({
            'success': True,
            'comments': comments_list
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@posts_bp.route('/posts/<int:post_id>/comments', methods=['POST'])
@require_login
def add_comment(post_id):
    """Add a comment to a post"""
    try:
        data = request.get_json()
        content = data.get('content', '').strip()
        
        if not content:
            abort(400, message='Le contenu du commentaire est requis')
        
        new_comment = Comment(
            post_id=post_id,
            user_id=session['user_id'],
            content=content
        )
        
        db.session.add(new_comment)
        db.session.commit()
        
        # --- Création de la notification ---
        post = Post.query.get(post_id)
        if post and post.user_id != session['user_id']:
            message = f"@{session['username']} a commenté votre post."
            create_notification(
                user_id=post.user_id,
                message=message,
                entity_type='comment',
                entity_id=post_id
            )
        # --- Fin de la création de la notification ---
        
        return jsonify({
            'success': True,
            'message': 'Commentaire ajouté avec succès',
            'comment_id': new_comment.id
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
