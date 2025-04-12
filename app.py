import os
from flask import Flask, jsonify, request
from flask_cors import CORS
#from tracks.nessie import nessie_bp
from tracks.mock_transactions import mock_bp
from db import init_db, create_user, verify_user, find_user_by_username


app = Flask(__name__)
CORS(app)  # Enable CORS so frontend can access it


# Initalize database connection
init_db(app)

# Register blueprint
# app.register_blueprint(nessie_bp, url_prefix='/api')
app.register_blueprint(mock_bp, url_prefix='/api') # account for the fake stuff

# --- Temporary endpoints for testing user functions ---

@app.route('/api/test/register', methods=['POST'])
def test_register():
    """
    Test endpoint to register a new user.
    Expects JSON with 'username', 'email', and 'password'.
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
    Test endpoint to verify user credentials.
    Expects JSON with 'username' and 'password'.
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
    Test endpoint to retrieve a user's details.
    Expects a query parameter ?username=<username>
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


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
