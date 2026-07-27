import os
from flask import Blueprint, request, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.user import User, Teacher, Student
from models.project import Project, ProjectStatusHistory, GraduationStatusDef
from models.submission import Submission
from models.review import Review
from utils.decorators import role_required
from utils.helpers import log_system

teacher_bp = Blueprint('teacher', __name__)


def get_teacher_id(user_id):
    t = Teacher.query.filter_by(user_id=user_id).first()
    return t.id if t else None


# ==================== 我的指导学生/评阅学生 ====================

@teacher_bp.route('/students', methods=['GET'])
@jwt_required()
@role_required('teacher')
def my_students():
    teacher_id = get_teacher_id(get_jwt_identity())
    role_type = request.args.get('type', 'advisor')
    keyword = request.args.get('keyword')

    if role_type == 'advisor':
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
        item = p.to_dict()
        item['student_name'] = p.student.name if p.student else None
        item['student_no'] = p.student.student_id if p.student else None
        item['student_department'] = p.student.department if p.student else None
        item['status_name'] = p.current_status.name if p.current_status else None
        item['year'] = p.graduation_year.year if p.graduation_year else None

        last_sub = Submission.query.filter_by(project_id=p.id).order_by(
            Submission.version.desc()
        ).first()
        item['latest_submission'] = last_sub.to_dict() if last_sub else None

        result.append(item)

    return jsonify(result), 200


# ==================== 待评审列表 ====================

@teacher_bp.route('/pending-reviews', methods=['GET'])
@jwt_required()
@role_required('teacher')
def pending_reviews():
    teacher_id = get_teacher_id(get_jwt_identity())
    review_type = request.args.get('type', 'advisor')

    if review_type == 'advisor':
        projects = Project.query.filter_by(advisor_id=teacher_id).all()
    else:
        projects = Project.query.filter_by(reviewer_id=teacher_id).all()

    pending = []
    for p in projects:
        submissions = Submission.query.filter_by(project_id=p.id).order_by(
            Submission.version.desc()
        ).all()
        for sub in submissions:
            existing_review = Review.query.filter_by(
                submission_id=sub.id, reviewer_id=teacher_id,
                review_type=review_type,
            ).order_by(Review.revision_round.desc()).first()

            if not existing_review:
                pending.append({
                    'submission': sub.to_dict(),
                    'project': {
                        'id': p.id,
                        'title': p.title,
                        'student_name': p.student.name if p.student else None,
                        'student_no': p.student.student_id if p.student else None,
                    },
                    'status': '待评审',
                })
            elif existing_review.is_approved:
                pass
            else:
                latest_revision = Submission.query.filter_by(
                    project_id=p.id,
                ).order_by(Submission.version.desc()).first()
                if latest_revision and latest_revision.id > sub.id:
                    new_review = Review.query.filter_by(
                        submission_id=latest_revision.id, reviewer_id=teacher_id,
                        review_type=review_type,
                    ).first()
                    if not new_review:
                        pending.append({
                            'submission': latest_revision.to_dict(),
                            'project': {
                                'id': p.id,
                                'title': p.title,
                                'student_name': p.student.name if p.student else None,
                                'student_no': p.student.student_id if p.student else None,
                            },
                            'status': '待再次评审',
                        })

    return jsonify(pending), 200


# ==================== 执行评审 ====================

