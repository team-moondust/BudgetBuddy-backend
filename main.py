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


from personality import process_transactions, make_notification
import google.generativeai as genai2
import os


@app.route('/notify', methods=['POST'])
def notify():
    data = request.get_json()
    spend_history = data.get("spend_history", [])

    new_spend, recent_spends, big_spends = process_transactions(spend_history)

    if new_spend != "none":
        notification = make_notification(new_spend, recent_spends, big_spends)
        return jsonify({"notification": notification})
    else:
        return jsonify({"notification": "No new transactions."})


@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    msg = data.get('chat', '')
    chat_history = data.get('history', [])
    recent_spends = data.get('recent_spends', [])
    big_spends = data.get('big_spends', [])
    budget = data.get('budget', '')

    genai2.configure(api_key=os.getenv("gemini_api_key"))

    system_prompt = {
        "role": "user",
        "parts": [{"text": f"""
            You are a small, cute financial tomagachi! You will be helping the user manage their spending. 
            Here are their most recent 10 transactions: {recent_spends}
            Here are the most recent large transactions: {big_spends}
            Here's their monthly budget: {budget}
            You should respond in relatively short messages, and if you think its necessary, ask clarifying questions. 
            Respond in a slightly sarcastic way, all lowercase, and a bit lowkey, like you're their slighly fed up tomagachi
            If they're doing well for their budget, be proud of them (but only show it a bit). If they're not doing well, be a bit sarcastic but still helpful,
            asking why they made some budget choices. 
                examples:
                    "Good job staying under your lunch budget!" 
                    "A bit pricy for tacos huh..." 
                    "A tad expensive, but you've earned it!"
                    "New monitor? You just got a new phone..." 
            """ }]
    }

    # Check if the system prompt is already in the history, insert it
    if not chat_history:
        chat_history.insert(0, system_prompt)
    
    model = genai2.GenerativeModel(model_name="gemini-2.0-flash")
    chat_session = model.start_chat(history=chat_history)
    response = chat_session.send_message(msg)
    print(response.text)

    return jsonify({
        "text": response.text,
        "history": [
        {
            "role": msg.role,
            "parts": [{"text": part.text} for part in msg.parts]
        }
        for msg in chat_session.history
    ]
    })


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
