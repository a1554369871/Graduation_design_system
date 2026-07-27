CREATE DATABASE IF NOT EXISTS Graduation_Design_System
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE Graduation_Design_System;

-- 用户表
CREATE TABLE users (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    username    VARCHAR(64)  NOT NULL UNIQUE,
    password_hash VARCHAR(256) NOT NULL,
    name        VARCHAR(64)  NOT NULL,
    role        ENUM('student','teacher','admin') NOT NULL,
    is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 学生扩展信息
CREATE TABLE students (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT          NOT NULL UNIQUE,
    student_id  VARCHAR(32)  NOT NULL UNIQUE COMMENT '学号',
    name        VARCHAR(64)  NOT NULL COMMENT '姓名',
    class_name  VARCHAR(64)  COMMENT '班级',
    major       VARCHAR(64)  COMMENT '专业',
    department  VARCHAR(64)  COMMENT '院系',
    phone       VARCHAR(16),
    email       VARCHAR(64),
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 教师扩展信息
CREATE TABLE teachers (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT          NOT NULL UNIQUE,
    teacher_id  VARCHAR(32)  NOT NULL UNIQUE COMMENT '工号',
    name        VARCHAR(64)  NOT NULL COMMENT '姓名',
    department  VARCHAR(64)  COMMENT '院系',
    title       VARCHAR(32)  COMMENT '职称',
    phone       VARCHAR(16),
    email       VARCHAR(64),
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 管理员表
CREATE TABLE admins (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT          NOT NULL UNIQUE,
    name        VARCHAR(64)  NOT NULL COMMENT '姓名',
    phone       VARCHAR(16),
    email       VARCHAR(64),
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 毕设年份字典
CREATE TABLE graduation_years (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    year        VARCHAR(9)   NOT NULL UNIQUE COMMENT '如 2025-2026',
    is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 毕设状态字典
CREATE TABLE graduation_status_defs (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(64)  NOT NULL COMMENT '状态名，如开题、中期',
    code        VARCHAR(32)  NOT NULL UNIQUE COMMENT '代码标识',
    sort_order  INT          NOT NULL DEFAULT 0,
    is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 选题表（教师发布）
CREATE TABLE topics (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id      INT          NOT NULL,
    title           VARCHAR(256) NOT NULL,
    description     TEXT,
    max_students    INT          NOT NULL DEFAULT 1,
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 学生选题记录
CREATE TABLE topic_selections (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    student_id      INT          NOT NULL,
    topic_id        INT,
    title           VARCHAR(256) NOT NULL,
    description     TEXT,
    type            ENUM('select','self_propose') NOT NULL COMMENT 'select-选择教师选题, self_propose-自主选题',
    status          ENUM('pending','approved','rejected') NOT NULL DEFAULT 'pending',
    review_comment  TEXT,
    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 毕设项目表
CREATE TABLE projects (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    student_id          INT          NOT NULL,
    title               VARCHAR(256) NOT NULL,
    graduation_year_id  INT          NOT NULL,
    description         TEXT,
    advisor_id          INT          NOT NULL COMMENT '指导教师',
    reviewer_id         INT                   COMMENT '评阅教师',
    current_status_id   INT          NOT NULL,
    max_submissions     INT          NOT NULL DEFAULT 5,
    submission_count    INT          NOT NULL DEFAULT 0,
    created_at          DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (graduation_year_id) REFERENCES graduation_years(id),
    FOREIGN KEY (advisor_id) REFERENCES teachers(id),
    FOREIGN KEY (reviewer_id) REFERENCES teachers(id) ON DELETE SET NULL,
    FOREIGN KEY (current_status_id) REFERENCES graduation_status_defs(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 项目状态变更历史
CREATE TABLE project_status_history (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    project_id      INT          NOT NULL,
    from_status_id  INT,
    to_status_id    INT          NOT NULL,
    operator_role   ENUM('student','teacher','admin') NOT NULL,
    operator_id     INT          NOT NULL COMMENT '操作者关联ID（students/teachers/admins表）',
    comment         TEXT,
    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (from_status_id) REFERENCES graduation_status_defs(id) ON DELETE SET NULL,
    FOREIGN KEY (to_status_id) REFERENCES graduation_status_defs(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 论文提交记录
CREATE TABLE submissions (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    project_id      INT          NOT NULL,
    version         INT          NOT NULL COMMENT '版本号',
    submission_type ENUM('draft','round1','round2','round3','final_check','final') NOT NULL DEFAULT 'draft',
    file_name       VARCHAR(256) NOT NULL,
    file_path       VARCHAR(512) NOT NULL,
    file_size       BIGINT       NOT NULL DEFAULT 0 COMMENT '文件大小（字节）',
    submitted_by    INT          NOT NULL COMMENT '提交人（student.id）',
    description     TEXT,
    downloaded_at   DATETIME     COMMENT '教师最后下载时间',
    download_count  INT          NOT NULL DEFAULT 0 COMMENT '下载次数',
    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (submitted_by) REFERENCES students(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 评审记录
CREATE TABLE reviews (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    submission_id   INT          NOT NULL,
    reviewer_id     INT          NOT NULL COMMENT '评阅教师ID',
    review_type     ENUM('advisor','reviewer') NOT NULL,
    revision_round  INT          NOT NULL DEFAULT 1 COMMENT '第几轮评审',
    score           DECIMAL(5,2) COMMENT '百分制分数',
    comment         TEXT,
    is_approved     BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    withdrawn_at    DATETIME     COMMENT '导师撤回时间',
    FOREIGN KEY (submission_id) REFERENCES submissions(id) ON DELETE CASCADE,
    FOREIGN KEY (reviewer_id) REFERENCES teachers(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 导出日志
CREATE TABLE export_logs (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    admin_id        INT          NOT NULL,
    export_type     ENUM('evaluation_form','thesis_materials') NOT NULL,
    filters_json    JSON,
    exported_at     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES admins(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 通知表
CREATE TABLE notifications (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    title       VARCHAR(256) NOT NULL COMMENT '标题',
    content     TEXT COMMENT '内容',
    sender_type ENUM('admin','teacher') NOT NULL COMMENT '发送者类型',
    sender_id   INT NOT NULL COMMENT '发送者ID（admins.id / teachers.id）',
    is_global   BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否全局可见（管理员通知为TRUE）',
    expires_at  DATETIME COMMENT '过期时间（到期后自动隐藏）',
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 通知接收人（教师发送给学生时记录）
CREATE TABLE notification_recipients (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    notification_id INT NOT NULL,
    student_id      INT NOT NULL COMMENT '学生ID',
    is_read         BOOLEAN NOT NULL DEFAULT FALSE,
    read_at         DATETIME,
    FOREIGN KEY (notification_id) REFERENCES notifications(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 系统操作日志
CREATE TABLE system_logs (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT          NOT NULL,
    action          VARCHAR(64)  NOT NULL COMMENT '操作标识',
    target_type     VARCHAR(64)  COMMENT '操作对象类型',
    target_id       INT          COMMENT '操作对象ID',
    detail          TEXT,
    ip_address      VARCHAR(45),
    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
