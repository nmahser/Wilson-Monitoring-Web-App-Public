### 3 pound keys mean that the code needs to be refactored. This is usually used when we change our idea for the initial design/value to display, etc.


#Third party imports
from dfply import * #dplyr package for python
from datetime import datetime
from functools import reduce
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import secretKey as sk

dbLite = SQLAlchemy()


def create_app():

    app = Flask(__name__)


    #DB LITE FOR USER LOGIN

    app.config['SECRET_KEY'] = sk.secretkey
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 

    dbLite.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    from auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
