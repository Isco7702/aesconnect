from flask import jsonify, session
from flask_smorest import Blueprint, abort
from ..models import db, Notification
from .auth import require_login

notifications_bp = Blueprint('notifications', __name__, url_prefix='/notifications')


@notifications_bp.route('/', methods=['GET'])
@require_login
def get_notifications():
    notifications = Notification.query.filter_by(user_id=session['user_id']).order_by(Notification.created_at.desc()).limit(100).all()
    return jsonify({
        'success': True,
        'notifications': [
            {
                'id': n.id,
                'message': n.message,
                'is_read': n.is_read,
                'created_at': n.created_at.isoformat() if n.created_at else None,
                'entity_type': n.entity_type,
                'entity_id': n.entity_id,
            }
            for n in notifications
        ]
    })


@notifications_bp.route('/<int:notification_id>/read', methods=['POST'])
@require_login
def mark_notification_read(notification_id):
    notification = Notification.query.filter_by(id=notification_id, user_id=session['user_id']).first()
    if not notification:
        abort(404, message='Notification non trouvée')

    notification.is_read = True
    db.session.commit()
    return jsonify({'success': True, 'message': 'Notification marquée comme lue'})
