from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.user import User, Student, Teacher, Admin
from models.project import GraduationYear, GraduationStatusDef, Project, ProjectStatusHistory
from models.submission import Submission
from models.review import Review
from models.system import ExportLog, SystemLog
from utils.decorators import role_required
from utils.helpers import log_system

admin_bp = Blueprint('admin', __name__)


def get_admin_id(user_id):
    admin = Admin.query.filter_by(user_id=user_id).first()
    return admin.id if admin else None


# ==================== 用户管理 ====================

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@role_required('admin')
def list_users():
    role = request.args.get('role')
    keyword = request.args.get('keyword')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = User.query
    if role:
        query = query.filter_by(role=role)
    if keyword:
        query = query.filter(
            db.or_(User.name.like(f'%{keyword}%'), User.username.like(f'%{keyword}%'))
        )

    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    result = []
    for u in pagination.items:
        info = u.to_dict()
        if u.role == 'student':
            s = Student.query.filter_by(user_id=u.id).first()
            if s:
                info.update(s.to_dict())
        elif u.role == 'teacher':
            t = Teacher.query.filter_by(user_id=u.id).first()
            if t:
                info.update(t.to_dict())
        elif u.role == 'admin':
            a = Admin.query.filter_by(user_id=u.id).first()
            if a:
                info.update(a.to_dict())
        result.append(info)

    return jsonify({
        'items': result,
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
    }), 200


@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    info = user.to_dict()
    if user.role == 'student':
        s = Student.query.filter_by(user_id=user.id).first()
        if s:
            info.update(s.to_dict())
    elif user.role == 'teacher':
        t = Teacher.query.filter_by(user_id=user.id).first()
        if t:
            info.update(t.to_dict())
    elif user.role == 'admin':
        a = Admin.query.filter_by(user_id=user.id).first()
        if a:
            info.update(a.to_dict())
    return jsonify(info), 200


@admin_bp.route('/users', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_user():
    data = request.get_json()
    role = data.get('role')

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'msg': '用户名已存在'}), 400

    user = User(
        username=data['username'],
        name=data['name'],
        role=role,
    )
    user.set_password(data.get('password', '123456'))
    db.session.add(user)
    db.session.flush()

    if role == 'student':
        if Student.query.filter_by(student_id=data['student_id']).first():
            db.session.rollback()
            return jsonify({'msg': '学号已存在'}), 400
        student = Student(
            user_id=user.id, student_id=data['student_id'], name=data['name'],
            class_name=data.get('class_name'), major=data.get('major'),
            department=data.get('department'), phone=data.get('phone'),
            email=data.get('email'),
        )
        db.session.add(student)
    elif role == 'teacher':
        if Teacher.query.filter_by(teacher_id=data['teacher_id']).first():
            db.session.rollback()
            return jsonify({'msg': '工号已存在'}), 400
        teacher = Teacher(
            user_id=user.id, teacher_id=data['teacher_id'], name=data['name'],
            department=data.get('department'), title=data.get('title'),
            phone=data.get('phone'), email=data.get('email'),
        )
        db.session.add(teacher)
    elif role == 'admin':
        admin = Admin(
            user_id=user.id, name=data['name'],
            phone=data.get('phone'), email=data.get('email'),
        )
        db.session.add(admin)

    db.session.commit()
    admin_id = get_admin_id(get_jwt_identity())
    log_system(get_jwt_identity(), 'create_user', 'user', user.id,
               f'创建{role}用户: {user.username}')
    return jsonify({'msg': '创建成功', 'user_id': user.id}), 201


@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
@role_required('admin')
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()

    if 'name' in data:
        user.name = data['name']
    if 'is_active' in data:
        user.is_active = data['is_active']

    if user.role == 'student':
        s = Student.query.filter_by(user_id=user.id).first()
        if s:
            for field in ['class_name', 'major', 'department', 'phone', 'email']:
                if field in data:
                    setattr(s, field, data[field])
    elif user.role == 'teacher':
        t = Teacher.query.filter_by(user_id=user.id).first()
        if t:
            for field in ['department', 'title', 'phone', 'email']:
                if field in data:
                    setattr(t, field, data[field])
    elif user.role == 'admin':
        a = Admin.query.filter_by(user_id=user.id).first()
        if a:
            for field in ['phone', 'email']:
                if field in data:
                    setattr(a, field, data[field])

    if 'password' in data and data['password']:
        user.set_password(data['password'])

    db.session.commit()
    log_system(get_jwt_identity(), 'update_user', 'user', user_id)
    return jsonify({'msg': '更新成功'}), 200


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    log_system(get_jwt_identity(), 'delete_user', 'user', user_id)
    return jsonify({'msg': '删除成功'}), 200


