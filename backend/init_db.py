from app import create_app
from extensions import db
from models.user import User, Student, Teacher, Admin
from models.project import GraduationYear, GraduationStatusDef, Project, ProjectStatusHistory
from models.submission import Submission
from models.review import Review
from models.system import ExportLog, SystemLog
from models.notification import Notification, NotificationRecipient
from models.topic import Topic, TopicSelection

app = create_app()

with app.app_context():
    print('正在删除所有表...')
    db.drop_all()

    print('正在创建所有表...')
    db.create_all()

    print('正在插入种子数据...')

    # 1. 状态字典
    statuses = [
        ('选题', 'topic_selection', 1),
        ('初稿', 'first_draft', 2),
        ('一轮修改', 'round1', 3),
        ('二轮修改', 'round2', 4),
        ('三轮修改', 'round3', 5),
        ('查重定稿', 'final_check', 6),
        ('最终提交', 'final_submission', 7),
        ('答辩', 'defense', 8),
        ('已归档', 'archived', 9),
    ]
    status_map = {}
    for name, code, sort in statuses:
        s = GraduationStatusDef(name=name, code=code, sort_order=sort)
        db.session.add(s)
        db.session.flush()
        status_map[code] = s.id

    # 2. 年份
    y1 = GraduationYear(year='2024-2025', is_active=True)
    y2 = GraduationYear(year='2025-2026', is_active=True)
    y3 = GraduationYear(year='2026-2027', is_active=False)
    db.session.add_all([y1, y2, y3])
    db.session.flush()

    # 3. 管理员
    admin_user = User(username='admin', name='系统管理员', role='admin')
    admin_user.set_password('admin123')
    db.session.add(admin_user)
    db.session.flush()
    admin = Admin(user_id=admin_user.id, name='系统管理员', phone='13800138000',
                  email='admin@graduation.edu.cn')
    db.session.add(admin)

    # 4. 教师
    teacher_data = [
        ('T001', '张教授', '计算机科学与技术学院', '教授'),
        ('T002', '李教授', '软件工程学院', '教授'),
        ('T003', '王副教授', '计算机科学与技术学院', '副教授'),
        ('T004', '赵副教授', '人工智能学院', '副教授'),
        ('T005', '陈讲师', '软件工程学院', '讲师'),
    ]
    teacher_map = {}
    for tid, tname, dept, title in teacher_data:
        u = User(username=tid, name=tname, role='teacher')
        u.set_password('123456')
        db.session.add(u)
        db.session.flush()
        t = Teacher(user_id=u.id, teacher_id=tid, name=tname,
                    department=dept, title=title)
        db.session.add(t)
        db.session.flush()
        teacher_map[tid] = t.id

    # 5. 学生
    student_data = [
        ('S202101', '张三', '计科2101班', '计算机科学与技术', '计算机科学与技术学院'),
        ('S202102', '李四', '计科2101班', '计算机科学与技术', '计算机科学与技术学院'),
        ('S202103', '王五', '软件2102班', '软件工程', '软件工程学院'),
        ('S202104', '赵六', '软件2102班', '软件工程', '软件工程学院'),
        ('S202105', '孙七', '计科2103班', '计算机科学与技术', '计算机科学与技术学院'),
        ('S202106', '周八', '人工智能2101班', '人工智能', '人工智能学院'),
        ('S202107', '吴九', '人工智能2101班', '人工智能', '人工智能学院'),
        ('S202108', '郑十', '计科2103班', '计算机科学与技术', '计算机科学与技术学院'),
    ]
    student_map = {}
    for sid, sname, cls, major, dept in student_data:
        u = User(username=sid, name=sname, role='student')
        u.set_password('123456')
        db.session.add(u)
        db.session.flush()
        s = Student(user_id=u.id, student_id=sid, name=sname,
                    class_name=cls, major=major, department=dept)
        db.session.add(s)
        db.session.flush()
        student_map[sid] = s.id

    # 6. 教师发布选题
    topic_data = [
        (teacher_map['T001'], '基于深度学习的图像识别系统研究与实现',
         '研究深度学习在图像识别领域的应用，设计并实现一个图像识别系统', 2),
        (teacher_map['T001'], '智慧校园学生管理系统的设计与实现',
         '设计一套面向智慧校园的学生管理系统，包含学籍、选课、成绩等模块', 2),
        (teacher_map['T002'], '基于区块链的毕业设计管理系统',
         '利用区块链技术设计去中心化的毕业设计管理平台', 1),
        (teacher_map['T002'], '面向小白的Python编程辅助平台',
         '开发一个帮助编程初学者学习Python的交互式辅助平台', 2),
        (teacher_map['T003'], '基于Vue3的在线考试系统设计与实现',
         '使用Vue3框架开发一个功能完善的在线考试系统', 2),
        (teacher_map['T003'], '基于Flask的实验室设备管理系统',
         '使用Flask框架开发实验室设备预约与管理系统', 1),
        (teacher_map['T004'], '校园二手交易平台的设计与实现',
         '设计一个面向校园的二手物品交易平台', 2),
        (teacher_map['T004'], '基于推荐算法的课程选课系统',
         '基于协同过滤算法实现智能课程推荐选课系统', 2),
        (teacher_map['T005'], '基于微服务的电商平台后端设计',
         '使用微服务架构设计一个电商平台后端系统', 1),
        (teacher_map['T005'], '人工智能在医疗诊断中的应用研究',
         '研究AI技术在医疗影像诊断中的辅助应用', 1),
    ]
    topic_map = {}
    for tid, title, desc, max_stu in topic_data:
        t = Topic(teacher_id=tid, title=title, description=desc, max_students=max_stu)
        db.session.add(t)
        db.session.flush()
        topic_map[title] = t.id

    # 7. 学生选题记录
    student_topics = [
        (student_map['S202101'], topic_map['基于深度学习的图像识别系统研究与实现'],
         '基于深度学习的图像识别系统研究与实现', None, 'select', 'approved'),
        (student_map['S202102'], topic_map['智慧校园学生管理系统的设计与实现'],
         '智慧校园学生管理系统的设计与实现', None, 'select', 'approved'),
        (student_map['S202103'], topic_map['基于区块链的毕业设计管理系统'],
         '基于区块链的毕业设计管理系统', None, 'select', 'approved'),
        (student_map['S202104'], topic_map['面向小白的Python编程辅助平台'],
         '面向小白的Python编程辅助平台', None, 'select', 'approved'),
        (student_map['S202105'], topic_map['基于Vue3的在线考试系统设计与实现'],
         '基于Vue3的在线考试系统设计与实现', None, 'select', 'approved'),
        (student_map['S202106'], topic_map['基于Flask的实验室设备管理系统'],
         '基于Flask的实验室设备管理系统', None, 'select', 'approved'),
        (student_map['S202107'], topic_map['校园二手交易平台的设计与实现'],
         '校园二手交易平台的设计与实现', None, 'select', 'approved'),
        (student_map['S202108'], topic_map['基于推荐算法的课程选课系统'],
         '基于推荐算法的课程选课系统', None, 'select', 'pending'),
    ]
    for sid, top_id, title, desc, stype, status in student_topics:
        ts = TopicSelection(student_id=sid, topic_id=top_id, title=title,
                            description=desc, type=stype, status=status)
        db.session.add(ts)
    db.session.flush()

    # 8. 项目
    projects_data = [
        (student_map['S202101'], '基于深度学习的图像识别系统研究与实现',
         y1.id, teacher_map['T001'], teacher_map['T003'], status_map['final_check'], 5, 2),
        (student_map['S202102'], '智慧校园学生管理系统的设计与实现',
         y1.id, teacher_map['T001'], teacher_map['T004'], status_map['round1'], 5, 1),
        (student_map['S202103'], '基于区块链的毕业设计管理系统',
         y1.id, teacher_map['T002'], teacher_map['T005'], status_map['final_check'], 5, 3),
        (student_map['S202104'], '面向小白的Python编程辅助平台',
         y1.id, teacher_map['T002'], teacher_map['T003'], status_map['final_check'], 5, 1),
        (student_map['S202105'], '基于Vue3的在线考试系统设计与实现',
         y1.id, teacher_map['T003'], teacher_map['T005'], status_map['final_check'], 5, 1),
        (student_map['S202106'], '基于Flask的实验室设备管理系统',
         y1.id, teacher_map['T004'], teacher_map['T001'], status_map['first_draft'], 5, 0),
        (student_map['S202107'], '校园二手交易平台的设计与实现',
         y1.id, teacher_map['T005'], teacher_map['T002'], status_map['topic_selection'], 5, 0),
        (student_map['S202108'], '基于推荐算法的课程选课系统',
         y1.id, teacher_map['T003'], teacher_map['T004'], status_map['topic_selection'], 5, 0),
    ]
    project_ids = []
    for sid, title, yid, aid, rid, stid, maxsub, subcnt in projects_data:
        p = Project(student_id=sid, title=title, graduation_year_id=yid,
                    advisor_id=aid, reviewer_id=rid, current_status_id=stid,
                    max_submissions=maxsub, submission_count=subcnt)
        db.session.add(p)
        db.session.flush()
        project_ids.append(p.id)

    # 9. 状态变更历史
    status_history_data = [
        (project_ids[0], None, status_map['topic_selection'], 'student', student_map['S202101'], '选题审核通过，进入初稿阶段'),
        (project_ids[0], status_map['topic_selection'], status_map['first_draft'], 'teacher', teacher_map['T001'], '选题审核通过，进入初稿阶段'),
        (project_ids[0], status_map['first_draft'], status_map['round1'], 'student', student_map['S202101'], '提交初稿，进入一轮修改阶段'),
        (project_ids[0], status_map['round1'], status_map['final_check'], 'teacher', teacher_map['T001'], '一轮修改通过，进入查重定稿阶段'),
        (project_ids[1], None, status_map['topic_selection'], 'student', student_map['S202102'], '选题审核通过，进入初稿阶段'),
        (project_ids[1], status_map['topic_selection'], status_map['first_draft'], 'teacher', teacher_map['T001'], '选题审核通过，进入初稿阶段'),
        (project_ids[1], status_map['first_draft'], status_map['round1'], 'teacher', teacher_map['T001'], '初稿评审通过，进入一轮修改阶段'),
        (project_ids[2], None, status_map['topic_selection'], 'student', student_map['S202103'], '选题审核通过，进入初稿阶段'),
        (project_ids[2], status_map['topic_selection'], status_map['first_draft'], 'teacher', teacher_map['T002'], '选题审核通过，进入初稿阶段'),
        (project_ids[2], status_map['first_draft'], status_map['round1'], 'student', student_map['S202103'], '提交初稿，进入一轮修改阶段'),
        (project_ids[2], status_map['round1'], status_map['round2'], 'teacher', teacher_map['T002'], '一轮未通过，进入二轮修改阶段'),
        (project_ids[2], status_map['round2'], status_map['final_check'], 'teacher', teacher_map['T002'], '二轮修改通过，进入查重定稿阶段'),
        (project_ids[3], None, status_map['topic_selection'], 'student', student_map['S202104'], '选题审核通过，进入初稿阶段'),
        (project_ids[3], status_map['topic_selection'], status_map['first_draft'], 'teacher', teacher_map['T002'], '选题审核通过，进入初稿阶段'),
        (project_ids[3], status_map['first_draft'], status_map['final_check'], 'teacher', teacher_map['T002'], '初稿已评审通过，进入查重定稿阶段'),
        (project_ids[4], None, status_map['topic_selection'], 'student', student_map['S202105'], '选题审核通过，进入初稿阶段'),
        (project_ids[4], status_map['topic_selection'], status_map['first_draft'], 'teacher', teacher_map['T003'], '选题审核通过，进入初稿阶段'),
        (project_ids[4], status_map['first_draft'], status_map['final_check'], 'teacher', teacher_map['T003'], '初稿已评审通过，进入查重定稿阶段'),
    ]
    for pid, from_sid, to_sid, op_role, op_id, comment in status_history_data:
        h = ProjectStatusHistory(project_id=pid, from_status_id=from_sid,
                                 to_status_id=to_sid, operator_role=op_role,
                                 operator_id=op_id, comment=comment)
        db.session.add(h)

    # 10. 提交记录
    sub_data = [
        (project_ids[0], 1, 'draft', '毕设_张三_初稿_v1.pdf', '1/张三_初稿_v1.pdf',
         2048000, student_map['S202101'], '初稿提交'),
        (project_ids[0], 2, 'round1', '毕设_张三_一轮_v2.pdf', '1/张三_一轮_v2.pdf',
         2150000, student_map['S202101'], '一轮修改稿'),
        (project_ids[1], 1, 'draft', '毕设_李四_初稿_v1.pdf', '2/李四_初稿_v1.pdf',
         1024000, student_map['S202102'], '初稿提交'),
        (project_ids[2], 1, 'draft', '毕设_王五_初稿_v1.pdf', '3/王五_初稿_v1.pdf',
         1800000, student_map['S202103'], '初稿提交'),
        (project_ids[2], 2, 'round1', '毕设_王五_一轮_v2.pdf', '3/王五_一轮_v2.pdf',
         1900000, student_map['S202103'], '一轮修改稿'),
        (project_ids[2], 3, 'round2', '毕设_王五_二轮_v3.pdf', '3/王五_二轮_v3.pdf',
         1950000, student_map['S202103'], '二轮修改稿'),
        (project_ids[3], 1, 'draft', '毕设_赵六_初稿_v1.pdf', '4/赵六_初稿_v1.pdf',
         2200000, student_map['S202104'], '初稿提交'),
        (project_ids[4], 1, 'draft', '毕设_孙七_初稿_v1.pdf', '5/孙七_初稿_v1.pdf',
         1600000, student_map['S202105'], '初稿提交'),
    ]
    sub_map = {}
    for pid, ver, stype, fname, fpath, fsize, submitter, desc in sub_data:
        sub = Submission(project_id=pid, version=ver, submission_type=stype,
                         file_name=fname, file_path=fpath, file_size=fsize,
                         submitted_by=submitter, description=desc)
        db.session.add(sub)
        db.session.flush()
        sub_map[(pid, ver)] = sub.id

    # 11. 评审记录
    review_data = [
        (sub_map[(project_ids[0], 1)], teacher_map['T001'], 'advisor', 1, 75.00,
         '初稿结构需要调整，第三章内容不够充实', False),
        (sub_map[(project_ids[0], 2)], teacher_map['T001'], 'advisor', 2, 85.00,
         '一轮修改后基本符合要求，进入查重定稿阶段', True),
        (sub_map[(project_ids[1], 1)], teacher_map['T001'], 'advisor', 1, 80.00,
         '初稿内容比较完整，可以进入一轮修改', True),
        (sub_map[(project_ids[2], 1)], teacher_map['T002'], 'advisor', 1, 70.00,
         '初稿内容完整但缺乏实验数据支撑', False),
        (sub_map[(project_ids[2], 2)], teacher_map['T002'], 'advisor', 2, 78.00,
         '一轮修改后仍有格式问题', False),
        (sub_map[(project_ids[2], 3)], teacher_map['T002'], 'advisor', 3, 88.00,
         '二轮修改后达到要求，进入查重定稿阶段', True),
    ]
    for sub_id, rev_id, rtype, rnd, score, comment, approved in review_data:
        rv = Review(submission_id=sub_id, reviewer_id=rev_id, review_type=rtype,
                    revision_round=rnd, score=score, comment=comment,
                    is_approved=approved)
        db.session.add(rv)

    db.session.commit()
    print('种子数据插入完成!')
    print(f'  管理员: admin / admin123')
    print(f'  教师:   T001-T005 / 123456')
    print(f'  学生:   S202101-S202108 / 123456')
