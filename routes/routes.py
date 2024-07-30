from flask import render_template, request, jsonify, redirect, url_for, session
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from pymongo import MongoClient
import json

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
        return render_template('budgetform.html')
    
    @app.route('/api/budget_data', methods=['GET'])
    def get_budget_data():
        if 'email' not in session:
            return jsonify({"error": "Unauthorized"}), 401

        email = session['email']
        try:
            budget_data = db.budgets.find_one({"email": email}, {"_id": 0})
            if budget_data:
                return jsonify(budget_data)
            else:
                return redirect(url_for('budget_form'))
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        

    @app.route('/api/budget_data', methods=['POST'])
    def post_budget_data():
        if 'email' not in session:
            return jsonify({"error": "Unauthorized"}), 401

        email = session['email']
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
            db.budgets.update_one(
            {'email': email},
            {
                '$set': {
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
                }
            },
            upsert=True
        )
            return jsonify({"message": "Budget data saved successfully"}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
    @app.route('/profile', methods=['GET', 'POST'])
    def profile():
        if 'email' not in session:
            return redirect(url_for('home'))
        
        if request.method == 'POST':
            form_data = request.get_json()
            if not form_data:
                return jsonify({"error": "No data provided"}), 400

            first_name = form_data.get('firstName')
            last_name = form_data.get('lastName')
            email = form_data.get('email')
            phone_number = form_data.get('phoneNumber')

            # Ensure email from form data matches the session email
            if email != session['email']:
                return jsonify({"error": "Email mismatch"}), 400

            try:
                # Update or insert the profile data
                db.profiles.update_one(
                    {'email': email},
                    {'$set': {
                        'first_name': first_name,
                        'last_name': last_name,
                        'phone_number': phone_number
                    }},
                    upsert=True
                )
                return jsonify({"message": "Profile data saved successfully"}), 201
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        return render_template('profile.html')
    
    @app.route('/get_profile', methods=['GET'])
    def get_profile():
        if 'email' not in session:
            return redirect(url_for('home'))

        email = session['email']
        profile = db.profiles.find_one({"email": email})

        if profile:
            return jsonify({
                "firstName": profile.get('first_name', ''),
                "lastName": profile.get('last_name', ''),
                "email": profile.get('email', ''),
                "phoneNumber": profile.get('phone_number', '')
            })
        else:
            return jsonify({
                "firstName": "",
                "lastName": "",
                "email": "",
                "phoneNumber": ""
            })

