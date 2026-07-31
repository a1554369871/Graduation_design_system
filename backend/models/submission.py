from datetime import datetime
from extensions import db


class Submission(db.Model):
    __tablename__ = 'submissions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    version = db.Column(db.Integer, nullable=False)
    submission_type = db.Column(db.Enum('draft', 'round1', 'round2', 'round3', 'final_check', 'final'),
                                nullable=False, default='draft')
    file_name = db.Column(db.String(256), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    file_size = db.Column(db.BigInteger, nullable=False, default=0)
    submitted_by = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    description = db.Column(db.Text)
    downloaded_at = db.Column(db.DateTime)
    download_count = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    reviews = db.relationship('Review', backref='submission', lazy=True,
                              cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'version': self.version,
            'submission_type': self.submission_type,
            'file_name': self.file_name,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'submitted_by': self.submitted_by,
            'description': self.description,
            'downloaded_at': self.downloaded_at.isoformat() if self.downloaded_at else None,
            'download_count': self.download_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
