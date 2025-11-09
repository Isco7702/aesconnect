from models import db, Notification
from datetime import datetime

def create_notification(user_id, message, entity_type=None, entity_id=None):
    """
    Crée et enregistre une nouvelle notification dans la base de données.
    """
    try:
        new_notification = Notification(
            user_id=user_id,
            message=message,
            entity_type=entity_type,
            entity_id=entity_id,
            created_at=datetime.utcnow()
        )
        db.session.add(new_notification)
        db.session.commit()
        return True
    except Exception as e:
        # Log l'erreur mais ne propage pas, car la notification est secondaire
        print(f"Erreur lors de la création de la notification pour l'utilisateur {user_id}: {e}")
        db.session.rollback()
        return False