# ==================== 教师分配 ====================

@admin_bp.route('/assignments', methods=['GET'])
@jwt_required()
@role_required('admin')
def list_assignments():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    teacher_id = request.args.get('teacher_id', type=int)

    query = Project.query
    if teacher_id:
        query = query.filter(
            db.or_(Project.advisor_id == teacher_id, Project.reviewer_id == teacher_id)
        )

    pagination = query.order_by(Project.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    result = []
    for p in pagination.items:
        item = p.to_dict()
        item['student_name'] = p.student.name if p.student else None
        item['student_no'] = p.student.student_id if p.student else None
        item['advisor_name'] = p.advisor.name if p.advisor else None
        item['reviewer_name'] = p.reviewer.name if p.reviewer else None
        item['status_name'] = p.current_status.name if p.current_status else None
        item['year'] = p.graduation_year.year if p.graduation_year else None
        result.append(item)

    return jsonify({
        'items': result,
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
    }), 200


@admin_bp.route('/assignments/assign-advisor', methods=['POST'])
@jwt_required()
@role_required('admin')
def assign_advisor():
    data = request.get_json()
    student_id = data.get('student_id')
    teacher_id = data.get('teacher_id')

    project = Project.query.filter_by(student_id=student_id).first()
    if not project:
        return jsonify({'msg': '该学生暂无毕设项目'}), 404

    project.advisor_id = teacher_id
    db.session.commit()

    teacher = Teacher.query.get(teacher_id)
    student = Student.query.get(student_id)
    log_system(get_jwt_identity(), 'assign_advisor', 'project', project.id,
               f'将学生{student.name}分配给指导老师{teacher.name}')
    return jsonify({'msg': '分配成功'}), 200


@admin_bp.route('/assignments/assign-reviewer', methods=['POST'])
@jwt_required()
@role_required('admin')
def assign_reviewer():
    data = request.get_json()
    student_id = data.get('student_id')
    teacher_id = data.get('teacher_id')

    project = Project.query.filter_by(student_id=student_id).first()
    if not project:
        return jsonify({'msg': '该学生暂无毕设项目'}), 404

    project.reviewer_id = teacher_id
    db.session.commit()

    teacher = Teacher.query.get(teacher_id)
    student = Student.query.get(student_id)
    log_system(get_jwt_identity(), 'assign_reviewer', 'project', project.id,
               f'将学生{student.name}分配给评阅老师{teacher.name}')
    return jsonify({'msg': '分配成功'}), 200


# ==================== 毕设状态管理 ====================

@admin_bp.route('/status-defs', methods=['GET'])
@jwt_required()
@role_required('admin')
def list_status_defs():
    defs = GraduationStatusDef.query.order_by(GraduationStatusDef.sort_order).all()
    return jsonify([d.to_dict() for d in defs]), 200


@admin_bp.route('/status-defs', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_status_def():
    data = request.get_json()
    if GraduationStatusDef.query.filter_by(code=data['code']).first():
        return jsonify({'msg': '状态代码已存在'}), 400

    sd = GraduationStatusDef(
        name=data['name'], code=data['code'],
        sort_order=data.get('sort_order', 0),
    )
    db.session.add(sd)
    db.session.commit()
    log_system(get_jwt_identity(), 'create_status_def', 'graduation_status_def', sd.id)
    return jsonify({'msg': '创建成功', 'id': sd.id}), 201


@admin_bp.route('/status-defs/<int:sd_id>', methods=['PUT'])
@jwt_required()
@role_required('admin')
def update_status_def(sd_id):
    sd = GraduationStatusDef.query.get_or_404(sd_id)
    data = request.get_json()
    for field in ['name', 'code', 'sort_order', 'is_active']:
        if field in data:
            setattr(sd, field, data[field])
    db.session.commit()
    log_system(get_jwt_identity(), 'update_status_def', 'graduation_status_def', sd_id)
    return jsonify({'msg': '更新成功'}), 200


@admin_bp.route('/status-defs/<int:sd_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin')
def delete_status_def(sd_id):
    sd = GraduationStatusDef.query.get_or_404(sd_id)
    if Project.query.filter_by(current_status_id=sd_id).first():
        return jsonify({'msg': '该状态正在使用中，无法删除'}), 400
    db.session.delete(sd)
    db.session.commit()
    log_system(get_jwt_identity(), 'delete_status_def', 'graduation_status_def', sd_id)
    return jsonify({'msg': '删除成功'}), 200


# ==================== 毕设年份管理 ====================

@admin_bp.route('/graduation-years', methods=['GET'])
@jwt_required()
@role_required('admin')
def list_years():
    years = GraduationYear.query.order_by(GraduationYear.year.desc()).all()
    return jsonify([y.to_dict() for y in years]), 200


@admin_bp.route('/graduation-years', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_year():
    data = request.get_json()
    if GraduationYear.query.filter_by(year=data['year']).first():
        return jsonify({'msg': '年份已存在'}), 400
    y = GraduationYear(year=data['year'])
    db.session.add(y)
    db.session.commit()
    return jsonify({'msg': '创建成功', 'id': y.id}), 201


@admin_bp.route('/graduation-years/<int:yid>', methods=['PUT'])
@jwt_required()
@role_required('admin')
def update_year(yid):
    y = GraduationYear.query.get_or_404(yid)
    data = request.get_json()
    if 'year' in data:
        y.year = data['year']
    if 'is_active' in data:
        y.is_active = data['is_active']
    db.session.commit()
    return jsonify({'msg': '更新成功'}), 200


@admin_bp.route('/graduation-years/<int:yid>', methods=['DELETE'])
@jwt_required()
@role_required('admin')
def delete_year(yid):
    y = GraduationYear.query.get_or_404(yid)
    if Project.query.filter_by(graduation_year_id=yid).first():
        return jsonify({'msg': '该年份正在使用中，无法删除'}), 400
    db.session.delete(y)
    db.session.commit()
    return jsonify({'msg': '删除成功'}), 200


# ==================== 提交限制 ====================

@admin_bp.route('/projects/<int:project_id>/submission-limit', methods=['PUT'])
@jwt_required()
@role_required('admin')
def set_submission_limit(project_id):
    project = Project.query.get_or_404(project_id)
    data = request.get_json()
    project.max_submissions = data.get('max_submissions', project.max_submissions)
    db.session.commit()
    log_system(get_jwt_identity(), 'set_submission_limit', 'project', project_id)
    return jsonify({'msg': '设置成功'}), 200


# ==================== 交互过程 ====================

@admin_bp.route('/projects/<int:project_id>/interactions', methods=['GET'])
@jwt_required()
@role_required('admin')
def project_interactions(project_id):
    project = Project.query.get_or_404(project_id)

    status_logs = ProjectStatusHistory.query.filter_by(project_id=project_id).order_by(
        ProjectStatusHistory.created_at
    ).all()

    submissions = Submission.query.filter_by(project_id=project_id).order_by(
        Submission.version
    ).all()

    interactions = []
    for sl in status_logs:
        interactions.append({
            'type': 'status_change',
            'time': sl.created_at.isoformat() if sl.created_at else None,
            'content': f'状态变更: {sl.from_status.name if sl.from_status else "无"} → {sl.to_status.name}',
            'operator_role': sl.operator_role,
            'comment': sl.comment,
        })

    for sub in submissions:
        interactions.append({
            'type': 'submission',
            'time': sub.created_at.isoformat() if sub.created_at else None,
            'version': sub.version,
            'submission_type': sub.submission_type,
            'file_name': sub.file_name,
            'description': sub.description,
        })
        for rv in sub.reviews:
            interactions.append({
                'type': 'review',
                'time': rv.created_at.isoformat() if rv.created_at else None,
                'reviewer_name': rv.reviewer.name if rv.reviewer else None,
                'review_type': rv.review_type,
                'score': float(rv.score) if rv.score else None,
                'comment': rv.comment,
                'is_approved': rv.is_approved,
            })

    interactions.sort(key=lambda x: x.get('time', ''))
    return jsonify(interactions), 200


# ==================== 导出 ====================

@admin_bp.route('/export/evaluation-forms', methods=['POST'])
@jwt_required()
@role_required('admin')
def export_evaluation_forms():
    data = request.get_json()
    project_ids = data.get('project_ids', [])

    query = Project.query
    if project_ids:
        query = query.filter(Project.id.in_(project_ids))

    projects = query.all()
    export_data = []
    for p in projects:
        submissions = Submission.query.filter_by(project_id=p.id).all()
        for sub in submissions:
            for rv in sub.reviews:
                export_data.append({
                    'student_name': p.student.name if p.student else None,
                    'student_no': p.student.student_id if p.student else None,
                    'title': p.title,
                    'version': sub.version,
                    'reviewer': rv.reviewer.name if rv.reviewer else None,
                    'review_type': rv.review_type,
                    'score': float(rv.score) if rv.score else None,
                    'comment': rv.comment,
                    'is_approved': rv.is_approved,
                    'reviewed_at': rv.created_at.isoformat() if rv.created_at else None,
                })

    admin_id = get_admin_id(get_jwt_identity())
    el = ExportLog(admin_id=admin_id, export_type='evaluation_form', filters_json=data)
    db.session.add(el)
    db.session.commit()
    log_system(get_jwt_identity(), 'export_evaluation_forms', 'export_log', el.id)

    return jsonify({'data': export_data, 'count': len(export_data)}), 200


@admin_bp.route('/export/thesis-materials', methods=['POST'])
@jwt_required()
@role_required('admin')
def export_thesis_materials():
    data = request.get_json()
    project_ids = data.get('project_ids', [])

    query = Project.query
    if project_ids:
        query = query.filter(Project.id.in_(project_ids))

    projects = query.all()
    export_data = []
    for p in projects:
        submissions = Submission.query.filter_by(project_id=p.id).order_by(
            Submission.version.desc()
        ).all()
        latest = submissions[0] if submissions else None
        export_data.append({
            'student_name': p.student.name if p.student else None,
            'student_no': p.student.student_id if p.student else None,
            'title': p.title,
            'advisor': p.advisor.name if p.advisor else None,
            'status': p.current_status.name if p.current_status else None,
            'latest_version': latest.version if latest else None,
            'latest_file': latest.file_name if latest else None,
            'latest_file_path': latest.file_path if latest else None,
            'submissions': [s.to_dict() for s in submissions],
        })

    admin_id = get_admin_id(get_jwt_identity())
    el = ExportLog(admin_id=admin_id, export_type='thesis_materials', filters_json=data)
    db.session.add(el)
    db.session.commit()
    log_system(get_jwt_identity(), 'export_thesis_materials', 'export_log', el.id)

    return jsonify({'data': export_data, 'count': len(export_data)}), 200


# ==================== 操作日志 ====================

@admin_bp.route('/logs', methods=['GET'])
@jwt_required()
@role_required('admin')
def list_logs():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    pagination = SystemLog.query.order_by(SystemLog.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    items = []
    for log in pagination.items:
        item = log.to_dict()
        item['username'] = log.user.username if log.user else None
        items.append(item)

    return jsonify({
        'items': items,
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
    }), 200


# ==================== 总览统计 ====================

@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@role_required('admin')
def dashboard():
    total_students = Student.query.count()
    total_teachers = Teacher.query.count()
    total_projects = Project.query.count()
    total_submissions = Submission.query.count()

    status_stats = db.session.query(
        GraduationStatusDef.name, db.func.count(Project.id)
    ).join(Project, GraduationStatusDef.id == Project.current_status_id
    ).group_by(GraduationStatusDef.id).all()

    return jsonify({
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_projects': total_projects,
        'total_submissions': total_submissions,
        'status_stats': [{'name': s, 'count': c} for s, c in status_stats],
    }), 200


# ==================== 项目列表（管理员视角） ====================

@admin_bp.route('/projects', methods=['GET'])
@jwt_required()
@role_required('admin')
def list_projects():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status_id = request.args.get('status_id', type=int)
    keyword = request.args.get('keyword')

    query = Project.query
    if status_id:
        query = query.filter_by(current_status_id=status_id)
    if keyword:
        query = query.join(Student).filter(
            db.or_(
                Project.title.like(f'%{keyword}%'),
                Student.name.like(f'%{keyword}%'),
                Student.student_id.like(f'%{keyword}%'),
            )
        )

    pagination = query.order_by(Project.updated_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    result = []
    for p in pagination.items:
        item = p.to_dict()
        item['student_name'] = p.student.name if p.student else None
        item['student_no'] = p.student.student_id if p.student else None
        item['advisor_name'] = p.advisor.name if p.advisor else None
        item['reviewer_name'] = p.reviewer.name if p.reviewer else None
        item['status_name'] = p.current_status.name if p.current_status else None
        item['year'] = p.graduation_year.year if p.graduation_year else None
        result.append(item)

    return jsonify({
        'items': result,
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
    }), 200


@admin_bp.route('/projects/<int:project_id>', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_project(project_id):
    p = Project.query.get_or_404(project_id)
    item = p.to_dict()
    item['student_name'] = p.student.name if p.student else None
    item['student_no'] = p.student.student_id if p.student else None
    item['advisor_name'] = p.advisor.name if p.advisor else None
    item['reviewer_name'] = p.reviewer.name if p.reviewer else None
    item['status_name'] = p.current_status.name if p.current_status else None
    item['year'] = p.graduation_year.year if p.graduation_year else None
    item['submissions'] = [s.to_dict() for s in p.submissions]
    for s in item['submissions']:
        sub = Submission.query.get(s['id'])
        if sub:
            s['reviews'] = [rv.to_dict() for rv in sub.reviews]
    return jsonify(item), 200


# ==================== 获取教师列表（用于下拉选择） ====================

@admin_bp.route('/teachers/list', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_teacher_list():
    teachers = Teacher.query.all()
    return jsonify([t.to_dict() for t in teachers]), 200


@admin_bp.route('/students/list', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_student_list():
    students = Student.query.all()
    return jsonify([s.to_dict() for s in students]), 200


# ==================== 创建项目（管理员） ====================

@admin_bp.route('/projects', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_project():
    data = request.get_json()
    project = Project(
        student_id=data['student_id'],
        title=data['title'],
        graduation_year_id=data['graduation_year_id'],
        description=data.get('description'),
        advisor_id=data['advisor_id'],
        reviewer_id=data.get('reviewer_id'),
        current_status_id=data.get('current_status_id', 1),
        max_submissions=data.get('max_submissions', 5),
    )
    db.session.add(project)
    db.session.flush()

    history = ProjectStatusHistory(
        project_id=project.id,
        from_status_id=None,
        to_status_id=project.current_status_id,
        operator_role='admin',
        operator_id=get_admin_id(get_jwt_identity()),
        comment='管理员创建项目',
    )
    db.session.add(history)
    db.session.commit()

    log_system(get_jwt_identity(), 'create_project', 'project', project.id)
    return jsonify({'msg': '创建成功', 'project_id': project.id}), 201


@admin_bp.route('/projects/<int:project_id>', methods=['PUT'])
@jwt_required()
@role_required('admin')
def update_project(project_id):
    p = Project.query.get_or_404(project_id)
    data = request.get_json()
    for field in ['title', 'description', 'advisor_id', 'reviewer_id',
                  'current_status_id', 'max_submissions', 'graduation_year_id']:
        if field in data:
            setattr(p, field, data[field])
    if 'status_id' in data and data['status_id'] != p.current_status_id:
        history = ProjectStatusHistory(
            project_id=p.id,
            from_status_id=p.current_status_id,
            to_status_id=data['status_id'],
            operator_role='admin',
            operator_id=get_admin_id(get_jwt_identity()),
            comment='管理员修改项目状态',
        )
        db.session.add(history)
        p.current_status_id = data['status_id']

    db.session.commit()
    log_system(get_jwt_identity(), 'update_project', 'project', project_id)
    return jsonify({'msg': '更新成功'}), 200


@admin_bp.route('/projects/<int:project_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin')
def delete_project(project_id):
    p = Project.query.get_or_404(project_id)
    db.session.delete(p)
    db.session.commit()
    log_system(get_jwt_identity(), 'delete_project', 'project', project_id)
    return jsonify({'msg': '删除成功'}), 200
