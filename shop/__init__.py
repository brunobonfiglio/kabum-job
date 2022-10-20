from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

import os

import sentry_sdk
sentry_sdk.init(
    "https://e7547433e06143ab9c05a87e576368c3@o464374.ingest.sentry.io/5514931",
    traces_sample_rate=1.0
)



#basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kabum.db'
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://gofyllfqcvhfbb:82d522137bb7ff111ac2f3d23de3e9467a0064ca9281ba1137a3e7cf3f07e498@ec2-3-224-38-18.compute-1.amazonaws.com:5432/dd6ba5nnttoovn"

# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "KRdo4I7nguFDBk8hngqbVqUcRLyGe339"


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# from shop.admin import routes
from shop.products import routes
