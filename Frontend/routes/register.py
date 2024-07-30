from flask import Flask, render_template, request
from pymongo import MongoClient  # Assuming you're using MongoDB

# Replace with your MongoDB Atlas connection string
client = MongoClient("mongodb+srv://your_username:your_password@your_cluster.net/your_database")
db = client.get_database("your_database_name")

app = Flask(__name__)

@app.route('/')
def home():
  return render_template('index.html')

@app.route('/register', methods=["POST"])
def register():
  # Get form data
  email = request.form["email"]
  password = request.form["password"]
  nickname = request.form["nickname"]
  favorite_food = request.form["favorite_food"]
  favorite_movie = request.form["favorite_movie"]

  # Validation (optional, implement as needed)
  #  - Check if email is already registered
  #  - Ensure password meets complexity requirements

  # Hash password before storing (use bcrypt or similar)
  hashed_password = # Implement password hashing logic here

  # Create user document
  user = {"email": email, "password": hashed_password, "nickname": nickname,
          "favorite_food": favorite_food, "favorite_movie": favorite_movie}

  # Insert user data into MongoDB
  db.users.insert_one(user)

  # Registration success or error handling
  return render_template("success.html")  # or handle errors

if __name__ == '__main__':
  app.run(debug=True)
