from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.user import User, Student, Teacher, Admin
from models.project import Project, GraduationStatusDef
from models.notification import Notification, NotificationRecipient
from utils.decorators import role_required
from utils.helpers import log_system

notification_bp = Blueprint('notification', __name__)


def get_student_id(user_id):
    s = Student.query.filter_by(user_id=user_id).first()
    return s.id if s else None


def get_teacher_id(user_id):
    t = Teacher.query.filter_by(user_id=user_id).first()
    return t.id if t else None


def get_admin_id(user_id):
    a = Admin.query.filter_by(user_id=user_id).first()
    return a.id if a else None


def get_sender_name(sender_type, sender_id):
    if sender_type == 'admin':
        a = Admin.query.get(sender_id)
        return a.name if a else '管理员'
    elif sender_type == 'teacher':
        t = Teacher.query.get(sender_id)
        return t.name if t else '教师'
    return '未知'


# ==================== 学生端 - 获取通知 ====================

@notification_bp.route('/student', methods=['GET'])
@jwt_required()
@role_required('student')
def student_notifications():
    student_id = get_student_id(get_jwt_identity())
    if not student_id:
        return jsonify({'msg': '学生信息不存在'}), 404

    notice_type = request.args.get('type', 'all')

    result = []

    if notice_type in ('all', 'admin'):
        admin_notifications = Notification.query.filter(
            Notification.sender_type == 'admin',
            Notification.is_global == True,
            db.or_(
                Notification.expires_at.is_(None),
                Notification.expires_at > datetime.now()
            )
        ).order_by(Notification.created_at.desc()).all()

        for n in admin_notifications:
            item = n.to_dict()
            item['sender_name'] = get_sender_name(n.sender_type, n.sender_id)
            item['notice_type'] = 'admin'
            recipient = NotificationRecipient.query.filter_by(
                notification_id=n.id, student_id=student_id
            ).first()
            item['is_read'] = recipient.is_read if recipient else True
            result.append(item)

    if notice_type in ('all', 'teacher'):
        recipient_ids = db.session.query(NotificationRecipient.notification_id).filter(
            NotificationRecipient.student_id == student_id
        ).subquery()

        teacher_notifications = Notification.query.filter(
            Notification.id.in_(recipient_ids),
            Notification.sender_type == 'teacher',
            db.or_(
                Notification.expires_at.is_(None),
                Notification.expires_at > datetime.now()
            )
        ).order_by(Notification.created_at.desc()).all()

        for n in teacher_notifications:
            item = n.to_dict()
            item['sender_name'] = get_sender_name(n.sender_type, n.sender_id)
            item['notice_type'] = 'teacher'
            recipient = NotificationRecipient.query.filter_by(
                notification_id=n.id, student_id=student_id
            ).first()
            item['is_read'] = recipient.is_read if recipient else False
            result.append(item)

    result.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return jsonify(result), 200


@notification_bp.route('/student/read/<int:notification_id>', methods=['PUT'])
@jwt_required()
@role_required('student')
def mark_as_read(notification_id):
    student_id = get_student_id(get_jwt_identity())
    recipient = NotificationRecipient.query.filter_by(
        notification_id=notification_id, student_id=student_id
    ).first()
    if recipient:
        recipient.is_read = True
        recipient.read_at = datetime.now()
        db.session.commit()
    return jsonify({'msg': 'ok'}), 200


# ==================== 教师端 - 获取管理员通知 ====================

@notification_bp.route('/admin-list', methods=['GET'])
@jwt_required()
@role_required('teacher', 'admin')
def admin_notifications():
    notifications = Notification.query.filter(
        Notification.sender_type == 'admin',
        Notification.is_global == True,
        db.or_(
            Notification.expires_at.is_(None),
            Notification.expires_at > datetime.now()
        )
    ).order_by(Notification.created_at.desc()).all()

    result = []
    for n in notifications:
        item = n.to_dict()
        item['sender_name'] = get_sender_name(n.sender_type, n.sender_id)
        result.append(item)
    return jsonify(result), 200


# ==================== 教师端 - 学生进度与发送通知 ====================

@notification_bp.route('/teacher/students-progress', methods=['GET'])
@jwt_required()
@role_required('teacher')
def teacher_students_progress():
    teacher_id = get_teacher_id(get_jwt_identity())
    advisor_type = request.args.get('type', 'advisor')
    keyword = request.args.get('keyword')

    if advisor_type == 'advisor':
        query = Project.query.filter_by(advisor_id=teacher_id)
    else:
        query = Project.query.filter_by(reviewer_id=teacher_id)

    if keyword:
        query = query.join(Student).filter(
            db.or_(
                Student.name.like(f'%{keyword}%'),
                Student.student_id.like(f'%{keyword}%'),
                Project.title.like(f'%{keyword}%'),
            )
        )

    projects = query.order_by(Project.updated_at.desc()).all()
    result = []
    for p in projects:
        item = {
            'student_id': p.student.id if p.student else None,
            'student_user_id': p.student.user_id if p.student else None,
            'student_name': p.student.name if p.student else None,
            'student_no': p.student.student_id if p.student else None,
            'project_title': p.title,
            'project_id': p.id,
            'status_name': p.current_status.name if p.current_status else None,
            'status_sort': p.current_status.sort_order if p.current_status else None,
            'updated_at': p.updated_at.isoformat() if p.updated_at else None,
        }
        result.append(item)

    return jsonify(result), 200


