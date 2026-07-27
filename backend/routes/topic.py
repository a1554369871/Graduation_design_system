from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.user import User, Student, Teacher
from models.project import Project, ProjectStatusHistory, GraduationStatusDef
from models.topic import Topic, TopicSelection
from utils.decorators import role_required
from utils.helpers import log_system

topic_bp = Blueprint('topic', __name__)


def get_student_id(user_id):
    s = Student.query.filter_by(user_id=user_id).first()
    return s.id if s else None


def get_teacher_id(user_id):
    t = Teacher.query.filter_by(user_id=user_id).first()
    return t.id if t else None


# ==================== 学生端：选题管理 ====================

@topic_bp.route('/student/available-topics', methods=['GET'])
@jwt_required()
@role_required('student')
def available_topics():
    topics = Topic.query.filter_by(is_active=True).all()
    result = []
    for t in topics:
        item = t.to_dict()
        item['can_select'] = item['selected_count'] < item['max_students']
        result.append(item)
    return jsonify(result), 200


@topic_bp.route('/student/my-selection', methods=['GET'])
@jwt_required()
@role_required('student')
def my_selection():
    student_id = get_student_id(get_jwt_identity())
    selection = TopicSelection.query.filter_by(student_id=student_id).order_by(
        TopicSelection.created_at.desc()
    ).first()
    if not selection:
        return jsonify(None), 200
    return jsonify(selection.to_dict()), 200


@topic_bp.route('/student/select', methods=['POST'])
@jwt_required()
@role_required('student')
def select_topic():
    student_id = get_student_id(get_jwt_identity())
    data = request.get_json()

    existing = TopicSelection.query.filter_by(
        student_id=student_id, status='pending'
    ).first()
    if existing:
        return jsonify({'msg': '您已有待审核的选题申请，请等待审核'}), 400

    approved = TopicSelection.query.filter_by(
        student_id=student_id, status='approved'
    ).first()
    if approved:
        return jsonify({'msg': '您已通过选题审核，无需重复选题'}), 400

    topic_id = data.get('topic_id')
    topic = Topic.query.get(topic_id)
    if not topic or not topic.is_active:
        return jsonify({'msg': '选题不存在或已关闭'}), 404

    selection = TopicSelection(
        student_id=student_id,
        topic_id=topic.id,
        title=topic.title,
        description=topic.description,
        type='select',
        status='pending',
    )
    db.session.add(selection)
    db.session.commit()

    log_system(get_jwt_identity(), 'select_topic', 'topic_selection', selection.id,
               f'学生选择选题: {topic.title}')
    return jsonify({'msg': '选题已提交，等待教师审核', 'selection': selection.to_dict()}), 201


@topic_bp.route('/student/propose', methods=['POST'])
@jwt_required()
@role_required('student')
def propose_topic():
    student_id = get_student_id(get_jwt_identity())
    data = request.get_json()

    if not data.get('title'):
        return jsonify({'msg': '请输入选题标题'}), 400

    existing = TopicSelection.query.filter_by(
        student_id=student_id, status='pending'
    ).first()
    if existing:
        return jsonify({'msg': '您已有待审核的选题申请，请等待审核'}), 400

    approved = TopicSelection.query.filter_by(
        student_id=student_id, status='approved'
    ).first()
    if approved:
        return jsonify({'msg': '您已通过选题审核，无需重复选题'}), 400

    selection = TopicSelection(
        student_id=student_id,
        topic_id=None,
        title=data['title'],
        description=data.get('description', ''),
        type='self_propose',
        status='pending',
    )
    db.session.add(selection)
    db.session.commit()

    log_system(get_jwt_identity(), 'propose_topic', 'topic_selection', selection.id,
               f'学生自主选题: {data["title"]}')
    return jsonify({'msg': '自主选题已提交，等待教师审核', 'selection': selection.to_dict()}), 201


# ==================== 教师端：选题管理 ====================

@topic_bp.route('/teacher/topics', methods=['GET'])
@jwt_required()
@role_required('teacher')
def list_my_topics():
    teacher_id = get_teacher_id(get_jwt_identity())
    topics = Topic.query.filter_by(teacher_id=teacher_id).order_by(
        Topic.created_at.desc()
    ).all()
    result = []
    for t in topics:
        item = t.to_dict()
        selections = TopicSelection.query.filter_by(topic_id=t.id).all()
        item['selections'] = [s.to_dict() for s in selections]
        result.append(item)
    return jsonify(result), 200


@topic_bp.route('/teacher/topics', methods=['POST'])
@jwt_required()
@role_required('teacher')
def create_topic():
    teacher_id = get_teacher_id(get_jwt_identity())
    data = request.get_json()

    if not data.get('title'):
        return jsonify({'msg': '请输入选题标题'}), 400

    topic = Topic(
        teacher_id=teacher_id,
        title=data['title'],
        description=data.get('description', ''),
        max_students=data.get('max_students', 1),
    )
    db.session.add(topic)
    db.session.commit()

    log_system(get_jwt_identity(), 'create_topic', 'topic', topic.id,
               f'教师发布选题: {topic.title}')
    return jsonify({'msg': '选题发布成功', 'topic': topic.to_dict()}), 201


