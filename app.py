from flask import Flask
from flask import render_template
from flask import request

app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html', name='Fabel')
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
    psw = request.form['psw']
    if username == 'admin' and psw == '1234':
        return f'вы вошли'
    else:
        return f'не правильный логин или пароль, повторите попытку'
if __name__=='__main__':
    app.run(debug=True)