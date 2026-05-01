from ..models import db, Notification


def create_notification(user_id: int, message: str, entity_type: str | None = None, entity_id: int | None = None):
    notification = Notification(
        user_id=user_id,
        message=message,
        entity_type=entity_type,
        entity_id=entity_id,
    )
    db.session.add(notification)
    db.session.commit()
    return notification
