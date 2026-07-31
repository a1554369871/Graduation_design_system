from datetime import datetime
from extensions import db


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(256), nullable=False)
    content = db.Column(db.Text)
    sender_type = db.Column(db.Enum('admin', 'teacher'), nullable=False)
    sender_id = db.Column(db.Integer, nullable=False)
    is_global = db.Column(db.Boolean, nullable=False, default=False)
    expires_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    recipients = db.relationship('NotificationRecipient', backref='notification', lazy=True,
                                 cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'sender_type': self.sender_type,
            'sender_id': self.sender_id,
            'is_global': self.is_global,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class NotificationRecipient(db.Model):
    __tablename__ = 'notification_recipients'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    notification_id = db.Column(db.Integer, db.ForeignKey('notifications.id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    read_at = db.Column(db.DateTime)

    student = db.relationship('Student', backref='notification_recipients')

    def to_dict(self):
        return {
            'id': self.id,
            'notification_id': self.notification_id,
            'student_id': self.student_id,
            'is_read': self.is_read,
            'read_at': self.read_at.isoformat() if self.read_at else None,
        }
