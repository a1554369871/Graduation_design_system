from datetime import datetime
from extensions import db


class Topic(db.Model):
    __tablename__ = 'topics'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    title = db.Column(db.String(256), nullable=False)
    description = db.Column(db.Text)
    max_students = db.Column(db.Integer, nullable=False, default=1)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    selections = db.relationship('TopicSelection', backref='topic', lazy=True)

    @property
    def selected_count(self):
        return TopicSelection.query.filter_by(
            topic_id=self.id, status='approved'
        ).count()

    def to_dict(self):
        return {
            'id': self.id,
            'teacher_id': self.teacher_id,
            'teacher_name': self.teacher.name if self.teacher else None,
            'title': self.title,
            'description': self.description,
            'max_students': self.max_students,
            'selected_count': self.selected_count,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class TopicSelection(db.Model):
    __tablename__ = 'topic_selections'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id', ondelete='SET NULL'))
    title = db.Column(db.String(256), nullable=False)
    description = db.Column(db.Text)
    type = db.Column(db.Enum('select', 'self_propose'), nullable=False)
    status = db.Column(db.Enum('pending', 'approved', 'rejected'), nullable=False, default='pending')
    review_comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student.name if self.student else None,
            'student_no': self.student.student_id if self.student else None,
            'topic_id': self.topic_id,
            'topic_title': self.topic.title if self.topic else None,
            'title': self.title,
            'description': self.description,
            'type': self.type,
            'status': self.status,
            'review_comment': self.review_comment,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
