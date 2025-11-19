from flask_smorest import Blueprint, abort
from flask import request, jsonify, session, current_app
from utils.notifications import create_notification
from models import db, User, Post, Comment, Like, Group, GroupMember
# from database import get_raw_db_connection # Fonctions SQLite brutes (obsolète)
from .auth import require_login # Décorateur d'authentification

groups_bp = Blueprint('groups', __name__, url_prefix='/groups')

# Groups routes
@groups_bp.route('/groups', methods=['GET'])
@require_login
def get_groups():
    """Get all groups"""
    try:
        user_id = session['user_id']
        
        # Sous-requête pour vérifier si l'utilisateur est membre
        is_member_subquery = db.session.query(
            GroupMember.group_id,
            db.literal(1).label('is_member')
        ).filter(GroupMember.user_id == user_id).subquery()

        # Requête principale
        groups_query = db.session.query(
            Group,
            User.username.label('creator_username'),
            db.func.coalesce(is_member_subquery.c.is_member, 0).label('is_member')
        ).join(User, Group.creator_id == User.id
        ).outerjoin(is_member_subquery, Group.id == is_member_subquery.c.group_id
        ).order_by(Group.created_at.desc()).all()

        # Formater les résultats
        groups_list = []
        for group, creator_username, is_member in groups_query:
            group_dict = {
                'id': group.id,
                'name': group.name,
                'description': group.description,
                'creator_id': group.creator_id,
                'created_at': group.created_at.isoformat(),
                'is_private': group.is_private,
                'members_count': group.members_count,
                'creator_username': creator_username,
                'is_member': bool(is_member)
            }
            groups_list.append(group_dict)
        
        return jsonify({
            'success': True,
            'groups': groups_list
        })
    
    except Exception as e:
        current_app.logger.error(f"Erreur: {e}")
        abort(500, message=str(e))

@groups_bp.route('/groups', methods=['POST'])
@require_login
def create_group():
    """Create a new group"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        is_private = data.get('is_private', False)
        user_id = session['user_id']
        
        if not name:
            abort(400, message='Le nom du groupe est requis')
        
        # Create group
        new_group = Group(
            name=name,
            description=description,
            creator_id=user_id,
            is_private=is_private,
            members_count=1 # Le créateur est automatiquement membre
        )
        db.session.add(new_group)
        db.session.flush() # Pour obtenir l'ID du groupe avant le commit
        
        # Add creator as a member and admin
        new_member = GroupMember(
            group_id=new_group.id,
            user_id=user_id,
            is_admin=True
        )
        db.session.add(new_member)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Groupe créé avec succès',
            'group_id': new_group.id
        })
    
    except Exception as e:
        current_app.logger.error(f"Erreur: {e}")
        db.session.rollback()
        abort(500, message=str(e))

@groups_bp.route('/groups/<int:group_id>/join', methods=['POST'])
@require_login
def join_group(group_id):
    """Join a group"""
    try:
        user_id = session['user_id']
        
        # Check if group exists
        group = Group.query.get(group_id)
        if not group:
            abort(404, message='Groupe non trouvé')
        
        # Check if already a member
        member = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
        
        if member:
            abort(400, message='Vous êtes déjà membre de ce groupe')
        
        # Add member
        new_member = GroupMember(
            group_id=group_id,
            user_id=user_id,
            is_admin=False
        )
        db.session.add(new_member)
        group.members_count += 1
        db.session.commit()
        
        # --- Création de la notification ---
        if group.creator_id != user_id:
            message = f"@{session['username']} a rejoint votre groupe '{group.name}'."
            create_notification(
                user_id=group.creator_id,
                message=message,
                entity_type='group',
                entity_id=group_id
            )
        # --- Fin de la création de la notification ---
        
        return jsonify({
            'success': True,
            'message': 'Vous avez rejoint le groupe avec succès'
        })
    
    except Exception as e:
        current_app.logger.error(f"Erreur: {e}")
        db.session.rollback()
        abort(500, message=str(e))
