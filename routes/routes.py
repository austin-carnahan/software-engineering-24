from flask import render_template, request, jsonify, redirect, url_for, session
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
        email = request.form.get("email")
        password = request.form.get("password")
        nickname = request.form.get("nickname")
        favorite_food = request.form.get("favorite_food")
        favorite_movie = request.form.get("favorite_movie")

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        user = db.users.find_one({"email": email})
        if user:
            return jsonify({"error": "Email already registered"}), 400

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        user = {"email": email, "password": hashed_password, "nickname": nickname,
                "favorite_food": favorite_food, "favorite_movie": favorite_movie}

        db.users.insert_one(user)

        return jsonify({"message": "Registration successful"}), 201

    @app.route('/login', methods=["POST"])
    def login():
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        user = db.users.find_one({"email": email})
        if user and bcrypt.check_password_hash(user["password"], password):
            access_token = create_access_token(identity={"email": email})
            session['email'] = email
            response = jsonify({"message": "Login successful"})
            response.headers["Authorization"] = f"Bearer {access_token}"
            return response
        else:
            return jsonify({"error": "Invalid credentials"}), 401

    @app.route('/dashboard', methods=['GET'])
    @jwt_required(optional=True)
    def dashboard():
        if 'email' not in session:
            return redirect(url_for('home'))
        return render_template('dashboard.html')

    @app.route('/logout', methods=['GET'])
    def logout():
        session.clear()
        return jsonify({"message": "Logged out successfully"})

    @app.route('/budgetform', methods=['GET', 'POST'])
    def budget_form():
        if 'email' not in session:
            return redirect(url_for('home'))

        if request.method == 'POST':
            form_data = request.get_json()
            if not form_data:
                return jsonify({"error": "No data provided"}), 400

            primary_income = form_data.get('primaryIncome')
            other_income = form_data.get('otherIncome')
            housing = form_data.get('housing')
            groceries = form_data.get('groceries')
            shopping = form_data.get('shopping')
            transportation = form_data.get('transportation')
            bills = form_data.get('bills')
            entertainment = form_data.get('entertainment')
            education = form_data.get('education')
            savings = form_data.get('savings')
            debt = form_data.get('debt')
            debt_balance = form_data.get('debtBalance')
            savings_balance = form_data.get('savingsBalance')

            email = session['email']

            try:
                db.budgets.insert_one({
                    'email': email,
                    'primary_income': primary_income,
                    'other_income': other_income,
                    'housing': housing,
                    'groceries': groceries,
                    'shopping': shopping,
                    'transportation': transportation,
                    'bills': bills,
                    'entertainment': entertainment,
                    'education': education,
                    'savings': savings,
                    'debt': debt,
                    'debt_balance': debt_balance,
                    'savings_balance': savings_balance
                })
                return jsonify({"message": "Budget data saved successfully"}), 201
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        return render_template('budgetform.html')