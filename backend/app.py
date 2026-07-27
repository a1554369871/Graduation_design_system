from flask import Flask, jsonify
from config import Config
from extensions import db, jwt, cors

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.teacher import teacher_bp
    from routes.student import student_bp
    from routes.notification import notification_bp
    from routes.topic import topic_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(teacher_bp, url_prefix='/api/teacher')
    app.register_blueprint(student_bp, url_prefix='/api/student')
    app.register_blueprint(notification_bp, url_prefix='/api/notifications')
    app.register_blueprint(topic_bp, url_prefix='/api/topics')

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({'msg': '请求方法不被允许'}), 405

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'msg': '请求的资源不存在'}), 404

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
