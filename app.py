from flask import Flask
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from mongoengine import connect
import os

bcrypt = Bcrypt()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    # Dynamically load configuration based on environment variable
    config_name = os.getenv('FLASK_CONFIG', 'DevelopmentConfig')
    app.config.from_object(f'config.{config_name}')
    
    CORS(app)
    
    bcrypt.init_app(app)
    jwt.init_app(app)
    connect(
        db=app.config['MONGODB_SETTINGS']['db'],
        host=app.config['MONGODB_SETTINGS']['host'],
        port=app.config['MONGODB_SETTINGS']['port']
    )
    
    with app.app_context():
        # Import routes
        from routes import home

    return app