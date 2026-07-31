from datetime import datetime
from extensions import db


class GraduationYear(db.Model):
    __tablename__ = 'graduation_years'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    year = db.Column(db.String(9), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    projects = db.relationship('Project', backref='graduation_year', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'year': self.year,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class GraduationStatusDef(db.Model):
    __tablename__ = 'graduation_status_defs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), nullable=False)
    code = db.Column(db.String(32), unique=True, nullable=False)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    projects = db.relationship('Project', backref='current_status', lazy=True,
                               foreign_keys='Project.current_status_id')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'sort_order': self.sort_order,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(256), nullable=False)
    graduation_year_id = db.Column(db.Integer, db.ForeignKey('graduation_years.id'), nullable=False)
    description = db.Column(db.Text)
    advisor_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    current_status_id = db.Column(db.Integer, db.ForeignKey('graduation_status_defs.id'), nullable=False)
    max_submissions = db.Column(db.Integer, nullable=False, default=5)
    submission_count = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    submissions = db.relationship('Submission', backref='project', lazy=True,
                                  cascade='all, delete-orphan')
    status_histories = db.relationship('ProjectStatusHistory', backref='project', lazy=True,
                                       cascade='all, delete-orphan',
                                       order_by='ProjectStatusHistory.created_at')

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'title': self.title,
            'graduation_year_id': self.graduation_year_id,
            'description': self.description,
            'advisor_id': self.advisor_id,
            'reviewer_id': self.reviewer_id,
            'current_status_id': self.current_status_id,
            'max_submissions': self.max_submissions,
            'submission_count': self.submission_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class ProjectStatusHistory(db.Model):
    __tablename__ = 'project_status_history'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    from_status_id = db.Column(db.Integer, db.ForeignKey('graduation_status_defs.id', ondelete='SET NULL'))
    to_status_id = db.Column(db.Integer, db.ForeignKey('graduation_status_defs.id'), nullable=False)
    operator_role = db.Column(db.Enum('student', 'teacher', 'admin'), nullable=False)
    operator_id = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    from_status = db.relationship('GraduationStatusDef', foreign_keys=[from_status_id])
    to_status = db.relationship('GraduationStatusDef', foreign_keys=[to_status_id])

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'from_status_id': self.from_status_id,
            'from_status_name': self.from_status.name if self.from_status else None,
            'to_status_id': self.to_status_id,
            'to_status_name': self.to_status.name if self.to_status else None,
            'operator_role': self.operator_role,
            'operator_id': self.operator_id,
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
