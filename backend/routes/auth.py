from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.user import User, Student, Teacher, Admin
from extensions import db
from utils.decorators import role_required
from utils.helpers import log_system

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/check-username', methods=['GET'])
def check_username():
    username = request.args.get('username', '').strip()
    role = request.args.get('role', '').strip()

    if not username or role not in ('student', 'teacher'):
        return jsonify({'available': False}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'available': False}), 200

    if role == 'student' and Student.query.filter_by(student_id=username).first():
        return jsonify({'available': False}), 200
    if role == 'teacher' and Teacher.query.filter_by(teacher_id=username).first():
        return jsonify({'available': False}), 200

    return jsonify({'available': True}), 200


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    role = data.get('role')

    if role not in ('student', 'teacher'):
        return jsonify({'msg': '角色必须是 student 或 teacher'}), 400

    if role == 'student':
        student_id = data.get('student_id', '').strip()
        name = data.get('name', '').strip()
        class_name = data.get('class_name', '').strip()
        major = data.get('major', '').strip()
        department = data.get('department', '').strip()
        password = data.get('password', '').strip()
        phone = data.get('phone', '').strip() or None
        email = data.get('email', '').strip() or None

        if not all([student_id, name, class_name, major, department, password]):
            return jsonify({'msg': '学号、姓名、班级、专业、学院、密码不能为空'}), 400

        if User.query.filter_by(username=student_id).first():
            return jsonify({'msg': '该学号已注册'}), 409
        if Student.query.filter_by(student_id=student_id).first():
            return jsonify({'msg': '该学号已注册'}), 409

        user = User(username=student_id, name=name, role='student')
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        student = Student(
            user_id=user.id,
            student_id=student_id,
            name=name,
            class_name=class_name,
            major=major,
            department=department,
            phone=phone,
            email=email,
        )
        db.session.add(student)

    elif role == 'teacher':
        teacher_id = data.get('teacher_id', '').strip()
        name = data.get('name', '').strip()
        department = data.get('department', '').strip()
        title = data.get('title', '').strip()
        password = data.get('password', '').strip()
        phone = data.get('phone', '').strip() or None
        email = data.get('email', '').strip() or None

        if not all([teacher_id, name, department, title, password]):
            return jsonify({'msg': '教师号、姓名、学院、职业、密码不能为空'}), 400

        if User.query.filter_by(username=teacher_id).first():
            return jsonify({'msg': '该教师号已注册'}), 409
        if Teacher.query.filter_by(teacher_id=teacher_id).first():
            return jsonify({'msg': '该教师号已注册'}), 409

        user = User(username=teacher_id, name=name, role='teacher')
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        teacher = Teacher(
            user_id=user.id,
            teacher_id=teacher_id,
            name=name,
            department=department,
            title=title,
            phone=phone,
            email=email,
        )
        db.session.add(teacher)

    db.session.commit()
    return jsonify({'msg': '注册成功'}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'msg': '用户名和密码不能为空'}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({'msg': '用户名或密码错误'}), 401

    if not user.is_active:
        return jsonify({'msg': '账号已被禁用'}), 403

    token = create_access_token(identity=str(user.id))
    user_info = user.to_dict()

    if user.role == 'student':
        student = Student.query.filter_by(user_id=user.id).first()
        if student:
            user_info['student_id'] = student.student_id
            user_info['student_no'] = student.student_id
            user_info['class_name'] = student.class_name
            user_info['major'] = student.major
            user_info['department'] = student.department
    elif user.role == 'teacher':
        teacher = Teacher.query.filter_by(user_id=user.id).first()
        if teacher:
            user_info['teacher_id'] = teacher.teacher_id
            user_info['teacher_no'] = teacher.teacher_id
            user_info['title'] = teacher.title
            user_info['department'] = teacher.department
    elif user.role == 'admin':
        admin = Admin.query.filter_by(user_id=user.id).first()
        if admin:
            user_info['admin_id'] = admin.id

    log_system(user.id, 'login', 'user', user.id, f'{user.role}用户登录')
    return jsonify({'token': token, 'user': user_info}), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'msg': '用户不存在'}), 404

    user_info = user.to_dict()
    if user.role == 'student':
        student = Student.query.filter_by(user_id=user.id).first()
        if student:
            user_info.update(student.to_dict())
    elif user.role == 'teacher':
        teacher = Teacher.query.filter_by(user_id=user.id).first()
        if teacher:
            user_info.update(teacher.to_dict())
    elif user.role == 'admin':
        admin = Admin.query.filter_by(user_id=user.id).first()
        if admin:
            user_info.update(admin.to_dict())

    return jsonify(user_info), 200


@auth_bp.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    user_id = get_jwt_identity()
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not old_password or not new_password:
        return jsonify({'msg': '旧密码和新密码不能为空'}), 400

    user = User.query.get(user_id)
    if not user.check_password(old_password):
        return jsonify({'msg': '旧密码错误'}), 400

    user.set_password(new_password)
    db.session.commit()
    log_system(user_id, 'change_password', 'user', user_id)
    return jsonify({'msg': '密码修改成功'}), 200