@notification_bp.route('/teacher/send', methods=['POST'])
@jwt_required()
@role_required('teacher')
def teacher_send_notification():
    teacher_id = get_teacher_id(get_jwt_identity())
    data = request.get_json()
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    student_ids = data.get('student_ids', [])

    if not title:
        return jsonify({'msg': '标题不能为空'}), 400
    if not student_ids:
        return jsonify({'msg': '请选择接收学生'}), 400

    notification = Notification(
        title=title,
        content=content,
        sender_type='teacher',
        sender_id=teacher_id,
        is_global=False,
    )
    db.session.add(notification)
    db.session.flush()

    for sid in student_ids:
        recipient = NotificationRecipient(
            notification_id=notification.id,
            student_id=sid,
        )
        db.session.add(recipient)

    db.session.commit()

    log_system(get_jwt_identity(), 'send_notification', 'notification', notification.id,
               f'教师发送通知给{len(student_ids)}名学生')
    return jsonify({'msg': '发送成功', 'notification_id': notification.id}), 201


@notification_bp.route('/teacher/sent', methods=['GET'])
@jwt_required()
@role_required('teacher')
def teacher_sent_notifications():
    teacher_id = get_teacher_id(get_jwt_identity())
    notifications = Notification.query.filter_by(
        sender_type='teacher', sender_id=teacher_id
    ).order_by(Notification.created_at.desc()).all()

    result = []
    for n in notifications:
        item = n.to_dict()
        item['sender_name'] = get_sender_name(n.sender_type, n.sender_id)
        recipients = NotificationRecipient.query.filter_by(
            notification_id=n.id
        ).all()
        item['recipient_count'] = len(recipients)
        item['read_count'] = sum(1 for r in recipients if r.is_read)
        item['recipients'] = []
        for r in recipients:
            item['recipients'].append({
                'student_id': r.student_id,
                'student_name': r.student.name if r.student else None,
                'student_no': r.student.student_id if r.student else None,
                'is_read': r.is_read,
                'read_at': r.read_at.isoformat() if r.read_at else None,
            })
        result.append(item)

    return jsonify(result), 200


# ==================== 管理员端 - 发送通知 ====================

@notification_bp.route('/admin/send', methods=['POST'])
@jwt_required()
@role_required('admin')
def admin_send_notification():
    admin_id = get_admin_id(get_jwt_identity())
    data = request.get_json()
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    expires_at_str = data.get('expires_at')

    if not title:
        return jsonify({'msg': '标题不能为空'}), 400

    expires_at = None
    if expires_at_str:
        try:
            expires_at = datetime.fromisoformat(expires_at_str)
        except ValueError:
            return jsonify({'msg': '过期时间格式错误'}), 400

    notification = Notification(
        title=title,
        content=content,
        sender_type='admin',
        sender_id=admin_id,
        is_global=True,
        expires_at=expires_at,
    )
    db.session.add(notification)
    db.session.commit()

    log_system(get_jwt_identity(), 'send_notification', 'notification', notification.id,
               f'管理员发送通知: {title}')
    return jsonify({'msg': '发送成功', 'notification_id': notification.id}), 201


@notification_bp.route('/admin/all', methods=['GET'])
@jwt_required()
@role_required('admin')
def admin_all_notifications():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    pagination = Notification.query.filter_by(
        sender_type='admin'
    ).order_by(Notification.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    result = []
    for n in pagination.items:
        item = n.to_dict()
        item['sender_name'] = get_sender_name(n.sender_type, n.sender_id)
        item['is_expired'] = n.expires_at and n.expires_at < datetime.now()
        result.append(item)

    return jsonify({
        'items': result,
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
    }), 200


@notification_bp.route('/admin/<int:notification_id>', methods=['PUT'])
@jwt_required()
@role_required('admin')
def admin_update_notification(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    if notification.sender_type != 'admin':
        return jsonify({'msg': '只能修改管理员发送的通知'}), 400

    data = request.get_json()
    if 'title' in data:
        notification.title = data['title']
    if 'content' in data:
        notification.content = data['content']
    if 'expires_at' in data:
        if data['expires_at']:
            try:
                notification.expires_at = datetime.fromisoformat(data['expires_at'])
            except ValueError:
                return jsonify({'msg': '过期时间格式错误'}), 400
        else:
            notification.expires_at = None

    db.session.commit()
    log_system(get_jwt_identity(), 'update_notification', 'notification', notification_id)
    return jsonify({'msg': '更新成功'}), 200


@notification_bp.route('/admin/<int:notification_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin')
def admin_delete_notification(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    if notification.sender_type != 'admin':
        return jsonify({'msg': '只能删除管理员发送的通知'}), 400

    db.session.delete(notification)
    db.session.commit()
    log_system(get_jwt_identity(), 'delete_notification', 'notification', notification_id)
    return jsonify({'msg': '删除成功'}), 200


# ==================== 获取所有学生列表（教师发送通知时选择） ====================

@notification_bp.route('/teacher/students-list', methods=['GET'])
@jwt_required()
@role_required('teacher')
def teacher_students_list():
    teacher_id = get_teacher_id(get_jwt_identity())
    keyword = request.args.get('keyword')

    projects = Project.query.filter_by(advisor_id=teacher_id).all()
    student_ids = [p.student_id for p in projects]

    query = Student.query.filter(Student.id.in_(student_ids))
    if keyword:
        query = query.filter(
            db.or_(
                Student.name.like(f'%{keyword}%'),
                Student.student_id.like(f'%{keyword}%'),
            )
        )

    students = query.all()
    return jsonify([s.to_dict() for s in students]), 200
