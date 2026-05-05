from flask import Flask
from flask import render_template
from flask import request

app = Flask(__name__)
@app.route('/')
def index():
    return render_template('Thanatos.html', name='Fabel')
@app.route('/courses')
def courses():
    return 'это твои курсы'
@app.route('/hello', methods=['POST'])
def hello():
    name = request.form['name']
    return f'Привет, {name}!'
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if username == 'admin' and psw == '1234':
        return f'вы вошли'
    else:
        return f'не правильный логин или пароль, повторите попытку'
@app.route('/registration', methods=['POST'])
def registration():
    username = request.json.get('username')
    password = request.json.get('password')
    if not username or not password:
        return {"status": "Неправильный логин или пароль"}
    else:
        return {"status": "Заходь"}
if __name__ == '__main__':
    app.run(debug=True)