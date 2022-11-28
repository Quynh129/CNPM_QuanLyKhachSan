from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote
from flask_login import LoginManager
import cloudinary
from flask_babelex import Babel

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'mysql+pymysql://root:%s@localhost/dbquanlykhachsan?charset=utf8mb4' % quote('Admin@123')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.secret_key = 'Day@la@mot@dong@ki@tu@ngau@nhien'

cloudinary.config(cloud_name='dthmdqv1m',
                  api_key='334554822929273',
                  api_secret='Pg4MZRYAuMJaHnscVDBOQOJPy2E')

db = SQLAlchemy(app=app)

login = LoginManager(app=app)

babel = Babel(app=app)


@babel.localeselector
def load_locale():
    return 'vi'
