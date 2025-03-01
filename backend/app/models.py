# app/models.py

from app import db
from datetime import datetime
from sqlalchemy import Index, event
from sqlalchemy.orm import relationship
from app.extensions import db

class aquamans(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.Float)
    tempResult = db.Column(db.String(255))
    oxygen = db.Column(db.Float)
    oxygenResult = db.Column(db.String(255))
    phlevel = db.Column(db.Float)
    phResult = db.Column(db.String(255))
    turbidity = db.Column(db.Float)
    turbidityResult = db.Column(db.String(255))
    catfish = db.Column(db.Float, default=0)
    dead_catfish = db.Column(db.Float, default=0)
    timeData = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    dead_catfish_image = db.Column(db.LargeBinary, nullable=True)
    
    # Add relationship to alerts
    alerts = relationship('Alert', backref='reading', lazy='dynamic')

    # Add indexes for commonly queried columns
    __table_args__ = (
        Index('idx_temp_oxy_ph', 'temperature', 'oxygen', 'phlevel'),
        Index('idx_parameters', 'temperature', 'oxygen', 'phlevel', 'turbidity'),
        Index('idx_results', 'tempResult', 'oxygenResult', 'phResult', 'turbidityResult'),
    )

    def __repr__(self):
        return f'<aquamans {self.id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'temperature': self.temperature,
            'tempResult': self.tempResult,
            'oxygen': self.oxygen,
            'oxygenResult': self.oxygenResult,
            'phlevel': self.phlevel,
            'phResult': self.phResult,
            'turbidity': self.turbidity,
            'turbidityResult': self.turbidityResult,
            'catfish': self.catfish,
            'dead_catfish': self.dead_catfish,
            'timeData': self.timeData.strftime('%Y-%m-%d %H:%M:%S') if self.timeData else None
        }

    def check_parameters(self):
        """Check if any parameters are outside normal ranges"""
        alerts = []
        
        # Temperature check
        if self.temperature <= 20 or self.temperature >= 35:
            alerts.append({
                'type': 'temperature',
                'severity': 'critical',
                'value': self.temperature,
                'message': f'Temperature is {self.tempResult}'
            })
        elif 20 < self.temperature < 26 or 32 <= self.temperature < 35:
            alerts.append({
                'type': 'temperature',
                'severity': 'warning',
                'value': self.temperature,
                'message': f'Temperature is {self.tempResult}'
            })

        # Oxygen check
        if self.oxygen <= 0.8:
            alerts.append({
                'type': 'oxygen',
                'severity': 'critical',
                'value': self.oxygen,
                'message': f'Oxygen is {self.oxygenResult}'
            })
        elif self.oxygen < 1.5:
            alerts.append({
                'type': 'oxygen',
                'severity': 'warning',
                'value': self.oxygen,
                'message': f'Oxygen is {self.oxygenResult}'
            })

        # pH check
        if self.phlevel < 4 or self.phlevel > 9:
            alerts.append({
                'type': 'ph',
                'severity': 'critical',
                'value': self.phlevel,
                'message': f'pH is {self.phResult}'
            })
        elif 4 <= self.phlevel < 6 or 7.5 < self.phlevel <= 9:
            alerts.append({
                'type': 'ph',
                'severity': 'warning',
                'value': self.phlevel,
                'message': f'pH is {self.phResult}'
            })

        # Turbidity check
        if self.turbidity >= 50:
            alerts.append({
                'type': 'turbidity',
                'severity': 'critical',
                'value': self.turbidity,
                'message': f'Turbidity is {self.turbidityResult}'
            })
        elif 20 <= self.turbidity < 50:
            alerts.append({
                'type': 'turbidity',
                'severity': 'warning',
                'value': self.turbidity,
                'message': f'Turbidity is {self.turbidityResult}'
            })

        return alerts

class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reading_id = db.Column(db.Integer, db.ForeignKey('aquamans.id'))
    alert_type = db.Column(db.String(50))  # 'water_quality' or 'dead_catfish'
    severity = db.Column(db.String(20))    # 'critical', 'warning', 'info'
    parameter = db.Column(db.String(20))   # 'temperature', 'oxygen', 'ph', 'turbidity'
    value = db.Column(db.Float)
    message = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    acknowledged = db.Column(db.Boolean, default=False)
    acknowledged_at = db.Column(db.DateTime)
    acknowledged_by = db.Column(db.String(100))

    def to_dict(self):
        return {
            'id': self.id,
            'reading_id': self.reading_id,
            'alert_type': self.alert_type,
            'severity': self.severity,
            'parameter': self.parameter,
            'value': self.value,
            'message': self.message,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'acknowledged': self.acknowledged,
            'acknowledged_at': self.acknowledged_at.strftime('%Y-%m-%d %H:%M:%S') if self.acknowledged_at else None,
            'acknowledged_by': self.acknowledged_by
        }

# Add SQLAlchemy event listeners to automatically create alerts
@event.listens_for(aquamans, 'after_insert')
def check_parameters_after_insert(mapper, connection, target):
    alerts = target.check_parameters()
    if alerts:
        for alert_data in alerts:
            alert = Alert(
                reading_id=target.id,
                alert_type='water_quality',
                severity=alert_data['severity'],
                parameter=alert_data['type'],
                value=alert_data['value'],
                message=alert_data['message']
            )
            db.session.add(alert)
        try:
            db.session.commit()
        except:
            db.session.rollback()