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

def test_bcrypt_hashing(app):
    """Test if Bcrypt hashing works correctly."""
    bcrypt = Bcrypt(app)
    password = "mysecretpassword"
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    assert bcrypt.check_password_hash(hashed_password, password) is True
    assert bcrypt.check_password_hash(hashed_password, "wrongpassword") is False

def test_user_registration(client):
    """Test if a user can be registered successfully."""
    data = {
        'email': 'test@example.com',
        'password': 'password123',
        'nickname': 'TestUser',
        'favorite_food': 'Pizza',
        'favorite_movie': 'Inception'
    }
    response = client.post('/register', data=data)
    assert response.status_code == 201

    client = MongoClient('mongodb://localhost:27017/')
    user = client.testdb.users.find_one({"email": "test@example.com"})
    assert user is not None
    assert user['nickname'] == 'TestUser'
    assert user['favorite_food'] == 'Pizza'
    assert user['favorite_movie'] == 'Inception'

def test_get_budget_data(client, app):
    """Test fetching budget data for a logged-in user."""
    # Register and login a user
    register_data = {
        'email': 'test@example.com',
        'password': 'password123',
        'nickname': 'TestUser',
        'favorite_food': 'Pizza',
        'favorite_movie': 'Inception'
    }
    client.post('/register', data=register_data)
    login_data = {
        'email': 'test@example.com',
        'password': 'password123'
    }
    response = client.post('/login', data=login_data)
    assert response.status_code == 200

    with client.session_transaction() as sess:
        sess['email'] = 'test@example.com'

    # Insert budget data
    client = MongoClient('mongodb://localhost:27017/')
    budget_data = {
        'email': 'test@example.com',
        'primary_income': 5000,
        'other_income': 1000,
        'housing': 1200,
        'groceries': 400,
        'shopping': 300,
        'transportation': 200,
        'bills': 150,
        'entertainment': 100,
        'education': 250,
        'savings': 500,
        'debt': 300,
        'debt_balance': 2000,
        'savings_balance': 5000
    }
    client.testdb.budgets.insert_one(budget_data)

    # Fetch budget data
    response = client.get('/api/budget_data')
    assert response.status_code == 200
    budget_data = response.get_json()
    assert budget_data['primary_income'] == 5000
    assert budget_data['other_income'] == 1000
    assert budget_data['housing'] == 1200
    assert budget_data['groceries'] == 400
    assert budget_data['shopping'] == 300
    assert budget_data['transportation'] == 200
    assert budget_data['bills'] == 150
    assert budget_data['entertainment'] == 100
    assert budget_data['education'] == 250
    assert budget_data['savings'] == 500
    assert budget_data['debt'] == 300
    assert budget_data['debt_balance'] == 2000
    assert budget_data['savings_balance'] == 5000
