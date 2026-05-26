from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager
import hashlib
import sqlite3
import datetime
import json
import requests

app = Flask(__name__)
CORS(app)

app.config["JWT_SECRET_KEY"] = "secret"
jwt = JWTManager(app)

DB = 'detailing.db'

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

# фикс для авторизации (фронт отправляет токен без пробела)
@app.before_request
def before_req():
    auth = request.headers.get("Authorization")
    if auth and auth.startswith("Bearer") and not auth.startswith("Bearer "):
        token = auth[6:]
        request.environ['HTTP_AUTHORIZATION'] = f'Bearer {token}'

@app.route('/registration', methods=['POST'])
def reg():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'заполни все поля'})
        
    pass_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    conn = get_db()
    try:
        user = conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
        if user:
            return jsonify({'error': 'такой юзер уже есть'})
            
        d = datetime.date.today().strftime('%Y-%m-%d')
        cursor = conn.execute('INSERT INTO students (name, registration_date) VALUES (?, ?)', (username, d))
        st_id = cursor.lastrowid
        
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conn.execute(
            'INSERT INTO users (username, password_hash, created_at, student_id) VALUES (?, ?, ?, ?)',
            (username, pass_hash, now, st_id)
        )
        conn.commit()
        
        token = create_access_token(identity=username)
        return jsonify({'status': 'ok', 'token': token})
    except Exception as e:
        conn.rollback()
        # print("err:", e)
        return jsonify({'error': str(e)})
    finally:
        conn.close()

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'пустые поля'})
        
    pass_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    
    if not user:
        return jsonify({'error': 'не найден', 'id': 'log-nick'})
    if user['password_hash'] != pass_hash:
        return jsonify({'error': 'неверный пароль', 'id': 'log-pass'})
        
    token = create_access_token(identity=username)
    return jsonify({'token': token, 'status': 'ok'})

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    return jsonify(logged_in_as=get_jwt_identity())

@app.route('/user', methods=['GET'])
@jwt_required()
def profile_front():
    current_user = get_jwt_identity()
    conn = get_db()
    user = conn.execute('''
        SELECT u.username, u.created_at, c.title AS course_title
        FROM users u
        LEFT JOIN students s ON u.student_id = s.id
        LEFT JOIN enrollments e ON s.id = e.student_id
        LEFT JOIN courses c ON e.course_id = c.id
        WHERE u.username = ?
        LIMIT 1
    ''', (current_user,)).fetchone()
    conn.close()
    
    if not user:
        return jsonify({'error': 'юзер не найден'}), 404
        
    return jsonify({
        'username': user['username'],
        'data': {
            'created_at': user['created_at']
        },
        'course': user['course_title']
    })

