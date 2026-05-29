from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from db_helper import get_db
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)

@auth.route('/registration', methods=['POST'])
def reg():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    conn = get_db()
    cursor = conn.cursor()
    user = cursor.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    if user:
        conn.close()
        return jsonify({"error": "ты уже существуешь"}), 400
    hashed_password = generate_password_hash(password)
    cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed_password))
    conn.commit()
    conn.close()
    token = create_access_token(identity=username)
    return jsonify({"status": "ok", "token": token}), 200

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    conn = get_db()
    cursor = conn.cursor()
    user = cursor.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({"error": "ты не родился ещё", "id": "log-nick"}), 401
    token = create_access_token(identity=username)
    return jsonify({"status": "ok", "token": token}), 200