@teacher_bp.route('/reviews', methods=['POST'])
@jwt_required()
@role_required('teacher')
def submit_review():
    teacher_id = get_teacher_id(get_jwt_identity())
    data = request.get_json()

    submission_id = data['submission_id']
    review_type = data.get('review_type', 'advisor')

    existing = Review.query.filter_by(
        submission_id=submission_id, reviewer_id=teacher_id,
        review_type=review_type,
    ).order_by(Review.revision_round.desc()).first()

    revision_round = (existing.revision_round + 1) if existing else 1

    review = Review(
        submission_id=submission_id,
        reviewer_id=teacher_id,
        review_type=review_type,
        revision_round=revision_round,
        score=data.get('score'),
        comment=data.get('comment'),
        is_approved=data.get('is_approved', False),
    )
    db.session.add(review)

    sub = Submission.query.get(submission_id)
    if sub:
        sub.project.submission_count = max(
            sub.project.submission_count, sub.version
        )

    if data.get('is_approved') and review_type == 'advisor':
        project = sub.project
        sub_type = sub.submission_type

        NEXT_STATUS_MAP = {
            'draft': 'round1',
            'round1': 'final_check',
            'round2': 'final_check',
            'round3': 'final_check',
            'final_check': 'final_submission',
            'final': 'archived',
        }

        next_code = NEXT_STATUS_MAP.get(sub_type)
        if next_code:
            next_status = GraduationStatusDef.query.filter_by(code=next_code).first()
            if next_status:
                comment_text = {
                    'draft': '初稿评审通过，请学生提交一轮修改稿',
                    'round1': '一轮修改通过，进入查重定稿阶段',
                    'round2': '二轮修改通过，进入查重定稿阶段',
                    'round3': '三轮修改通过，进入查重定稿阶段',
                    'final_check': '查重定稿通过，进入最终提交阶段',
                    'final': '最终稿通过，项目已归档',
                }.get(sub_type, f'评审通过，进入{next_status.name}阶段')

                if sub_type in ('round1', 'round2', 'round3'):
                    comment_text = f'{next_status.name}阶段评审通过，进入查重定稿阶段'

                if sub_type == 'draft':
                    history = ProjectStatusHistory(
                        project_id=project.id,
                        from_status_id=project.current_status_id,
                        to_status_id=next_status.id,
                        operator_role='teacher',
                        operator_id=teacher_id,
                        comment='初稿评审通过，进入一轮修改阶段',
                    )
                    db.session.add(history)
                    project.current_status_id = next_status.id
                else:
                    history = ProjectStatusHistory(
                        project_id=project.id,
                        from_status_id=project.current_status_id,
                        to_status_id=next_status.id,
                        operator_role='teacher',
                        operator_id=teacher_id,
                        comment=comment_text,
                    )
                    db.session.add(history)
                    project.current_status_id = next_status.id

    elif not data.get('is_approved') and review_type == 'advisor':
        sub = Submission.query.get(submission_id)
        if sub:
            project = sub.project
            sub_type = sub.submission_type

            REJECT_NEXT_MAP = {
                'draft': None,
                'round1': 'round2',
                'round2': 'round3',
                'round3': None,
            }

            reject_comment = {
                'draft': '初稿需修改，请重新提交',
                'round1': '一轮修改未通过，进入二轮修改阶段',
                'round2': '二轮修改未通过，进入三轮修改阶段',
                'round3': '三轮修改未通过，请联系管理员',
            }.get(sub_type, '评审未通过，请修改后重新提交')

            next_code = REJECT_NEXT_MAP.get(sub_type)
            if next_code:
                next_status = GraduationStatusDef.query.filter_by(code=next_code).first()
                if next_status:
                    history = ProjectStatusHistory(
                        project_id=project.id,
                        from_status_id=project.current_status_id,
                        to_status_id=next_status.id,
                        operator_role='teacher',
                        operator_id=teacher_id,
                        comment=reject_comment,
                    )
                    db.session.add(history)
                    project.current_status_id = next_status.id
            else:
                if sub_type == 'draft':
                    pass
                elif sub_type == 'round3':
                    history = ProjectStatusHistory(
                        project_id=project.id,
                        from_status_id=project.current_status_id,
                        to_status_id=project.current_status_id,
                        operator_role='teacher',
                        operator_id=teacher_id,
                        comment='三轮修改未通过，无法继续提交',
                    )
                    db.session.add(history)

    db.session.commit()

    log_system(get_jwt_identity(), 'submit_review', 'review', review.id,
               f'{review_type}提交评审: {review.comment}')
    return jsonify({'msg': '评审提交成功', 'review_id': review.id}), 201


# ==================== 手动推进阶段 ====================

