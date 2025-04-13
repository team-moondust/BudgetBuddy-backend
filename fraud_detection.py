import pandas as pd
from db import get_transasctions_from_email 
from personality import process_transactions
from sklearn.ensemble import IsolationForest
import os
from flask import Flask, jsonify, request
from flask_cors import CORS


# app = Flask(__name__)
# CORS(app)  # Enable CORS so frontend can access it

# @app.route("/api/fraud", methods=["POST"])
# def detect_fraud():

#     data = request.get_json()
#     user_email = data.get("email")

#     spend_history = get_transasctions_from_email(user_email)
#     new_spend, _ , _ = process_transactions(spend_history)

#     df = pd.DataFrame(spend_history)

#     df['purchase_date'] = pd.to_datetime(df['purchase_date'])

#     df['hour'] = df['purchase_date'].dt.hour
#     df['dayofweek'] = df['purchase_date'].dt.dayofweek

#     X = df[['amount', 'hour', 'dayofweek']]

#     # Train Isolation Forest
#     model = IsolationForest(contamination=0.05, random_state=18)
#     model.fit(X)

#     # Prepare new_spend data
#     new_dt = pd.to_datetime(new_spend['purchase_date'])
#     new_features = [[
#         new_spend['amount'],
#         new_dt.hour,
#         new_dt.dayofweek
#     ]]

#     # Predict
#     prediction = model.predict(new_features) 
#     is_fraud = prediction[0] == -1

#     return is_fraud
