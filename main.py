from dotenv import load_dotenv

load_dotenv()

import os
from flask import Flask, jsonify, request
from flask_cors import CORS

from sklearn.ensemble import IsolationForest
import pandas as pd

# from tracks.nessie import nessie_bp
from tracks.mock_transactions import mock_bp
from db import (
    init_db,
    create_user,
    update_user,
    verify_user,
    find_user_by_email,
    get_transasctions_from_email,
)
from personality import process_transactions, make_notification
import google.generativeai as genai2
from score import (
    explanation_to_score,
    sentence_for_score,
)
from score import gemini_analyze_transactions, math_analyzer
from tracks.nessie_data_generator import generate_realistic_transactions
import json
from datetime import datetime, timedelta


app = Flask(__name__)
CORS(app)  # Enable CORS so frontend can access it


# Initalize database connection
init_db(app)

# Register blueprint
# app.register_blueprint(nessie_bp, url_prefix='/api')
# app.register_blueprint(mock_bp, url_prefix='/api') # account for the fake stuff


@app.route("/api/register", methods=["POST"])
def register():
    """
    endpoint to register a new user.
    Expects JSON with 'name', 'email', 'nessie_id', and 'password'.
    """
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    nessie_id = data.get("nessie_id")
    password = data.get("password")

    # Validate input data
    if not name or not email or not password or not nessie_id:
        return jsonify({"error": "Missing required fields."}), 400

    # Call create_user from db.py
    user = create_user(name, email, password, nessie_id)
    return jsonify({"message": "User created", "user": user, "success": True}), 201


@app.route("/api/login", methods=["POST"])
def test_login():
    """
    Test endpoint to verify user credentials.
    Expects JSON with 'email' and 'password'.
    """
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Missing email or password", "success": False}), 400

    if verify_user(email, password):
        return (
            jsonify(
                {
                    "message": "Login successful",
                    "success": True,
                    "user": find_user_by_email(email),
                }
            ),
            200,
        )
    else:
        return jsonify({"error": "Invalid email or password", "success": False}), 401


@app.route("/api/user", methods=["GET"])
def test_get_user():
    """
    Test endpoint to retrieve a user's details.
    Expects a query parameter ?email=email
    """
    email = request.args.get("email")
    if not email:
        return (
            jsonify({"error": "Missing email query parameter", "success": False}),
            400,
        )

    user = find_user_by_email(email)
    if not user:
        return jsonify({"error": "User not found", "success": False}), 404
    return jsonify(user), 200


@app.route("/api/test/transactions", methods=["GET"])
def test_transactions():
    """
    GET endpoint that takes in ?email=... and returns all transactions.
    """
    email = request.args.get("email")
    if not email:
        return jsonify({"error": "Email is required"}), 400

    transactions = get_transasctions_from_email(email)
    return jsonify(transactions), 200


@app.route("/api/onboarding", methods=["POST"])
def onboarding():
    data = request.get_json()
    try:
        update_user(
            data.get("email"),
            {
                "onboarded": True,
                "pet_choice": data.get("pet_choice"),
                "goals": data.get("goals"),
                "response_style": data.get("response_style"),
                "monthly_budget": data.get("monthly_budget"),
            },
        )
        return jsonify({"success": True}), 201
    except:
        return jsonify({"success": False}), 500


