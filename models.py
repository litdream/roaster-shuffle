from datetime import datetime
from extensions import db

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    participants = db.relationship('Participant', backref='event', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat()
        }

class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='pool') # 'pool' or 'roster'
    team_id = db.Column(db.Integer, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'event_id': self.event_id,
            'name': self.name,
            'status': self.status,
            'team_id': self.team_id
        }
