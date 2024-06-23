from flask import Flask
from flask_cors import CORS
import os

def create_app():
    app = Flask(__name__)
    # Dynamically load configuration based on environment variable
    config_name = os.getenv('FLASK_CONFIG', 'DevelopmentConfig')
    app.config.from_object(f'config.{config_name}')
    
    CORS(app)
    
    with app.app_context():
        # Import routes
        from routes import home

    return app