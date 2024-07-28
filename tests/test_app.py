import sys
import os
import pytest
from flask import Flask, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def app():
    app = Flask(__name__)

    # Load configuration
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'super-secret-key'
    app.config['MONGO_URI'] = 'mongodb://localhost:27017/testdb'  # Dummy URI for testing
    
    CORS(app)
    bcrypt = Bcrypt(app)
    jwt = JWTManager(app)

    @app.route('/')
    def home():
        return jsonify({"message": "Home Route"})

    @app.route('/login', methods=["POST"])
    def login():
        return jsonify({"message": "Login Route"}), 200

    @app.route('/dashboard')
    def dashboard():
        return jsonify({"message": "Dashboard Route"}), 200

    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_home_route(client):
    response = client.get('/')
    assert response.status_code == 200

def test_login_route_accessible(client):
    data = {
        'email': 'test@example.com',
        'password': 'password123'
    }
    response = client.post('/login', data=data)
    assert response.status_code == 200

def test_dashboard_route(client):
    response = client.get('/dashboard')
    assert response.status_code == 200
