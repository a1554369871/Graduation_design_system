USE Graduation_Design_System;

-- ==========================================
-- 1. 毕设状态字典
-- ==========================================
INSERT INTO graduation_status_defs (name, code, sort_order) VALUES
('选题',          'topic_selection',    1),
('初稿',          'first_draft',        2),
('一轮修改',      'round1',             3),
('二轮修改',      'round2',             4),
('三轮修改',      'round3',             5),
('查重定稿',      'final_check',        6),
('最终提交',      'final_submission',   7),
('答辩',          'defense',            8),
('已归档',        'archived',           9);

-- ==========================================
-- 2. 毕设年份
-- ==========================================
INSERT INTO graduation_years (year, is_active) VALUES
('2024-2025', TRUE),
('2025-2026', TRUE),
('2026-2027', FALSE);

-- ==========================================
-- 3. 管理员
-- ==========================================
INSERT INTO users (username, password_hash, name, role) VALUES
('admin', 'pbkdf2:sha256:600000$salted$hash_will_be_updated_by_code', '系统管理员', 'admin');

INSERT INTO admins (user_id, name, phone, email) VALUES
(1, '系统管理员', '13800138000', 'admin@graduation.edu.cn');

-- ==========================================
-- 4. 教师
-- ==========================================
INSERT INTO users (username, password_hash, name, role) VALUES
('T001', 'pbkdf2:sha256:600000$salted$hash_will_be_updated', '张教授', 'teacher'),
('T002', 'pbkdf2:sha256:600000$salted$hash_will_be_updated', '李教授', 'teacher'),
('T003', 'pbkdf2:sha256:600000$salted$hash_will_be_updated', '王副教授', 'teacher'),
('T004', 'pbkdf2:sha256:600000$salted$hash_will_be_updated', '赵副教授', 'teacher'),
('T005', 'pbkdf2:sha256:600000$salted$hash_will_be_updated', '陈讲师', 'teacher');

INSERT INTO teachers (user_id, teacher_id, name, department, title) VALUES
(2,  'T001', '张教授',   '计算机科学与技术学院', '教授'),
(3,  'T002', '李教授',   '软件工程学院',        '教授'),
(4,  'T003', '王副教授', '计算机科学与技术学院', '副教授'),
(5,  'T004', '赵副教授', '人工智能学院',        '副教授'),
(6,  'T005', '陈讲师',   '软件工程学院',        '讲师');

-- ==========================================
-- 5. 学生
-- ==========================================
INSERT INTO users (username, password_hash, name, role) VALUES
('S202101', 'pbkdf2:sha256:600000$salted$hash_will_be_updated', '张三', 'student'),
('S202102', 'pbkdf2:sha256:600000$salted$hash_will_be_updated', '李四', 'student'),
('S202103', 'pbkdf2:sha256:600000$salted$hash_will_be_updated', '王五', 'student'),
('S202104', 'pbkdf2:sha256:600000$salted$hash_will_be_updated', '赵六', 'student'),
('S202105', 'pbkdf2:sha256:600000$salted$hash_will_be_updated', '孙七', 'student'),
('S202106', 'pbkdf2:sha256:600000$salted$hash_will_be_updated', '周八', 'student'),
('S202107', 'pbkdf2:sha256:600000$salted$hash_will_be_updated', '吴九', 'student'),
('S202108', 'pbkdf2:sha256:600000$salted$hash_will_be_updated', '郑十', 'student');

INSERT INTO students (user_id, student_id, name, class_name, major, department) VALUES
(7,  'S202101', '张三', '计科2101班', '计算机科学与技术', '计算机科学与技术学院'),
(8,  'S202102', '李四', '计科2101班', '计算机科学与技术', '计算机科学与技术学院'),
(9,  'S202103', '王五', '软件2102班', '软件工程',         '软件工程学院'),
(10, 'S202104', '赵六', '软件2102班', '软件工程',         '软件工程学院'),
(11, 'S202105', '孙七', '计科2103班', '计算机科学与技术', '计算机科学与技术学院'),
(12, 'S202106', '周八', '人工智能2101班', '人工智能',     '人工智能学院'),
(13, 'S202107', '吴九', '人工智能2101班', '人工智能',     '人工智能学院'),
(14, 'S202108', '郑十', '计科2103班', '计算机科学与技术', '计算机科学与技术学院');

-- ==========================================
-- 6. 教师发布选题
-- ==========================================
INSERT INTO topics (teacher_id, title, description, max_students) VALUES
(1, '基于深度学习的图像识别系统研究与实现', '研究深度学习在图像识别领域的应用，设计并实现一个图像识别系统', 2),
(1, '智慧校园学生管理系统的设计与实现', '设计一套面向智慧校园的学生管理系统，包含学籍、选课、成绩等模块', 2),
(2, '基于区块链的毕业设计管理系统', '利用区块链技术设计去中心化的毕业设计管理平台', 1),
(2, '面向小白的Python编程辅助平台', '开发一个帮助编程初学者学习Python的交互式辅助平台', 2),
(3, '基于Vue3的在线考试系统设计与实现', '使用Vue3框架开发一个功能完善的在线考试系统', 2),
(3, '基于Flask的实验室设备管理系统', '使用Flask框架开发实验室设备预约与管理系统', 1),
(4, '校园二手交易平台的设计与实现', '设计一个面向校园的二手物品交易平台', 2),
(4, '基于推荐算法的课程选课系统', '基于协同过滤算法实现智能课程推荐选课系统', 2),
(5, '基于微服务的电商平台后端设计', '使用微服务架构设计一个电商平台后端系统', 1),
(5, '人工智能在医疗诊断中的应用研究', '研究AI技术在医疗影像诊断中的辅助应用', 1);

