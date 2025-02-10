from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from models import db, User
import jwt
from datetime import datetime, timedelta

# 创建蓝图
auth_bp = Blueprint('auth', __name__)

# 用户登录接口
@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        # 从数据库中查找用户
        user = db.session.query(User).filter_by(username=username).first()

        if not user:
            return jsonify({"error": "该用户不存在，请注册"}), 404

        if not check_password_hash(user.password_hash, password):  # 使用加密的密码哈希进行比较
            return jsonify({"error": "无效的密码"}), 401

        user.last_login = datetime.utcnow()
        db.session.commit()

        token = jwt.encode(
            {
                'username': username,
                'exp': datetime.utcnow() + timedelta(hours=1)
            },
            'your_secret_key',
            algorithm='HS256'
        )

        token = token.decode('utf-8')

        return jsonify({"message": "登录成功", "token": token}), 200

    except Exception as e:
        return jsonify({"error": "内部服务器错误"}), 500

# 用户注册接口
@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')

        if not username or not password or not email:
            return jsonify({"error": "Missing required fields"}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username already exists"}), 400

        hashed_password = generate_password_hash(password)
        role = "admin" if username.lower().startswith("admin") else "user"
        new_user = User(
            username=username,
            password_hash=hashed_password,
            email=email,
            role=role
        )

        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "Registration successful"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Registration failed"}), 500
