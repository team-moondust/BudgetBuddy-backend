
from dotenv import load_dotenv
import os
from google import genai
import google.generativeai as genai2

import pandas as pd
from io import StringIO
from datetime import datetime, timedelta

from generate_data import generate_data

from flask import Flask, request, jsonify
from flask_cors import CORS


load_dotenv()   


app = Flask(__name__)


"""
process the transactions. Returns 2 strings
    1. Expensive transactions from the past 3 months
    2. Most recent 10 transcations
"""
def process_transactions(spend_history):
    df = pd.DataFrame(spend_history)
    df['purchase_date'] = pd.to_datetime(df['purchase_date'])

    # Check for transaction in the last 5 minutes
    now = datetime.now()
    five_minutes_ago = now - timedelta(minutes=5)
    new_transaction_df = df[df['purchase_date'] >= five_minutes_ago]
    new_transaction = not new_transaction_df.empty

    # Filter past 3 months
    cutoff_date = now - pd.DateOffset(months=3)
    recent_df = df[df['purchase_date'] >= cutoff_date]

    # 90th percentile of past 3 months
    percentile_90 = recent_df['amount'].quantile(0.9)
    top_90_df = recent_df[recent_df['amount'] >= percentile_90]

    # Most recent 10 transactions
    recent_10_df = df.sort_values(by='purchase_date', ascending=False).head(10)

    # Format function
    def format_transaction(row):
        return f"Transaction id: {row['id']} Vendor: {row['vendor_name']} Purchase date: {row['purchase_date'].strftime('%Y-%m-%d %H:%M')}, Transaction amount: {row['amount']}"

    # Apply formatting
    top_90_formatted = "\n".join(top_90_df.apply(format_transaction, axis=1))
    recent_10_formatted = "\n".join(recent_10_df.apply(format_transaction, axis=1))
    new_transaction_formatted = "\n".join(new_transaction_df.apply(format_transaction, axis=1)) if new_transaction else "none"

    return (new_transaction_formatted, recent_10_formatted, top_90_formatted)

    

"""
Given a new transaction has been made (a transaction in the previous 5 minutes), generate a short message for the notification

"Good job staying under your lunch budget!" 
"A bit pricy for tacos huh..." 
"A tad expensive, but you've earned it!"
"New monitor? You just got a new phone..." 
"""
def make_notification(new_spend, recent_spends, big_spends):
    gemini_api_key = os.getenv("gemini_api_key")
    client = genai.Client(api_key=gemini_api_key)

    # this occurs when a new transaction is made
    notification_response = client.models.generate_content(
        model="gemini-2.0-flash", 
        contents=f"""
            You are a small, cute finaincial buddy! You will be helping the user manage their spending. 
            They just made a new transaction: {new_spend}
            Here are their most recent 10 transactions: {recent_spends}
            Here are the most recent large transactions: {big_spends}

            Make a short n sweet message for a notification based on this new transaction. 
            Examples:
                "Good job staying under your lunch budget!" - Spent a reasonable amount for lunch
                "A bit pricy for tacos huh..." - Spent too much for a meal
                "A tad expensive, but you've earned it!" - Spent too much, but has been hitting savings goals
                "New monitor? You just got a new phone..." - Made too many big purchases for budget
        """
    )
    print(notification_response.text)

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
        "history": chat_session.history
    })



if __name__ == "__main__":  
    # spend_history = '''
    # [
    #     {"id": "txn1", "merchant_id": "food_merchant_id", "vendor_name": "Domino's Pizza", "purchase_date": "2025-04-12 2:30", "amount": 35.50},
    #     {"id": "txn2", "merchant_id": "coffee_merchant", "vendor_name": "Starbucks", "purchase_date": "2025-03-15 09:45", "amount": 6.25},
    #     {"id": "txn3", "merchant_id": "retail", "vendor_name": "Target", "purchase_date": "2025-02-20 14:10", "amount": 120.99},
    #     {"id": "txn4", "merchant_id": "tech", "vendor_name": "Apple Store", "purchase_date": "2025-03-25 13:30", "amount": 999.99},
    #     {"id": "txn5", "merchant_id": "grocery", "vendor_name": "Trader Joe's", "purchase_date": "2025-01-28 18:25", "amount": 58.25},
    #     {"id": "txn6", "merchant_id": "tech", "vendor_name": "Best Buy", "purchase_date": "2025-04-01 11:40", "amount": 299.99},
    #     {"id": "txn7", "merchant_id": "clothing", "vendor_name": "Uniqlo", "purchase_date": "2025-03-30 16:50", "amount": 80.00},
    #     {"id": "txn8", "merchant_id": "food_merchant_id", "vendor_name": "Domino's Pizza", "purchase_date": "2025-02-01 12:00", "amount": 20.00},
    #     {"id": "txn9", "merchant_id": "coffee_merchant", "vendor_name": "Starbucks", "purchase_date": "2025-03-05 08:10", "amount": 4.50},
    #     {"id": "txn10", "merchant_id": "delivery", "vendor_name": "Amazon", "purchase_date": "2025-04-09 21:00", "amount": 40.75},
    #     {"id": "txn11", "merchant_id": "retail", "vendor_name": "Target", "purchase_date": "2025-02-01 10:30", "amount": 200.00}
    # ]
    # '''
    # (new_spend, recent_spends, big_spends) = process_transactions(spend_history)
    # make_notification(new_spend, recent_spends, big_spends)


    json_data = generate_data(1)


    person = json_data.get('people')[0]
    budget = person.get("budget")
    spend_history = person.get("spend_history")

    (new_spend, recent_spends, big_spends) = process_transactions(spend_history)

    msg = "what can i do to reduce my expenses :("
    (response, history) = chat(msg, [], recent_spends, big_spends, budget)
    msg = "hmm could you tell me more about overall strategy?"
    (response, history) = chat(msg, history, recent_spends, big_spends, budget)


