from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from db_helper import get_db

courses = Blueprint('courses', __name__)

@courses.route('/api/courses', methods=['GET'])
@jwt_required()
def get_courses():
    search = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT * FROM courses WHERE name LIKE ? ORDER BY id LIMIT ? OFFSET ?"
    cursor.execute(query, (f"%{search}%", per_page, offset))
    courses_list = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in courses_list]), 200