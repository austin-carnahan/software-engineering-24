# routes/routes.py

import sys
import os
import uuid
from flask import render_template, request, jsonify, redirect, url_for, session
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from pymongo import MongoClient
from email_utils import send_email  # Import the send_email function
from datetime import timedelta

def register_routes(app):
    bcrypt = Bcrypt(app)
    jwt = JWTManager(app)

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

        # Extract and save form data
        try:
            db.budgets.update_one(
                {'email': email},
                {
                    '$set': form_data
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

    @app.route('/transactions', methods=['GET', 'POST'])
    def transactions():
        if 'email' not in session:
            return redirect(url_for('home'))

        if request.method == 'POST':
            form_data = request.get_json()
            event_name = form_data.get('event_name')
            event_date = form_data.get('event_date')
            category = form_data.get('category')
            description = form_data.get('description', '')  # Optional field
            price = form_data.get('price')

            if not event_name or not event_date or not category or not price:
                return jsonify({"error": "All required fields must be filled out"}), 400

            try:
                db.transactions.insert_one({
                    'email': session['email'],
                    'event_name': event_name,
                    'event_date': event_date,
                    'category': category,
                    'description': description,
                    'price': float(price)
                })
                return jsonify({"message": "Transaction saved successfully"}), 201
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        return render_template('transactions.html')

    @app.route('/get_transactions', methods=['GET'])
    def get_transactions():
        if 'email' not in session:
            return redirect(url_for('home'))

        email = session['email']
        transactions = db.transactions.find({"email": email})
        transaction_list = []
        for transaction in transactions:
            transaction_list.append({
                "event_name": transaction['event_name'],
                "event_date": transaction['event_date'],
                "category": transaction['category'],
                "description": transaction['description'],
                "price": transaction['price']
            })

        return jsonify(transaction_list)

    # @app.route('/forgot_password', methods=['POST'])
    # def forgot_password():
    #     print("here at forgot")
    #     data = request.get_json()  # Get JSON data
    #     email = data.get('email')  # Extract email from JSON data

    #     if not email:
    #         return jsonify({"error": "Email is required"}), 400

    #     user = db.users.find_one({"email": email})
    #     print("user found", user)
    #     if not user:
    #         return jsonify({"error": "User not found"}), 404
    #     print("passw",user["password"])
        
    #     subject = "Password Reset Request"
    #     body = f"Your password is: {user["password"]}"
        
    #     try:
    #         send_email(subject, body, email)
    #         return jsonify({"message": "Password reset email sent"}), 200
    #     except Exception as e:
    #         return jsonify({"error": str(e)}), 500

    @app.route('/forgot_password', methods=['POST'])
    def forgot_password():
        data = request.get_json()
        email = data.get('email')  # Extract email from JSON data

        if not email:
            return jsonify({"error": "Email is required"}), 400

        user = db.users.find_one({"email": email})
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Generate a unique token
        token = str(uuid.uuid4())
        reset_link = f"http://127.0.0.1:5500/templates/reset_password.html?token={token}"

        # Save the token in the database
        db.password_resets.update_one(
            {"email": email},
            {"$set": {"token": token}},
            upsert=True
        )

        subject = "Password Reset Request"
        body = f"Click the link to reset your password: {reset_link}"
        
        try:
            send_email(subject, body, email)
            return jsonify({"message": "Password reset email sent"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/reset_password/<token>', methods=['GET', 'POST'])
    def reset_password(token):
        if request.method == 'POST':
            data = request.get_json()
            new_password = data.get('password')

            if not new_password:
                return jsonify({"error": "Password is required"}), 400

            reset_entry = db.password_resets.find_one({"token": token})

            if not reset_entry:
                return jsonify({"error": "Invalid or expired token"}), 400

            email = reset_entry['email']
            hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')

            # Update the user's password
            db.users.update_one(
                {"email": email},
                {"$set": {"password": hashed_password}}
            )

            # Remove the token entry after successful password reset
            db.password_resets.delete_one({"token": token})

            return jsonify({"message": "Password has been reset"}), 200

        return render_template('reset_password.html', token=token)