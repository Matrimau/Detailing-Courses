from flask import Flask
from flask_jwt_extended import JWTManager
from auth import auth
from courses import courses
from profile import profile
from mini import mini

app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = 'super-secret'
jwt = JWTManager(app)

app.register_blueprint(auth)
app.register_blueprint(courses)
app.register_blueprint(profile)
app.register_blueprint(mini)

if __name__ == '__main__':
    app.run(debug=True)