@app.route("/api/notify", methods=["POST"])
def notify():
    data = request.get_json()
    spend_history = data.get("spend_history", [])

    new_spend, recent_spends, big_spends = process_transactions(spend_history)

    if new_spend != "none":
        notification = make_notification(new_spend, recent_spends, big_spends)
        return jsonify({"notification": notification})
    else:
        return jsonify({"notification": "No new transactions. Good Job!"})


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    msg = data.get("chat", "")
    chat_history = data.get("history", [])
    budget = data.get("budget", "")
    response_style = data.get("response_style", "")

    user_email = data.get("email", "")
    spend_history = get_transasctions_from_email(user_email)

    print(spend_history)
    new_spend, recent_spends, big_spends = process_transactions(spend_history)

    genai2.configure(api_key=os.getenv("gemini_api_key"))

    system_prompt = {
        "role": "user",
        "parts": [
            {
                "text": f"""
            Base response style: 
                You are a small, cute financial tomagachi! You will be helping the user manage their spending. 
                Here are their most recent 10 transactions: {recent_spends}
                Here are the most recent large transactions: {big_spends}
                Here's their monthly budget: {budget}
                You should respond in relatively short messages, and if you think its necessary, ask clarifying questions. 
                Respond all lowercase, a bit lowkey, and like a friend showing tough love!
                If they're doing well for their budget, be proud of them. If they're not doing as well, be a bit sarcastic but still helpful,
                making sure to help them through their budget woes.
                You can use markdown formatting, but please don't use headings or titles!
                    examples:
                        "Good job staying under your lunch budget!" 
                        "A bit pricy for tacos huh..." 
                        "A tad expensive, but you've earned it!"
                        "New monitor? But you just got a new phone..." 
            Also take these output style guides into consideration (if the user wants you to be more gentle, more sarcastic, etc):
                Be direct when answering user questions, don't beat around the bush. You should aim to be helpful. 
                {response_style}
            """
            }
        ],
    }

    # Check if the system prompt is already in the history, insert it
    # if not chat_history:
    chat_history.insert(0, system_prompt)

    model = genai2.GenerativeModel(model_name="gemini-2.0-flash")
    chat_session = model.start_chat(history=chat_history)
    response = chat_session.send_message(msg)
    print(response.text)

    return jsonify(
        {
            "text": response.text,
            "history": [
                {"role": msg.role, "parts": [{"text": part.text} for part in msg.parts]}
                for msg in chat_session.history
            ],
        }
    )


@app.route("/api/compute_score", methods=["POST"])
def compute_final_score_for_person():
    """
    Compute the final financial health score for a person by combining:
      - A math analyzer score (for the past 30 days of transactions)
      - An LLM analyzer (Gemini) score on the same data.
    The weights (0.7 and 0.3) should sum to 1.
    """
    person = request.get_json()
    email = person.get("email")

    transactions = get_transasctions_from_email(email)

    now = datetime.now()
    cutoff = now - timedelta(days=30)
    filtered_transactions = [
        txn
        for txn in transactions
        if datetime.strptime(txn["purchase_date"], "%Y-%m-%d %H:%M") >= cutoff
    ]

    monthly_budget = person.get("monthly_budget", 0)
    score_math = math_analyzer(filtered_transactions, monthly_budget)

    # Update the person dict with the filtered spend_history.
    person_filtered = person.copy()
    person_filtered["spend_history"] = filtered_transactions
    score_llm = gemini_analyze_transactions(person_filtered)

    final_score = round((0.7 * score_math) + (0.3 * score_llm))
    explanation = explanation_to_score(person)
    startup_msg = sentence_for_score(person, final_score)
    return jsonify(
        {
            "final_score": final_score,
            "explanation": explanation,
            "startup_msg": startup_msg,
        }
    )


@app.route("/api/fraud", methods=["POST"])
def detect_fraud():

    data = request.get_json()
    user_email = data.get("email")

    spend_history = get_transasctions_from_email(user_email)
    new_spend, _, _ = process_transactions(spend_history)

    df = pd.DataFrame(spend_history)

    df["purchase_date"] = pd.to_datetime(df["purchase_date"])

    df["hour"] = df["purchase_date"].dt.hour
    df["dayofweek"] = df["purchase_date"].dt.dayofweek

    X = df[["amount", "hour", "dayofweek"]]

    # Train Isolation Forest
    model = IsolationForest(contamination=0.05, random_state=18)
    model.fit(X)

    # Prepare new_spend data
    new_dt = pd.to_datetime(new_spend["purchase_date"])
    new_features = [[new_spend["amount"], new_dt.hour, new_dt.dayofweek]]

    # Predict
    prediction = model.predict(new_features)
    is_fraud = prediction[0] == -1

    return is_fraud


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