-- ==========================================
-- 7. 学生选题记录
-- ==========================================
INSERT INTO topic_selections (student_id, topic_id, title, description, type, status) VALUES
(1, 1, '基于深度学习的图像识别系统研究与实现', NULL, 'select', 'approved'),
(2, 2, '智慧校园学生管理系统的设计与实现', NULL, 'select', 'approved'),
(3, 3, '基于区块链的毕业设计管理系统', NULL, 'select', 'approved'),
(4, 4, '面向小白的Python编程辅助平台', NULL, 'select', 'approved'),
(5, 5, '基于Vue3的在线考试系统设计与实现', NULL, 'select', 'approved'),
(6, 6, '基于Flask的实验室设备管理系统', NULL, 'select', 'approved'),
(7, 7, '校园二手交易平台的设计与实现', NULL, 'select', 'approved'),
(8, 8, '基于推荐算法的课程选课系统', NULL, 'select', 'pending');

-- ==========================================
-- 8. 毕设项目
-- ==========================================
INSERT INTO projects (student_id, title, graduation_year_id, advisor_id, reviewer_id, current_status_id, max_submissions, submission_count) VALUES
(1, '基于深度学习的图像识别系统研究与实现',  1, 1, 3, 3, 5, 2),
(2, '智慧校园学生管理系统的设计与实现',      1, 1, 4, 2, 5, 1),
(3, '基于区块链的毕业设计管理系统',          1, 2, 5, 5, 5, 3),
(4, '面向小白的Python编程辅助平台',          1, 2, 3, 6, 5, 1),
(5, '基于Vue3的在线考试系统设计与实现',      1, 3, 5, 6, 5, 1),
(6, '基于Flask的实验室设备管理系统',          1, 4, 1, 2, 5, 0),
(7, '校园二手交易平台的设计与实现',          1, 5, 2, 1, 5, 0),
(8, '基于推荐算法的课程选课系统',            1, 3, 4, 1, 5, 0);

-- ==========================================
-- 9. 提交记录
-- ==========================================
INSERT INTO submissions (project_id, version, submission_type, file_name, file_path, file_size, submitted_by, description) VALUES
(1, 1, 'draft',  '毕设_张三_初稿_v1.pdf',  '/uploads/1/张三_初稿_v1.pdf',  2048000, 1, '初稿提交'),
(1, 2, 'round1', '毕设_张三_一轮_v2.pdf',  '/uploads/1/张三_一轮_v2.pdf',  2150000, 1, '一轮修改稿'),
(2, 1, 'draft',  '毕设_李四_初稿_v1.pdf',  '/uploads/2/李四_初稿_v1.pdf',  1024000, 2, '初稿提交'),
(3, 1, 'draft',  '毕设_王五_初稿_v1.pdf',  '/uploads/3/王五_初稿_v1.pdf',  1800000, 3, '初稿提交'),
(3, 2, 'round1', '毕设_王五_一轮_v2.pdf',  '/uploads/3/王五_一轮_v2.pdf',  1900000, 3, '一轮修改稿'),
(3, 3, 'round2', '毕设_王五_二轮_v3.pdf',  '/uploads/3/王五_二轮_v3.pdf',  1950000, 3, '二轮修改稿'),
(4, 1, 'draft',  '毕设_赵六_初稿_v1.pdf',  '/uploads/4/赵六_初稿_v1.pdf',  2200000, 4, '初稿提交'),
(5, 1, 'draft',  '毕设_孙七_初稿_v1.pdf',  '/uploads/5/孙七_初稿_v1.pdf',  1600000, 5, '初稿提交');

-- ==========================================
-- 10. 评审记录
-- ==========================================
INSERT INTO reviews (submission_id, reviewer_id, review_type, revision_round, score, comment, is_approved) VALUES
(1, 1, 'advisor',  1, 75.00, '初稿结构需要调整，第三章内容不够充实', FALSE),
(2, 1, 'advisor',  2, 85.00, '一轮修改后基本符合要求，进入查重定稿阶段', TRUE),
(3, 1, 'advisor',  1, 80.00, '初稿内容比较完整，可以进入一轮修改', TRUE),
(4, 2, 'advisor',  1, 70.00, '初稿内容完整但缺乏实验数据支撑', FALSE),
(5, 2, 'advisor',  2, 78.00, '一轮修改后仍有格式问题', FALSE),
(6, 2, 'advisor',  3, 88.00, '二轮修改后达到要求，进入查重定稿阶段', TRUE);

-- ==========================================
-- 11. 状态变更历史
-- ==========================================
INSERT INTO project_status_history (project_id, from_status_id, to_status_id, operator_role, operator_id, comment) VALUES
(1, 1, 2, 'student', 1, '选题审核通过，进入初稿阶段'),
(1, 2, 3, 'student', 1, '提交初稿，进入一轮修改阶段'),
(2, 1, 2, 'student', 2, '选题审核通过，进入初稿阶段'),
(3, 1, 2, 'student', 3, '选题审核通过，进入初稿阶段'),
(3, 2, 3, 'student', 3, '提交初稿，进入一轮修改阶段'),
(3, 3, 4, 'teacher', 2, '一轮未通过，进入二轮修改阶段'),
(4, 1, 2, 'student', 4, '选题审核通过，进入初稿阶段'),
(4, 2, 5, 'teacher', 2, '初稿已评审通过，进入查重定稿阶段'),
(5, 1, 2, 'student', 5, '选题审核通过，进入初稿阶段');
