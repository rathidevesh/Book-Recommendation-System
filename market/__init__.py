from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db17.sqlite3'
app.config['STATIC_URL_PATH'] = '/static'
app.config['SECRET_KEY'] = '-Q\x8a\xe5Ug\x00q\xae\xe0\x99\x19'

app.config['WTF_CSRF_ENABLED'] = False
db = SQLAlchemy(app)

@app.before_first_request
def create_database():
     db.create_all()

# create the app instance before importing bcrypt
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login_page"

from market import routes
# from market import helpers

