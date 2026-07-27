import os
import time
from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from extensions import db
from models.user import User, Student
from models.project import Project, ProjectStatusHistory, GraduationStatusDef
from models.submission import Submission
from models.review import Review
from utils.decorators import role_required
from utils.helpers import log_system

student_bp = Blueprint('student', __name__)


def get_student_id(user_id):
    s = Student.query.filter_by(user_id=user_id).first()
    return s.id if s else None


ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'zip', 'rar'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


SUBMISSION_TYPE_MAP = {
    'first_draft': 'draft',
    'round1': 'round1',
    'round2': 'round2',
    'round3': 'round3',
    'final_check': 'final_check',
    'final': 'final',
}

# Allowed status codes for each submission type
ALLOWED_SUBMISSION_STAGES = {
    'draft': 'first_draft',
    'round1': 'round1',
    'round2': 'round2',
    'round3': 'round3',
    'final_check': 'final_check',
    'final': 'final_submission',
}


# ==================== 获取我的毕设项目信息 ====================

@student_bp.route('/my-project', methods=['GET'])
@jwt_required()
@role_required('student')
def my_project():
    student_id = get_student_id(get_jwt_identity())
    project = Project.query.filter_by(student_id=student_id).first()

    if not project:
        return jsonify({'msg': '暂无毕设项目，请联系管理员'}), 404

    item = project.to_dict()
    item['student_name'] = project.student.name if project.student else None
    item['student_no'] = project.student.student_id if project.student else None
    item['advisor_name'] = project.advisor.name if project.advisor else None
    item['advisor_title'] = project.advisor.title if project.advisor else None
    item['reviewer_name'] = project.reviewer.name if project.reviewer else None
    item['reviewer_title'] = project.reviewer.title if project.reviewer else None
    item['status_name'] = project.current_status.name if project.current_status else None
    item['status_code'] = project.current_status.code if project.current_status else None
    item['status_sort'] = project.current_status.sort_order if project.current_status else None
    item['year'] = project.graduation_year.year if project.graduation_year else None

    submissions = Submission.query.filter_by(project_id=project.id).order_by(
        Submission.version
    ).all()
    item['submissions'] = []
    for sub in submissions:
        s = sub.to_dict()
        s['reviews'] = [rv.to_dict() for rv in sub.reviews]
        item['submissions'].append(s)

    status_history = ProjectStatusHistory.query.filter_by(
        project_id=project.id
    ).order_by(ProjectStatusHistory.created_at).all()
    item['status_history'] = [h.to_dict() for h in status_history]

    return jsonify(item), 200


# ==================== 获取论文管理各阶段状态 ====================

@student_bp.route('/paper-status', methods=['GET'])
@jwt_required()
@role_required('student')
def paper_status():
    student_id = get_student_id(get_jwt_identity())
    project = Project.query.filter_by(student_id=student_id).first()

    if not project:
        return jsonify({'msg': '暂无毕设项目'}), 404

    current_code = project.current_status.code if project.current_status else None
    status_sort = project.current_status.sort_order if project.current_status else 0

    stages = ['first_draft', 'round1', 'round2', 'round3', 'final_check', 'final_submission']
    stage_names = {
        'first_draft': '初稿',
        'round1': '一轮修改',
        'round2': '二轮修改',
        'round3': '三轮修改',
        'final_check': '查重定稿',
        'final_submission': '最终提交',
    }

    stage_info = []
    for code in stages:
        stage_status = 'locked'
        stage_sort = GraduationStatusDef.query.filter_by(code=code).first().sort_order

        if status_sort > stage_sort:
            stage_status = 'completed'
        elif status_sort == stage_sort:
            last_sub = Submission.query.filter_by(
                project_id=project.id,
                submission_type=SUBMISSION_TYPE_MAP.get(code, code),
            ).order_by(Submission.version.desc()).first()

            if last_sub:
                review = Review.query.filter_by(
                    submission_id=last_sub.id
                ).order_by(Review.created_at.desc()).first()
                if review:
                    if review.is_approved:
                        stage_status = 'approved'
                    else:
                        stage_status = 'rejected'
                else:
                    stage_status = 'pending'
            else:
                stage_status = 'current'

        stage_info.append({
            'code': code,
            'name': stage_names.get(code, code),
            'status': stage_status,
        })

    return jsonify({
        'project_id': project.id,
        'current_status': current_code,
        'stages': stage_info,
    }), 200


# ==================== 按阶段提交论文 ====================

