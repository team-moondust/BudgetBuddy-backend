import json
import random
import uuid
from datetime import datetime, timedelta

def generate_sample_transaction(vendor):
    """
    Generate a single transaction dictionary based on the vendor profile.
    
    The vendor profile is a dict with:
      - merchant_id
      - vendor_name
      - min: minimum amount for a transaction
      - max: maximum amount for a transaction
    """
    txn_id = f"txn_{uuid.uuid4().hex[:6]}"
    now = datetime.now()
    # Generate a random purchase date within the past 60 days.
    random_days = random.randint(0, 59)
    random_seconds = random.randint(0, 86399)  # seconds in a day
    purchase_date = now - timedelta(days=random_days, seconds=random_seconds)
    purchase_date_str = purchase_date.strftime("%Y-%m-%d %H:%M")
    amount = round(random.uniform(vendor["min"], vendor["max"]), 2)
    return {
        "id": txn_id,
        "merchant_id": vendor["merchant_id"],
        "vendor_name": vendor["vendor_name"],
        "purchase_date": purchase_date_str,
        "amount": amount
    }

def generate_sample_spend_history(account_type, num_transactions):
    """
    Generate a list of transaction dictionaries based on account type.
    
    account_type determines which vendor list to use:
      "1" - Balanced spending: mix of food, transport, and groceries.
      "2" - Overspending on food.
      "3" - Overspending on entertainment.
    """
    if account_type == "1":
        vendors = [
            {"merchant_id": "food_merchant_id", "vendor_name": "Panera Bread", "min": 15.0, "max": 25.0},
            {"merchant_id": "transport_id", "vendor_name": "Uber", "min": 10.0, "max": 30.0},
            {"merchant_id": "groceries_id", "vendor_name": "Whole Foods", "min": 50.0, "max": 80.0}
        ]
    elif account_type == "2":
        vendors = [
            {"merchant_id": "food_merchant_id", "vendor_name": "Chipotle", "min": 20.0, "max": 30.0},
            {"merchant_id": "food_merchant_id", "vendor_name": "McDonald's", "min": 10.0, "max": 15.0},
            {"merchant_id": "food_merchant_id", "vendor_name": "Domino's Pizza", "min": 20.0, "max": 30.0},
            {"merchant_id": "food_merchant_id", "vendor_name": "Taco Bell", "min": 10.0, "max": 15.0},
            {"merchant_id": "food_merchant_id", "vendor_name": "Wendy's", "min": 10.0, "max": 20.0}
        ]
    elif account_type == "3":
        vendors = [
            {"merchant_id": "entertainment_id", "vendor_name": "Spotify", "min": 5.0, "max": 15.0},
            {"merchant_id": "entertainment_id", "vendor_name": "Netflix", "min": 10.0, "max": 20.0},
            {"merchant_id": "entertainment_id", "vendor_name": "Steam", "min": 50.0, "max": 70.0},
            {"merchant_id": "entertainment_id", "vendor_name": "Twitch Donations", "min": 10.0, "max": 30.0}
        ]
    else:
        vendors = []
    
    transactions = []
    for _ in range(num_transactions):
        vendor = random.choice(vendors)
        txn = generate_sample_transaction(vendor)
        transactions.append(txn)
    return transactions

def generate_data(num_people=50):
    """
    Generate sample data for 'num_people' individuals.
    
    Each person has:
      - "email_id": e.g. "person1@example.com"
      - "person_id": e.g. "person_1"
      - "spend_history": a list of transaction objects (each with id, merchant_id, vendor_name, purchase_date, amount)
      - "necessary_purchases": a string of what the user considers necessary/good purchases
      - "unnecessary_purchases": a string of what the user considers non-essential or wasteful
      - "budget": an integer (e.g., a monthly budget)
      
    Returns:
        dict: A dictionary representing the JSON object.
    """
    necessary_samples = [
        "groceries, bills, rent",
        "utilities, healthcare, food",
        "education, housing, transportation",
        "work essentials, groceries, medicine"
    ]
    unnecessary_samples = [
        "luxury goods, entertainment, junk food",
        "impulse buys, overpriced dining, non-essentials",
        "excessive subscriptions, fast food, high-end gadgets",
        "unnecessary outings, excessive shopping, frivolous expenses"
    ]
    
    people = []
    for i in range(1, num_people + 1):
        account_type = random.choice(["1", "2", "3"])
        num_txns = random.randint(5, 15)
        spend_history = generate_sample_spend_history(account_type, num_txns)
        person = {
            "email_id": f"person{i}@example.com",
            "person_id": f"person_{i}",
            "spend_history": spend_history,
            "necessary_purchases": random.choice(necessary_samples),
            "unnecessary_purchases": random.choice(unnecessary_samples),
            "budget": random.randint(0, 500)
        }
        people.append(person)
    return {"people": people}

if __name__ == "__main__":
    data = generate_data(50)
    print(json.dumps(data, indent=4))
