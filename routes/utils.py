from flask_smorest import Blueprint, abort
from flask import request, jsonify, session, current_app
from schemas import UserSchema, ReportCreateSchema, SuccessSchema
from models import db, Report, User

from .auth import require_login


utils_bp = Blueprint('utils', __name__, url_prefix='/utils')

@utils_bp.route('/search/users', methods=['GET'])
@require_login
def search_users():
    """Search users by username or full name"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'users': []})
        
        # Utilisation de l'ORM pour la recherche
        search_term = f'%{query}%'
        users_query = User.query.filter(
            (User.username.ilike(search_term)) | (User.full_name.ilike(search_term)),
            User.id != session['user_id']
        ).limit(20).all()
        
        users_list = [user.to_dict() for user in users_query]
        return jsonify({'users': users_list})
    
    except Exception as e:
        current_app.logger.error(f"Erreur search users: {e}")
        abort(500, message=str(e))

@utils_bp.route('/search/posts', methods=['GET'])
@require_login
def search_posts():
    """Search posts by content"""
    try:
        from models import Post
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'posts': []})
        
        # Recherche dans le contenu des posts
        search_term = f'%{query}%'
        posts_query = Post.query.filter(
            Post.content.ilike(search_term)
        ).order_by(Post.created_at.desc()).limit(50).all()
        
        posts_list = []
        for post in posts_query:
            post_dict = {
                'id': post.id,
                'user_id': post.user_id,
                'content': post.content,
                'image_url': post.image_url,
                'created_at': post.created_at.isoformat() if post.created_at else None,
                'likes_count': post.likes_count,
                'comments_count': post.comments_count,
                'username': post.author.username if post.author else 'Unknown',
                'full_name': post.author.full_name if post.author else 'Unknown',
                'avatar_url': post.author.avatar_url if post.author else ''
            }
            posts_list.append(post_dict)
        
        return jsonify({'posts': posts_list})
    
    except Exception as e:
        current_app.logger.error(f"Erreur search posts: {e}")
        abort(500, message=str(e))

@utils_bp.route('/report', methods=['POST'])
@require_login
@utils_bp.arguments(ReportCreateSchema)
@utils_bp.response(201, SuccessSchema(exclude=('success',)), description="Signalement envoyé avec succès")
def report_content(report_data):
    """Report inappropriate content or user"""
    try:
        new_report = Report(
            reporter_id=session['user_id'],
            reported_user_id=report_data.get('reported_user_id'),
            reported_post_id=report_data.get('reported_post_id'),
            reason=report_data['reason']
        )
        
        db.session.add(new_report)
        db.session.commit()
        
        return {
            'message': 'Signalement envoyé à la modération',
            'report_id': new_report.id
        }
    
    except Exception as e:
        current_app.logger.error(f"Erreur: {e}")
        db.session.rollback()
        abort(500, message=str(e))

@utils_bp.route('/health', methods=['GET'])
@utils_bp.response(200, SuccessSchema(exclude=('success',)), description="Statut de l'API")
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection via ORM
        db.session.execute(db.select([db.literal(1)])).scalar()
        db_status = 'connected'
    except Exception as e:
        db_status = f'error: {str(e)}'
    
    return {
        'message': 'Statut de l\'API',
        'status': 'healthy',
        'service': 'Social Network API',
        'database': db_status
    }