@student_bp.route('/submit-paper', methods=['POST'])
@jwt_required()
@role_required('student')
def submit_paper():
    student_id = get_student_id(get_jwt_identity())
    project = Project.query.filter_by(student_id=student_id).first()

    if not project:
        return jsonify({'msg': '暂无毕设项目'}), 404

    stage = request.form.get('stage', 'draft')
    if stage not in ALLOWED_SUBMISSION_STAGES:
        return jsonify({'msg': '不允许直接提交该阶段'}), 400

    submission_type = stage
    required_status_code = ALLOWED_SUBMISSION_STAGES[stage]
    required_status = GraduationStatusDef.query.filter_by(code=required_status_code).first()

    if not required_status:
        return jsonify({'msg': '阶段状态未定义'}), 400

    current_code = project.current_status.code if project.current_status else None

    if stage == 'draft' and current_code != 'first_draft':
        return jsonify({'msg': '当前不在初稿阶段，无法提交初稿'}), 400

    if stage in ('round1', 'round2', 'round3', 'final_check'):
        stage_order = {
            'round1': 'round1',
            'round2': 'round2',
            'round3': 'round3',
            'final_check': 'final_check',
        }
        expected_code = stage_order[stage]
        if current_code != expected_code:
            return jsonify({'msg': f'当前不在{stage}阶段，无法提交'}), 400

    if stage == 'final':
        if current_code != 'final_submission':
            return jsonify({'msg': '当前不在最终提交阶段'}), 400

    if 'file' not in request.files:
        return jsonify({'msg': '请选择文件'}), 400

    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'msg': '仅支持 pdf/doc/docx/zip/rar 格式'}), 400

    description = request.form.get('description', '')

    filename = secure_filename(file.filename)
    timestamp = str(int(time.time()))
    unique_name = f'{student_id}_{timestamp}_{filename}'

    rel_path = os.path.join(str(project.id), unique_name)
    abs_path = os.path.join(current_app.config['UPLOAD_FOLDER'], rel_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    file.save(abs_path)

    last_sub = Submission.query.filter_by(project_id=project.id).order_by(
        Submission.version.desc()
    ).first()
    new_version = (last_sub.version + 1) if last_sub else 1

    submission = Submission(
        project_id=project.id,
        version=new_version,
        submission_type=submission_type,
        file_name=file.filename,
        file_path=rel_path,
        file_size=os.path.getsize(abs_path),
        submitted_by=student_id,
        description=description,
    )
    db.session.add(submission)
    project.submission_count = new_version

    db.session.commit()

    log_system(get_jwt_identity(), 'submit_paper', 'submission', submission.id,
               f'提交{stage} v{new_version}')
    return jsonify({'msg': '提交成功', 'submission': submission.to_dict()}), 201


# ==================== 获取当前阶段待提交信息 ====================

@student_bp.route('/current-stage', methods=['GET'])
@jwt_required()
@role_required('student')
def current_stage():
    student_id = get_student_id(get_jwt_identity())
    project = Project.query.filter_by(student_id=student_id).first()

    if not project:
        return jsonify({'msg': '暂无毕设项目'}), 404

    current_code = project.current_status.code if project.current_status else None

    last_sub = Submission.query.filter_by(project_id=project.id).order_by(
        Submission.version.desc()
    ).first()

    result = {
        'project_id': project.id,
        'current_status_code': current_code,
        'current_status_name': project.current_status.name if project.current_status else None,
        'submission_count': project.submission_count,
        'max_submissions': project.max_submissions,
        'last_submission': None,
    }

    if last_sub:
        sub_data = last_sub.to_dict()
        sub_data['reviews'] = [rv.to_dict() for rv in last_sub.reviews]
        result['last_submission'] = sub_data

    return jsonify(result), 200


# ==================== 提交记录查看 ====================

@student_bp.route('/submissions', methods=['GET'])
@jwt_required()
@role_required('student')
def my_submissions():
    student_id = get_student_id(get_jwt_identity())
    project = Project.query.filter_by(student_id=student_id).first()
    if not project:
        return jsonify([]), 200

    submissions = Submission.query.filter_by(project_id=project.id).order_by(
        Submission.version.desc()
    ).all()

    result = []
    for sub in submissions:
        s = sub.to_dict()
        s['reviews'] = [rv.to_dict() for rv in sub.reviews]
        result.append(s)

    return jsonify(result), 200


# ==================== 学生下载自己的提交文件 ====================

@student_bp.route('/submissions/<int:submission_id>/download', methods=['GET'])
@jwt_required()
@role_required('student')
def download_my_submission(submission_id):
    student_id = get_student_id(get_jwt_identity())
    sub = Submission.query.get_or_404(submission_id)

    project = Project.query.get(sub.project_id)
    if not project or project.student_id != student_id:
        return jsonify({'msg': '无权下载该文件'}), 403

    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], sub.file_path)
    if not os.path.exists(file_path):
        return jsonify({'msg': '文件不存在'}), 404

    sub.downloaded_at = db.func.current_timestamp()
    sub.download_count = (sub.download_count or 0) + 1
    db.session.commit()

    return send_file(
        file_path,
        as_attachment=True,
        download_name=sub.file_name,
    )
