import json
import random
import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()


# def generate_realistic_transactions(filepath, account_id, num_entries=10):
#     NESSIE_API_KEY = os.getenv("NESSIE_API_KEY")

#     BASE_URL = f"http://api.nessieisreal.com/accounts/{account_id}/purchases?key={NESSIE_API_KEY}"

#     # Load merchant data from file
#     with open(filepath, 'r') as f:
#         merchants = json.load(f)

#     # Define category-based price ranges
#     category_price_ranges = {
#     # 🍽️ Food & Dining
#     "food": (10, 40),
#     "restaurant": (15, 60),
#     "meal_takeaway": (8, 30),
#     "meal_delivery": (10, 35),
#     "pizza": (10, 25),
#     "burritos": (7, 20),
#     "salads": (6, 18),
#     "cafe": (5, 15),
#     "bar": (10, 50),
#     "bakery": (5, 20),

#     # 🛒 Groceries & Stores
#     "grocery": (20, 100),
#     "groceries": (20, 100),
#     "grocery store": (20, 100),
#     "grocery_or_supermarket": (20, 100),
#     "supermarket": (20, 100),
#     "store": (15, 120),
#     "shopping": (15, 120),
#     "retail": (20, 150),
#     "department store": (40, 200),
#     "department_store": (40, 200),
#     "liquor_store": (15, 60),
#     "pharmacy": (10, 80),
#     "pharmacy, food, grocery": (10, 80),
#     "clothing_store": (30, 150),
#     "furniture_store": (80, 500),
#     "home_goods_store": (25, 200),

#     # 💻 Electronics & Subscriptions
#     "electronics_store": (100, 2000),
#     "electronics": (100, 2000),
#     "tech": (100, 1500),
#     "music": (8, 25),
#     "internet": (30, 80),
#     "subscriptions": (7, 20),
#     "phones": (50, 1000),
#     "laptop": (400, 2500),
#     "web": (10, 60),
#    "streaming": (10,30),
#    "music": (5, 20),

#     # 🛠️ Miscellaneous / Services
#     "utility stores": (30, 100),
#     "online vendor": (10, 100),
#     "personal": (10, 100),
#     "health": (20, 150),
#     "car_repair": (100, 500),
#     "florist": (20, 75),
#     }


#     # Flatten price range logic: get best guess for price range per merchant
#     def get_price_range(merchant_categories):
#         for cat in merchant_categories:
#             cat_lower = cat.lower()
#             if cat_lower in category_price_ranges:
#                 return category_price_ranges[cat_lower]
#         return (10, 50)  # default fallback

#     # Filter merchants that match at least one valid category
#     valid_categories = set(category_price_ranges.keys())
#     filtered_merchants = [
#         m for m in merchants
#         if "category" in m and any(cat.lower() in valid_categories for cat in m["category"])
#     ]

#     transactions = []

#     # Make sure at least one is within last 5 minutes
#     recent_idx = random.randint(0, num_entries - 1)

#     for i in range(num_entries):
#         merchant = random.choice(filtered_merchants)
#         min_amt, max_amt = get_price_range(merchant["category"])
#         amount = round(random.uniform(min_amt, max_amt), 2)

#         if i == recent_idx:
#             # Set this one to be within the last 5 minutes
#             purchase_date = datetime.now()
#         else:
#             # Random time in the past 60 days
#             random_days = random.randint(1, 59)
#             random_seconds = random.randint(0, 86399)
#             purchase_date = datetime.now() - timedelta(days=random_days, seconds=random_seconds)

#         txn = {
#             "merchant_id": merchant["_id"],
#             "medium": "balance",
#             "purchase_date": purchase_date.strftime("%Y-%m-%d %H:%M"),
#             "amount": amount,
#             "description": merchant["name"]
#         }

#         # response = requests.post(BASE_URL, json=txn)
#         # print(f"Status: {response.status_code}, Response: {response.json()}")
#         transactions.append(txn)


#     return transactions

