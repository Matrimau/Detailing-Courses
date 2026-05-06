from flask import Flask, request, render_template, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

users={}

@app.route('/')
def index():
    return render_template('Thanatos.html', name='Fabel')


@app.route('/registration', methods=['POST'])
def registration():
    username = request.json.get('username')
    password = request.json.get('password')
    if not username or not password:
        return jsonify({'error': 'всё заполни!'})
    if username in users:
        return jsonify({'error': 'ты уже существуешь'})
    users[username] = password
    return jsonify({'status': 'ok'})


@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    if not username or not password:
        return jsonify({'error': 'всё заполни!'})
    if username not in users:
        return jsonify({'error': 'ты не родился ещё'})
    if users[username] != password:
        return jsonify({'error': 'а пароль то у нас неверный'})
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True)