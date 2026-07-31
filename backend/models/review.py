from datetime import datetime
from extensions import db


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submissions.id', ondelete='CASCADE'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    review_type = db.Column(db.Enum('advisor', 'reviewer'), nullable=False)
    revision_round = db.Column(db.Integer, nullable=False, default=1)
    score = db.Column(db.Numeric(5, 2))
    comment = db.Column(db.Text)
    is_approved = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    withdrawn_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'submission_id': self.submission_id,
            'reviewer_id': self.reviewer_id,
            'reviewer_name': self.reviewer.name if self.reviewer else None,
            'review_type': self.review_type,
            'revision_round': self.revision_round,
            'score': float(self.score) if self.score else None,
            'comment': self.comment,
            'is_approved': self.is_approved,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'withdrawn_at': self.withdrawn_at.isoformat() if self.withdrawn_at else None,
        }
