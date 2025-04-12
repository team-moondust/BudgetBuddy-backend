# import the necessary libraries
from flask import Flask, request, jsonify
from flask_cors import CORS
#from tracks.nessie import nessie_bp   --->   change when nessie is back up again
from tracks.mock_transactions import mock_bp

# get the functions from db.py
from db import init_db, get_db, create_user, find_user_by_username, verify_user
from dotenv import load_dotenv
import os

# load environment variables from the .env file
load_dotenv()

# intialize the flask app and enable CORS so it can be accessed by the frontend
app = Flask(__name__)
CORS(app) 


# Initalize database connection
init_db(app)


# Register blueprint
# app.register_blueprint(nessie_bp, url_prefix='/api')
app.register_blueprint(mock_bp, url_prefix='/api') # account for the fake stuff

# ----------
# Temporary endpoints for testing user functions 
# ----------


@app.route('/api/test/register', methods=['POST'])
def test_register():
    """
    Function to register a new user.
    Expects JSON as: {"username": ..., "email": ..., "password": ... }
    """
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    # Validate input data
    if not username or not email or not password:
        return jsonify({"error": "Missing required fields."}), 400

    # Call create_user from db.py
    user_id = create_user(username, email, password)
    return jsonify({"message": "User created", "user_id": str(user_id)}), 201


@app.route('/api/test/login', methods=['POST'])
def test_login():
    """
    Function to verify user credentials.
    Expects JSON: { "username": ..., "password": ... }
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400
    
    if verify_user(username, password):
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401


@app.route('/api/test/user', methods=['GET'])
def test_get_user():
    """
    Retrieves a user's data.
    URL Query Parameter: ?username=<username>
    """
    username = request.args.get('username')
    if not username:
        return jsonify({"error": "Missing username query parameter"}), 400

    user = find_user_by_username(username)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Convert the ObjectId to string for JSON serialization
    user['_id'] = str(user['_id'])
    return jsonify(user), 200

# Entry point for the app
if __name__ == '__main__':
    app.run(port=os.environ.get("PORT") or 3001, debug=True)