@app.route('/<username>', methods=['GET'])
@jwt_required()
def profile(username):
    if get_jwt_identity() != username:
        return jsonify({'error': 'нет доступа'})
        
    conn = get_db()
    user = conn.execute('SELECT username, created_at FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    
    if not user:
        return jsonify({'error': 'не найден'}), 404
        
    return jsonify({
        'username': user['username'],
        'created_at': user['created_at']
    })

@app.route('/refresh-token', methods=['POST'])
@jwt_required()
def refresh_token():
    token = create_access_token(identity=get_jwt_identity())
    return jsonify({
        'token': token,
        'tolen': token # костыль для опечатки на фронте
    })

@app.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    months_ru = {
        '01': 'Янв', '02': 'Фев', '03': 'Мар', '04': 'Апр', '05': 'Май', '06': 'Июн',
        '07': 'Июл', '08': 'Авг', '09': 'Сен', '10': 'Окт', '11': 'Ноя', '12': 'Дек'
    }
    
    conn = get_db()
    try:
        total_users = conn.execute('SELECT COUNT(*) FROM students').fetchone()[0]
        hardcore = conn.execute('SELECT COUNT(*) FROM enrollments WHERE course_id = 3').fetchone()[0]
        normal = conn.execute('SELECT COUNT(*) FROM enrollments WHERE course_id = 2').fetchone()[0]
        chill = conn.execute('SELECT COUNT(*) FROM enrollments WHERE course_id = 1').fetchone()[0]
        
        rows = conn.execute('''
            SELECT strftime('%m', registration_date) as m, COUNT(*) as c
            FROM students
            WHERE registration_date IS NOT NULL AND registration_date != ''
            GROUP BY m
            ORDER BY m
        ''').fetchall()
        
        labels = []
        values = []
        for r in rows:
            labels.append(months_ru.get(r['m'], r['m']))
            values.append(r['c'])
            
        if len(labels) == 0:
            labels = ['Май']
            values = [total_users]
            
        return jsonify({
            'totalUsers': total_users,
            'hardcore': hardcore,
            'normal': normal,
            'chill': chill,
            'monthlyLabels': labels,
            'monthlyValues': values
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/about', methods=['GET'])
def about():
    try:
        with open('about.json', 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    except:
        return jsonify({'error': 'файл не найден'}), 404

@app.route('/api/hash/<text>', methods=['GET'])
def get_hash(text):
    return jsonify({
        'request': text,
        'result': hashlib.sha256(text.encode('utf-8')).hexdigest()
    })


# --- КУРСЫ ---
@app.route('/api/courses', methods=['GET'])
@jwt_required()
def get_courses():
    search = request.args.get('search', '')
    sort = request.args.get('sort', 'id')
    order = request.args.get('order', 'asc')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    if sort not in ['id', 'title', 'duration_hours']:
        sort = 'id'
    if order not in ['asc', 'desc']:
        order = 'asc'

    conn = get_db()
    if search:
        total = conn.execute('SELECT COUNT(*) FROM courses WHERE title LIKE ?', ('%' + search + '%',)).fetchone()[0]
        rows = conn.execute(
            f'SELECT * FROM courses WHERE title LIKE ? ORDER BY {sort} {order} LIMIT ? OFFSET ?',
            ('%' + search + '%', per_page, (page - 1) * per_page)
        ).fetchall()
    else:
        total = conn.execute('SELECT COUNT(*) FROM courses').fetchone()[0]
        rows = conn.execute(
            f'SELECT * FROM courses ORDER BY {sort} {order} LIMIT ? OFFSET ?',
            (per_page, (page - 1) * per_page)
        ).fetchall()
    conn.close()

    return jsonify({
        'data': [dict(r) for r in rows],
        'total': total,
        'page': page,
        'per_page': per_page
    })

@app.route('/api/courses/<int:cid>', methods=['GET'])
@jwt_required()
def get_course(cid):
    conn = get_db()
    c = conn.execute('SELECT * FROM courses WHERE id = ?', (cid,)).fetchone()
    conn.close()
    if not c:
        return jsonify({'error': 'не найдено'}), 404
    return jsonify(dict(c))

@app.route('/api/courses', methods=['POST'])
@jwt_required()
def create_course():
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({'error': 'title обязателен'}), 400

    conn = get_db()
    try:
        conn.execute('INSERT INTO courses (title, duration_hours) VALUES (?, ?)', (data['title'], data.get('duration_hours')))
        conn.commit()
        return jsonify({'status': 'ok'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/courses/<int:cid>', methods=['PUT'])
@jwt_required()
def update_course(cid):
    conn = get_db()
    c = conn.execute('SELECT * FROM courses WHERE id = ?', (cid,)).fetchone()
    if not c:
        conn.close()
        return jsonify({'error': 'не найдено'}), 404

    data = request.get_json()
    conn.execute('UPDATE courses SET title = ?, duration_hours = ? WHERE id = ?',
                 (data.get('title', c['title']), data.get('duration_hours', c['duration_hours']), cid))
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok'})

@app.route('/api/courses/<int:cid>', methods=['DELETE'])
@jwt_required()
def delete_course(cid):
    conn = get_db()
    conn.execute('DELETE FROM courses WHERE id = ?', (cid,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok'})


# --- СТУДЕНТЫ ---
@app.route('/api/students', methods=['GET'])
@jwt_required()
def get_students():
    search = request.args.get('search', '')
    sort = request.args.get('sort', 'id')
    order = request.args.get('order', 'asc')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    if sort not in ['id', 'name', 'email', 'phone', 'registration_date']:
        sort = 'id'
    if order not in ['asc', 'desc']:
        order = 'asc'

    conn = get_db()
    if search:
        total = conn.execute('SELECT COUNT(*) FROM students WHERE name LIKE ? OR email LIKE ?', ('%' + search + '%', '%' + search + '%')).fetchone()[0]
        rows = conn.execute(
            f'SELECT * FROM students WHERE name LIKE ? OR email LIKE ? ORDER BY {sort} {order} LIMIT ? OFFSET ?',
            ('%' + search + '%', '%' + search + '%', per_page, (page - 1) * per_page)
        ).fetchall()
    else:
        total = conn.execute('SELECT COUNT(*) FROM students').fetchone()[0]
        rows = conn.execute(
            f'SELECT * FROM students ORDER BY {sort} {order} LIMIT ? OFFSET ?',
            (per_page, (page - 1) * per_page)
        ).fetchall()
    conn.close()

    return jsonify({
        'data': [dict(r) for r in rows],
        'total': total,
        'page': page,
        'per_page': per_page
    })

@app.route('/api/students/<int:sid>', methods=['GET'])
@jwt_required()
def get_student(sid):
    conn = get_db()
    s = conn.execute('SELECT * FROM students WHERE id = ?', (sid,)).fetchone()
    conn.close()
    if not s:
        return jsonify({'error': 'не найдено'}), 404
    return jsonify(dict(s))

@app.route('/api/students', methods=['POST'])
@jwt_required()
def create_student():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'name обязателен'}), 400

    conn = get_db()
    try:
        reg = data.get('registration_date', datetime.date.today().strftime('%Y-%m-%d'))
        conn.execute('INSERT INTO students (name, phone, email, registration_date) VALUES (?, ?, ?, ?)',
                     (data['name'], data.get('phone'), data.get('email'), reg))
        conn.commit()
        return jsonify({'status': 'ok'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/students/<int:sid>', methods=['PUT'])
@jwt_required()
def update_student(sid):
    conn = get_db()
    s = conn.execute('SELECT * FROM students WHERE id = ?', (sid,)).fetchone()
    if not s:
        conn.close()
        return jsonify({'error': 'не найдено'}), 404

    data = request.get_json()
    conn.execute('UPDATE students SET name = ?, phone = ?, email = ? WHERE id = ?',
                 (data.get('name', s['name']), data.get('phone', s['phone']), data.get('email', s['email']), sid))
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok'})

@app.route('/api/students/<int:sid>', methods=['DELETE'])
@jwt_required()
def delete_student(sid):
    conn = get_db()
    conn.execute('DELETE FROM students WHERE id = ?', (sid,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok'})


# --- ЗАПИСИ ---
@app.route('/api/enrollments', methods=['GET'])
@jwt_required()
def get_enrollments():
    search = request.args.get('search', '')
    sort = request.args.get('sort', 'id')
    order = request.args.get('order', 'asc')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    if sort not in ['id', 'student_id', 'course_id', 'enrollment_date', 'status']:
        sort = 'id'
    if order not in ['asc', 'desc']:
        order = 'asc'

    conn = get_db()
    if search:
        total = conn.execute('SELECT COUNT(*) FROM enrollments WHERE status LIKE ? OR certificate_number LIKE ?', ('%' + search + '%', '%' + search + '%')).fetchone()[0]
        rows = conn.execute(
            f'''SELECT e.*, s.name as student_name, c.title as course_title
                FROM enrollments e
                LEFT JOIN students s ON e.student_id = s.id
                LEFT JOIN courses c ON e.course_id = c.id
                WHERE e.status LIKE ? OR e.certificate_number LIKE ?
                ORDER BY e.{sort} {order} LIMIT ? OFFSET ?''',
            ('%' + search + '%', '%' + search + '%', per_page, (page - 1) * per_page)
        ).fetchall()
    else:
        total = conn.execute('SELECT COUNT(*) FROM enrollments').fetchone()[0]
        rows = conn.execute(
            f'''SELECT e.*, s.name as student_name, c.title as course_title
                FROM enrollments e
                LEFT JOIN students s ON e.student_id = s.id
                LEFT JOIN courses c ON e.course_id = c.id
                ORDER BY e.{sort} {order} LIMIT ? OFFSET ?''',
            (per_page, (page - 1) * per_page)
        ).fetchall()
    conn.close()

    return jsonify({
        'data': [dict(r) for r in rows],
        'total': total,
        'page': page,
        'per_page': per_page
    })

@app.route('/api/enrollments/<int:eid>', methods=['GET'])
@jwt_required()
def get_enrollment(eid):
    conn = get_db()
    r = conn.execute('''SELECT e.*, s.name as student_name, c.title as course_title
                        FROM enrollments e
                        LEFT JOIN students s ON e.student_id = s.id
                        LEFT JOIN courses c ON e.course_id = c.id
                        WHERE e.id = ?''', (eid,)).fetchone()
    conn.close()
    if not r:
        return jsonify({'error': 'не найдено'}), 404
    return jsonify(dict(r))

@app.route('/api/enrollments', methods=['POST'])
@jwt_required()
def create_enrollment():
    data = request.get_json()
    if not data or not data.get('student_id') or not data.get('course_id'):
        return jsonify({'error': 'id нужны'}), 400

    conn = get_db()
    try:
        dt = data.get('enrollment_date', datetime.date.today().strftime('%Y-%m-%d'))
        st = data.get('status', 'Новый')
        conn.execute('INSERT INTO enrollments (student_id, course_id, enrollment_date, status) VALUES (?, ?, ?, ?)',
                     (data['student_id'], data['course_id'], dt, st))
        conn.commit()
        return jsonify({'status': 'ok'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/enrollments/<int:eid>', methods=['PUT'])
@jwt_required()
def update_enrollment(eid):
    conn = get_db()
    e = conn.execute('SELECT * FROM enrollments WHERE id = ?', (eid,)).fetchone()
    if not e:
        conn.close()
        return jsonify({'error': 'не найдено'}), 404

    data = request.get_json()
    conn.execute('UPDATE enrollments SET status = ?, certificate_number = ? WHERE id = ?',
                 (data.get('status', e['status']), data.get('certificate_number', e['certificate_number']), eid))
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok'})

@app.route('/api/enrollments/<int:eid>', methods=['DELETE'])
@jwt_required()
def delete_enrollment(eid):
    conn = get_db()
    conn.execute('DELETE FROM enrollments WHERE id = ?', (eid,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok'})


# --- ПРОКСИ НА FASTAPI ---
FASTAPI_URL = 'http://localhost:5001'

@app.route('/api/analytics', methods=['GET'])
@jwt_required()
def analytics_proxy():
    try:
        r = requests.get(f'{FASTAPI_URL}/api/analytics', timeout=2)
        return jsonify(r.json())
    except:
        return jsonify({
            'message': 'сервис не отвечает, вот фейк данные',
            'avg_duration': 60,
            'completion_rate': 15,
            'total_enrollments': 0,
            'popular_course': 'Нет данных'
        })

@app.route('/api/notifications', methods=['GET'])
@jwt_required()
def notif_proxy():
    try:
        r = requests.get(f'{FASTAPI_URL}/api/notifications', timeout=2)
        return jsonify(r.json())
    except:
        return jsonify({'notifications': []})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
