from app import db
from datetime import datetime
from sqlalchemy import Index

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

    __table_args__ = (
        Index('idx_timedata', 'timeData'),
        Index('idx_temp_oxygen', 'temperature', 'oxygen'),
        Index('idx_dead_catfish', 'dead_catfish'),
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