def generate_realistic_transactions(filepath, account_id, num_entries=10):
    NESSIE_API_KEY = os.getenv("NESSIE_API_KEY")

    BASE_URL = f"http://api.nessieisreal.com/accounts/{account_id}/purchases?key={NESSIE_API_KEY}"

    # Load merchant data from file
    with open(filepath, 'r') as f:
        merchants = json.load(f)

    # Define category-based price ranges
    category_price_ranges = {
    # 🍽️ Food & Dining
    "food": (10, 40),
    "restaurant": (15, 60),
    "meal_takeaway": (8, 30),
    "meal_delivery": (10, 35),
    "pizza": (10, 25),
    "burritos": (7, 20),
    "salads": (6, 18),
    "cafe": (5, 15),
    "bar": (10, 50),
    "bakery": (5, 20),

    # 🛒 Groceries & Stores
    "grocery": (20, 100),
    "groceries": (20, 100),
    "grocery store": (20, 100),
    "grocery_or_supermarket": (20, 100),
    "supermarket": (20, 100),
    "store": (15, 120),
    "shopping": (15, 120),
    "retail": (20, 150),
    "department store": (40, 200),
    "department_store": (40, 200),
    "liquor_store": (15, 60),
    "pharmacy": (10, 80),
    "pharmacy, food, grocery": (10, 80),
    "clothing_store": (30, 150),
    "furniture_store": (80, 500),
    "home_goods_store": (25, 200),

    # 💻 Electronics & Subscriptions
    "electronics_store": (100, 2000),
    "electronics": (100, 2000),
    "tech": (100, 1500),
    "music": (8, 25),
    "internet": (30, 80),
    "subscriptions": (7, 20),
    "phones": (50, 1000),
    "laptop": (400, 2500),
    "web": (10, 60),
    "streaming": (10,30),
    "music": (5, 20),

    # 🛠️ Miscellaneous / Services
    "utility stores": (30, 100),
    "online vendor": (10, 100),
    "personal": (10, 100),
    "health": (20, 150),
    "car_repair": (100, 500),
    "florist": (20, 75),
    }


    # Flatten price range logic: get best guess for price range per merchant
    def get_price_range(merchant_categories):
        for cat in merchant_categories:
            cat_lower = cat.lower()
            if cat_lower in category_price_ranges:
                return category_price_ranges[cat_lower]
        return (10, 50)  # default fallback

    # Filter merchants that match at least one valid category
    valid_categories = set(category_price_ranges.keys())
    filtered_merchants = [
        m for m in merchants
        if "category" in m and any(cat.lower() in valid_categories for cat in m["category"])
    ]

    transactions = []

    # Make sure at least one is within last 5 minutes
    recent_idx = random.randint(0, num_entries - 1)

    for i in range(num_entries):
        # Step 1: pick a random category
        selected_category = random.choice(list(category_price_ranges.keys()))

        # Step 2: pick a merchant that has this category
        matching_merchants = [
            m for m in merchants if "category" in m and
            any(cat.lower() == selected_category for cat in m["category"])
        ]

        if not matching_merchants:
            continue  # skip if no matching merchants

        merchant = random.choice(matching_merchants)
        min_amt, max_amt = category_price_ranges[selected_category]
        amount = round(random.uniform(min_amt, max_amt), 2)

        # Recent transaction logic
        if i == recent_idx:
            purchase_date = datetime.now()
        else:
            random_days = random.randint(1, 59)
            random_seconds = random.randint(0, 86399)
            purchase_date = datetime.now() - timedelta(days=random_days, seconds=random_seconds)



        txn = {
            "merchant_id": merchant["_id"],
            "medium": "balance",
            "purchase_date": purchase_date.strftime("%Y-%m-%d %H:%M"),
            "amount": amount,
            "description": merchant["name"]
        }

        response = requests.post(BASE_URL, json=txn)
        print(f"Status: {response.status_code}, Response: {response.json()}")
        transactions.append(txn)


    return transactions

#print(generate_realistic_transactions("cleaned_merchant_ids_final.txt", "67fb242d9683f20dd51955a2"))

def generate_realistic_transactions_hard(filepath, account_id):
    NESSIE_API_KEY = os.getenv("NESSIE_API_KEY")

    BASE_URL = f"http://api.nessieisreal.com/accounts/{account_id}/purchases?key={NESSIE_API_KEY}"

    txn = {
        "merchant_id": "57cf75cea73e494d8675edca",
        "medium": "balance",
        "purchase_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "amount": 12.45,
        "description": "Taco Bell"
    }
    
    response = requests.post(BASE_URL, json=txn)

    return response