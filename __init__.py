# ANPR Software for M.Sc. Project Summer 2023
# Developed by Emmanuel Begah (w1935132)

# Import Libraries
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
filename = "users.db"

# Function to initialsie application
def createApplication():
    application = Flask(__name__)
    application.config['SECRET_KEY'] = 'w1935132'  # Stores session & cookie data
    application.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{filename}'

    db.init_app(application)  # Initialise database object

    from .views import view
    from .auth import auth

    application.register_blueprint(view, url_prefix='/')
    application.register_blueprint(auth, url_prefix='/')

    from .models import User

    createDatabase(application)  # Creates database file not doesn't already exist

    loginManager = LoginManager()
    loginManager.login_view = 'auth.access'
    loginManager.init_app(application)

    @loginManager.user_loader
    def loadUser(id):
        return User.query.get(int(id))

    return application

# Function to initialise database
def createDatabase(application):
    if not path.exists('webapp/' + filename):
        with application.app_context():
            db.create_all()
        print('Database has been successfully created.')
