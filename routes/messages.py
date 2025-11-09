from flask_smorest import Blueprint, abort
from flask import request, jsonify, session, current_app
from models import db, User, Message
from schemas import MessageSchema, MessageSendSchema, SuccessSchema
from utils.notifications import create_notification
# from database import get_raw_db_connection # Fonctions SQLite brutes (obsolète)
from routes.auth import require_login

messages_bp = Blueprint('messages', __name__, url_prefix='/messages')

@messages_bp.route('/', methods=['GET'])
@require_login
@messages_bp.response(200, MessageSchema(many=True), description="Liste des messages reçus et envoyés")
def get_messages():
    """Get user's messages"""
    try:
        user_id = session['user_id']
        
        # Récupérer les messages envoyés ou reçus par l'utilisateur
        messages = Message.query.filter(
            (Message.receiver_id == user_id) | (Message.sender_id == user_id)
        ).order_by(Message.created_at.desc()).limit(50).all()
        
        # L'objet Message est retourné directement, Marshmallow s'occupe de la sérialisation
        return messages
        
    except Exception as e:
        current_app.logger.error(f"Erreur: {e}")
        abort(500, message=str(e))

@messages_bp.route('/', methods=['POST'])
@require_login
@messages_bp.arguments(MessageSendSchema)
@messages_bp.response(201, SuccessSchema(exclude=('success',)), description="Message envoyé avec succès")
def send_message(message_data):
    """Send a message"""
    try:
        receiver_id = message_data['receiver_id']
        content = message_data['content']
        
        # Vérifier si le destinataire existe
        if not User.query.get(receiver_id):
            abort(404, message='Destinataire non trouvé')
        
        new_message = Message(
            sender_id=session['user_id'],
            receiver_id=receiver_id,
            content=content
        )
        
        db.session.add(new_message)
        db.session.commit()
        
        # --- Création de la notification ---
        message_text = f"@{session['username']} vous a envoyé un message privé."
        create_notification(
            user_id=receiver_id,
            message=message_text,
            entity_type='message',
            entity_id=new_message.id
        )
        # --- Fin de la création de la notification ---
        
        return {
            'message': 'Message envoyé',
            'message_id': new_message.id
        }
    
    except Exception as e:
        current_app.logger.error(f"Erreur: {e}")
        db.session.rollback()
        abort(500, message=str(e))
