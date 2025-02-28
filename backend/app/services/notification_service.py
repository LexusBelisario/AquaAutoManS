# app/services/notification_service.py
from datetime import datetime
import logging
from flask_socketio import SocketIO
from app import db
from app.models import Alert 
socketio = SocketIO()

class NotificationService:
    def __init__(self):
        self.alert_history = []
        self.max_history = 50

    def send_alert(self, reading_id, alert_type, severity, parameter, value, message):
        try:
            # Create new alert using your existing Alert model
            new_alert = Alert(
                reading_id=reading_id,
                alert_type=alert_type,
                severity=severity,
                parameter=parameter,
                value=value,
                message=message,
                timestamp=datetime.utcnow()
            )
            
            # Add to database
            db.session.add(new_alert)
            db.session.commit()

            # Convert to dict for WebSocket emission
            alert_dict = new_alert.to_dict()
            
            # Add to history
            self.alert_history.append(alert_dict)
            if len(self.alert_history) > self.max_history:
                self.alert_history.pop(0)

            # Emit via WebSocket
            socketio.emit('new_alert', alert_dict)
            
            return alert_dict
            
        except Exception as e:
            logging.error(f"Error sending alert: {e}")
            db.session.rollback()
            return None

    def get_unacknowledged_alerts(self):
        """Get all unacknowledged alerts"""
        return Alert.query.filter_by(acknowledged=False).order_by(Alert.timestamp.desc()).all()

    def acknowledge_alert(self, alert_id, user):
        """Acknowledge an alert"""
        try:
            alert = Alert.query.get(alert_id)
            if alert:
                alert.acknowledged = True
                alert.acknowledged_at = datetime.utcnow()
                alert.acknowledged_by = user
                db.session.commit()
                return alert.to_dict()
        except Exception as e:
            logging.error(f"Error acknowledging alert: {e}")
            db.session.rollback()
        return None

    def get_alerts_by_type(self, alert_type):
        """Get alerts by type"""
        return Alert.query.filter_by(alert_type=alert_type).order_by(Alert.timestamp.desc()).all()

    def get_alerts_by_severity(self, severity):
        """Get alerts by severity"""
        return Alert.query.filter_by(severity=severity).order_by(Alert.timestamp.desc()).all()

    def get_recent_alerts(self, limit=10):
        """Get recent alerts"""
        return Alert.query.order_by(Alert.timestamp.desc()).limit(limit).all()

notification_service = NotificationService()