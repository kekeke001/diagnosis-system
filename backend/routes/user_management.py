from flask import Blueprint, jsonify, request
from models import db, User
from datetime import datetime
import jwt

# 创建蓝图
bp = Blueprint('user_management', __name__)

# 获取用户信息
@bp.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    user_data = [{
        'user_id': user.user_id,
        'username': user.username,
        'email': user.email,
        'role': user.role,
        'created_at': user.created_at,
        'last_login': user.last_login
    } for user in users]
    return jsonify(user_data)

# 删除用户
@bp.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "用户已删除"}), 200

# 更新用户最后登录时间
@bp.route('/api/users/login/<int:user_id>', methods=['PUT'])
def update_last_login(user_id):
    user = User.query.get_or_404(user_id)
    user.last_login = datetime.utcnow()
    db.session.commit()
    return jsonify({"message": "登录时间已更新"}), 200

# 获取当前用户信息
@bp.route('/api/current_user', methods=['GET'])
def get_current_user():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': '用户未登录'}), 401

    try:
        token = token.split(" ")[1]
        payload = jwt.decode(token, 'your_secret_key', algorithms=['HS256'])
        username = payload.get('username')
        if not username:
            return jsonify({'error': '无效的 token'}), 401
        return jsonify({'username': username})

    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'token 已过期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': '无效的 token'}), 401
