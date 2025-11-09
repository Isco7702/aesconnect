from flask_smorest import Blueprint, abort
from flask import request, jsonify, session, current_app
from models import db, Notification
from routes.auth import require_login

notifications_bp = Blueprint('notifications', __name__, url_prefix='/notifications')

@notifications_bp.route('/', methods=['GET'])
@require_login
def get_notifications():
    """Get the user's notifications"""
    try:
        user_id = session['user_id']
        
        # Récupérer les 50 dernières notifications non lues ou les 100 dernières
        notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).limit(100).all()
        
        notifications_list = [n.to_dict() for n in notifications]
        
        # Compter les notifications non lues
        unread_count = Notification.query.filter_by(user_id=user_id, is_read=False).count()
        
        return jsonify({
            'success': True,
            'notifications': notifications_list,
            'unread_count': unread_count
        })
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la récupération des notifications: {e}")
        abort(500, message=str(e))

@notifications_bp.route('/mark_read', methods=['POST'])
@require_login
def mark_all_as_read():
    """Mark all notifications as read"""
    try:
        user_id = session['user_id']
        
        # Marquer toutes les notifications non lues comme lues
        Notification.query.filter_by(user_id=user_id, is_read=False).update({Notification.is_read: True})
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Toutes les notifications ont été marquées comme lues',
            'unread_count': 0
        })
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors du marquage des notifications: {e}")
        db.session.rollback()
        abort(500, message=str(e))