@teacher_bp.route('/projects/<int:project_id>/advance-stage', methods=['POST'])
@jwt_required()
@role_required('teacher')
def advance_stage(project_id):
    teacher_id = get_teacher_id(get_jwt_identity())
    project = Project.query.get_or_404(project_id)

    if project.advisor_id != teacher_id:
        return jsonify({'msg': '仅指导老师可以手动推进阶段'}), 403

    MANUAL_ADVANCE_MAP = {
        'first_draft': 'round1',
        'round1': 'final_check',
        'round2': 'final_check',
        'round3': 'final_check',
        'final_check': 'final_submission',
        'final_submission': 'defense',
        'defense': 'archived',
    }

    current_code = project.current_status.code if project.current_status else None
    next_code = MANUAL_ADVANCE_MAP.get(current_code)

    if not next_code:
        return jsonify({'msg': '当前阶段无法手动推进'}), 400

    next_status = GraduationStatusDef.query.filter_by(code=next_code).first()
    if not next_status:
        return jsonify({'msg': '下一阶段状态未定义，请联系管理员'}), 500

    history = ProjectStatusHistory(
        project_id=project.id,
        from_status_id=project.current_status_id,
        to_status_id=next_status.id,
        operator_role='teacher',
        operator_id=teacher_id,
        comment=f'手动推进阶段：{project.current_status.name} → {next_status.name}',
    )
    db.session.add(history)
    project.current_status_id = next_status.id
    db.session.commit()

    log_system(get_jwt_identity(), 'advance_stage', 'project', project.id,
               f'教师手动推进项目阶段到{next_status.name}')

    return jsonify({
        'msg': f'已推进到{next_status.name}阶段',
        'new_status': next_status.to_dict(),
    }), 200


# ==================== 撤回评审 ====================

@teacher_bp.route('/reviews/<int:review_id>/withdraw', methods=['POST'])
@jwt_required()
@role_required('teacher')
def withdraw_review(review_id):
    teacher_id = get_teacher_id(get_jwt_identity())
    review = Review.query.get_or_404(review_id)

    if review.reviewer_id != teacher_id:
        return jsonify({'msg': '只能撤回自己的评审'}), 403

    review.is_approved = False
    review.withdrawn_at = db.func.current_timestamp()
    db.session.commit()

    log_system(get_jwt_identity(), 'withdraw_review', 'review', review_id)
    return jsonify({'msg': '已撤回评审'}), 200


# ==================== 评审历史 ====================

@teacher_bp.route('/review-history', methods=['GET'])
@jwt_required()
@role_required('teacher')
def review_history():
    teacher_id = get_teacher_id(get_jwt_identity())
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    pagination = Review.query.filter_by(reviewer_id=teacher_id).order_by(
        Review.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    result = []
    for rv in pagination.items:
        item = rv.to_dict()
        sub = Submission.query.get(rv.submission_id)
        if sub:
            item['project_title'] = sub.project.title if sub.project else None
            item['student_name'] = sub.project.student.name if sub.project and sub.project.student else None
            item['file_name'] = sub.file_name
            item['version'] = sub.version
        result.append(item)

    return jsonify({
        'items': result,
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
    }), 200


# ==================== 获取单个项目的完整详情 ====================

@teacher_bp.route('/projects/<int:project_id>', methods=['GET'])
@jwt_required()
@role_required('teacher')
def get_project_detail(project_id):
    p = Project.query.get_or_404(project_id)
    item = p.to_dict()
    item['student_name'] = p.student.name if p.student else None
    item['student_no'] = p.student.student_id if p.student else None
    item['student_department'] = p.student.department if p.student else None
    item['advisor_name'] = p.advisor.name if p.advisor else None
    item['reviewer_name'] = p.reviewer.name if p.reviewer else None
    item['status_name'] = p.current_status.name if p.current_status else None
    item['year'] = p.graduation_year.year if p.graduation_year else None

    submissions = Submission.query.filter_by(project_id=p.id).order_by(
        Submission.version
    ).all()
    item['submissions'] = []
    for sub in submissions:
        s = sub.to_dict()
        s['reviews'] = [rv.to_dict() for rv in sub.reviews]
        item['submissions'].append(s)

    item['status_history'] = [h.to_dict() for h in p.status_histories]
    return jsonify(item), 200


# ==================== 下载论文 ====================

@teacher_bp.route('/submissions/<int:submission_id>/download', methods=['GET'])
@jwt_required()
@role_required('teacher')
def download_submission(submission_id):
    sub = Submission.query.get_or_404(submission_id)
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], sub.file_path)

    if not os.path.exists(file_path):
        return jsonify({'msg': '文件不存在'}), 404

    sub.downloaded_at = db.func.current_timestamp()
    sub.download_count = (sub.download_count or 0) + 1
    db.session.commit()

    log_system(get_jwt_identity(), 'download_submission', 'submission', submission_id)

    return send_file(
        file_path,
        as_attachment=True,
        download_name=sub.file_name,
    )
