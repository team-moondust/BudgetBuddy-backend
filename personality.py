
from dotenv import load_dotenv
import os
from google import genai
import pandas as pd
from io import StringIO
from datetime import datetime, timedelta


load_dotenv()   

"""
process the transactions. Returns 2 strings
    1. Expensive transactions from the past 3 months
    2. Most recent 10 transcations
"""
def process_transactions(spend_history):
    df = pd.read_json(StringIO(spend_history))
    df['purchase_date'] = pd.to_datetime(df['purchase_date'])

    # Filter past 3 months
    cutoff_date = datetime.now() - pd.DateOffset(months=3)
    recent_df = df[df['purchase_date'] >= cutoff_date]

    # Get 90th percentile value
    percentile_90 = recent_df['amount'].quantile(0.9)
    top_90_df = recent_df[recent_df['amount'] >= percentile_90]

    # Get most recent 10 transactions
    recent_10_df = df.sort_values(by='purchase_date', ascending=False).head(10)

    # Format function
    def format_transaction(row):
        return f"Transaction id: {row['id']} Vendor: {row['vendor_name']} Purchase date: {row['purchase_date'].date()}, Transaction amount: {row['amount']}"

    # Apply formatting
    top_90_formatted = "\n".join(top_90_df.apply(format_transaction, axis=1))
    recent_10_formatted = "\n".join(recent_10_df.apply(format_transaction, axis=1))

    print("Top 90th percentile transactions in the past 3 months:\n")
    print(top_90_formatted)

    print("\nMost recent 10 transactions:\n")
    print(recent_10_formatted)

    


# talk to the buddy
def converse(transactions):
    gemini_api_key = os.getenv("gemini_api_key")
    client = genai.Client(api_key=gemini_api_key)
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents="Explain how AI works in a few words"
    )
    print(response.text)



if __name__ == "__main__":
    spend_history = '''
    [
        {"id": "txn1", "merchant_id": "food_merchant_id", "vendor_name": "Domino's Pizza", "purchase_date": "2025-04-10", "amount": 35.50},
        {"id": "txn2", "merchant_id": "coffee_merchant", "vendor_name": "Starbucks", "purchase_date": "2025-03-15", "amount": 6.25},
        {"id": "txn3", "merchant_id": "retail", "vendor_name": "Target", "purchase_date": "2025-02-20", "amount": 120.99},
        {"id": "txn4", "merchant_id": "tech", "vendor_name": "Apple Store", "purchase_date": "2025-03-25", "amount": 999.99},
        {"id": "txn5", "merchant_id": "grocery", "vendor_name": "Trader Joe's", "purchase_date": "2025-01-28", "amount": 58.25},
        {"id": "txn6", "merchant_id": "tech", "vendor_name": "Best Buy", "purchase_date": "2025-04-01", "amount": 299.99},
        {"id": "txn7", "merchant_id": "clothing", "vendor_name": "Uniqlo", "purchase_date": "2025-03-30", "amount": 80.00},
        {"id": "txn8", "merchant_id": "food_merchant_id", "vendor_name": "Domino's Pizza", "purchase_date": "2025-02-01", "amount": 20.00},
        {"id": "txn9", "merchant_id": "coffee_merchant", "vendor_name": "Starbucks", "purchase_date": "2025-03-05", "amount": 4.50},
        {"id": "txn10", "merchant_id": "delivery", "vendor_name": "Amazon", "purchase_date": "2025-04-09", "amount": 40.75},
        {"id": "txn11", "merchant_id": "retail", "vendor_name": "Target", "purchase_date": "2025-02-01", "amount": 200.00}
    ]
    '''

    process_transactions(spend_history)