@topic_bp.route('/teacher/topics/<int:topic_id>', methods=['PUT'])
@jwt_required()
@role_required('teacher')
def update_topic(topic_id):
    teacher_id = get_teacher_id(get_jwt_identity())
    topic = Topic.query.get_or_404(topic_id)

    if topic.teacher_id != teacher_id:
        return jsonify({'msg': '只能修改自己的选题'}), 403

    data = request.get_json()
    for field in ['title', 'description', 'max_students', 'is_active']:
        if field in data:
            setattr(topic, field, data[field])
    db.session.commit()

    log_system(get_jwt_identity(), 'update_topic', 'topic', topic_id)
    return jsonify({'msg': '选题更新成功', 'topic': topic.to_dict()}), 200


@topic_bp.route('/teacher/topics/<int:topic_id>', methods=['DELETE'])
@jwt_required()
@role_required('teacher')
def delete_topic(topic_id):
    teacher_id = get_teacher_id(get_jwt_identity())
    topic = Topic.query.get_or_404(topic_id)

    if topic.teacher_id != teacher_id:
        return jsonify({'msg': '只能删除自己的选题'}), 403

    db.session.delete(topic)
    db.session.commit()

    log_system(get_jwt_identity(), 'delete_topic', 'topic', topic_id)
    return jsonify({'msg': '选题已删除'}), 200


# ==================== 教师端：选题审核 ====================

@topic_bp.route('/teacher/pending-selections', methods=['GET'])
@jwt_required()
@role_required('teacher')
def pending_selections():
    teacher_id = get_teacher_id(get_jwt_identity())

    my_topic_ids = [t.id for t in Topic.query.filter_by(teacher_id=teacher_id).all()]

    selections = TopicSelection.query.filter(
        TopicSelection.status == 'pending'
    ).order_by(TopicSelection.created_at.desc()).all()

    result = []
    for s in selections:
        if s.type == 'select' and s.topic_id in my_topic_ids:
            result.append(s.to_dict())
        elif s.type == 'self_propose':
            if not s.topic_id:
                result.append(s.to_dict())

    return jsonify(result), 200


@topic_bp.route('/teacher/all-pending-selections', methods=['GET'])
@jwt_required()
@role_required('teacher')
def all_pending_selections():
    selections = TopicSelection.query.filter(
        TopicSelection.status == 'pending'
    ).order_by(TopicSelection.created_at.desc()).all()
    return jsonify([s.to_dict() for s in selections]), 200


@topic_bp.route('/teacher/selections/<int:selection_id>/review', methods=['POST'])
@jwt_required()
@role_required('teacher')
def review_selection(selection_id):
    teacher_id = get_teacher_id(get_jwt_identity())
    selection = TopicSelection.query.get_or_404(selection_id)
    data = request.get_json()

    action = data.get('action')
    comment = data.get('comment', '')

    if action == 'approve':
        selection.status = 'approved'
        selection.review_comment = comment

        project = Project.query.filter_by(student_id=selection.student_id).first()
        if project:
            project.title = selection.title
            project.description = selection.description or project.description

            first_draft_status = GraduationStatusDef.query.filter_by(
                code='first_draft'
            ).first()
            if first_draft_status:
                history = ProjectStatusHistory(
                    project_id=project.id,
                    from_status_id=project.current_status_id,
                    to_status_id=first_draft_status.id,
                    operator_role='teacher',
                    operator_id=teacher_id,
                    comment='选题审核通过，进入初稿阶段',
                )
                db.session.add(history)
                project.current_status_id = first_draft_status.id
        else:
            return jsonify({'msg': '未找到该学生的毕设项目'}), 404

        db.session.commit()
        log_system(get_jwt_identity(), 'approve_topic', 'topic_selection', selection_id,
                   f'选题审核通过: {selection.title}')
        return jsonify({'msg': '选题已通过，学生可进入初稿阶段'}), 200

    elif action == 'reject':
        selection.status = 'rejected'
        selection.review_comment = comment
        db.session.commit()

        log_system(get_jwt_identity(), 'reject_topic', 'topic_selection', selection_id,
                   f'选题审核不通过: {comment}')
        return jsonify({'msg': '选题已驳回'}), 200

    return jsonify({'msg': '无效的操作'}), 400


@topic_bp.route('/teacher/reviewed-selections', methods=['GET'])
@jwt_required()
@role_required('teacher')
def reviewed_selections():
    teacher_id = get_teacher_id(get_jwt_identity())

    my_topic_ids = [t.id for t in Topic.query.filter_by(teacher_id=teacher_id).all()]

    selections = TopicSelection.query.filter(
        TopicSelection.status.in_(['approved', 'rejected'])
    ).order_by(TopicSelection.updated_at.desc()).all()

    result = []
    for s in selections:
        if s.type == 'select' and s.topic_id in my_topic_ids:
            result.append(s.to_dict())
        elif s.type == 'self_propose' and not s.topic_id:
            result.append(s.to_dict())

    return jsonify(result), 200
