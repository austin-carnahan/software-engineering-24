from flask import render_template, request, jsonify, redirect, url_for
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from pymongo import MongoClient

def register_routes(app):
    bcrypt = Bcrypt(app)
    jwt = JWTManager(app)

    # MongoDB connection
    client = MongoClient(app.config['MONGO_URI'])
    db = client.get_database("personal_budget")

    @app.route('/', methods=['GET'])
    def home():
        return render_template('index.html')

    @app.route('/register', methods=["POST"])
    def register():
        email = request.form["email"]
        password = request.form["password"]
        nickname = request.form["nickname"]
        favorite_food = request.form["favorite_food"]
        favorite_movie = request.form["favorite_movie"]

        user = db.users.find_one({"email": email})
        if user:
            return jsonify({"error": "Email already registered"}), 400  # Bad Request

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        user = {"email": email, "password": hashed_password, "nickname": nickname,
                "favorite_food": favorite_food, "favorite_movie": favorite_movie}

        db.users.insert_one(user)

        return jsonify({"message": "Registration successful"}), 201  # Created

    @app.route('/login', methods=["POST"])
    def login():
        email = request.form["email"]
        password = request.form["password"]

        user = db.users.find_one({"email": email})
        if user and bcrypt.check_password_hash(user["password"], password):
            access_token = create_access_token(identity={"email": email})
            response = jsonify({"message": "Login successful"})
            response.headers["Authorization"] = f"Bearer {access_token}"
            response.status_code = 200
            response.autocorrect_location_header = False
            return response
        else:
            return jsonify({"error": "Invalid credentials"}), 401

    @app.route('/dashboard', methods=['GET'])
    def dashboard():
        return render_template('dashboard.html')