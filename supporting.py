from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB = 'detailing.db'

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

@app.get('/api/analytics')
def analytics():
    conn = get_db()
    try:
        avg_dur = conn.execute('SELECT AVG(duration_hours) FROM courses').fetchone()[0]
        total = conn.execute('SELECT COUNT(*) FROM enrollments').fetchone()[0]
        completed = conn.execute("SELECT COUNT(*) FROM enrollments WHERE status = 'Завершен'").fetchone()[0]
        
        rate = 0
        if total > 0:
            rate = round(completed / total * 100)
        popular = conn.execute('''
            SELECT c.title
            FROM enrollments e
            JOIN courses c ON e.course_id = c.id
            GROUP BY e.course_id
            ORDER BY COUNT(e.id) DESC
            LIMIT 1
        ''').fetchone()
        courses_stat = conn.execute('''
            SELECT c.title, c.duration_hours, COUNT(e.id) as students_count
            FROM courses c
            LEFT JOIN enrollments e ON c.id = e.course_id
            GROUP BY c.id
        ''').fetchall()
        courses_data = []
        for r in courses_stat:
            courses_data.append(dict(r))
        return {
            'avg_duration': round(avg_dur) if avg_dur else 0,
            'total_enrollments': total,
            'completed': completed,
            'completion_rate': rate,
            'popular_course': popular['title'] if popular else 'нет данных',
            'courses': courses_data
        }
    except Exception as e:
        return {'error': str(e)}
    finally:
        conn.close()

@app.get('/api/notifications')
def notifications():
    conn = get_db()
    try:
        rows = conn.execute('''
            SELECT s.name, c.title, e.enrollment_date, e.status
            FROM enrollments e
            JOIN students s ON e.student_id = s.id
            JOIN courses c ON e.course_id = c.id
            ORDER BY e.enrollment_date DESC
            LIMIT 10
        ''').fetchall()

        notifs = []
        for r in rows:
            notifs.append({
                'text': f"{r['name']} записался на курс \"{r['title']}\"",
                'date': r['enrollment_date'],
                'status': r['status']
            })

        return {'notifications': notifs}
    except Exception as e:
        return {'error': str(e)}
    finally:
        conn.close()

@app.get('/api/report')
def report():
    conn = get_db()
    try:
        total_students = conn.execute('SELECT COUNT(*) FROM students').fetchone()[0]
        total_courses = conn.execute('SELECT COUNT(*) FROM courses').fetchone()[0]
        total_enrollments = conn.execute('SELECT COUNT(*) FROM enrollments').fetchone()[0]

        statuses = conn.execute('''
            SELECT status, COUNT(*) as cnt
            FROM enrollments
            GROUP BY status
        ''').fetchall()
        status_data = {}
        for r in statuses:
            status_data[r['status']] = r['cnt']
        return {
            'total_students': total_students,
            'total_courses': total_courses,
            'total_enrollments': total_enrollments,
            'enrollments_by_status': status_data
        }
    except Exception as e:
        return {'error': str(e)}
    finally:
        conn.close()

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5001)