from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from db_helper import get_db

profile = Blueprint('profile', __name__)

@profile.route('/user', methods=['GET'])
@jwt_required()
def user_page():
    username = get_jwt_identity()
    conn = get_db()
    user_data = conn.execute("SELECT created_at FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return jsonify({
        "username": username,
        "data": {"created_at": user_data['created_at'] if user_data else "Неизвестно"},
        "course": "Пока не выбран"
    }), 200

@profile.route('/refresh-token', methods=['POST'])
@jwt_required()
def refresh():
    username = get_jwt_identity()
    new_token = create_access_token(identity=username)
    return jsonify({"token": new_token}), 200

@profile.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    conn.close()
    return jsonify({
        "totalUsers": total,
        "hardcore": 1,
        "normal": 2,
        "chill": 1,
        "monthlyLabels": ["Май"],
        "monthlyValues": [total]
    }), 200