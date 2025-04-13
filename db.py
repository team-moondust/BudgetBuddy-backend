import os
import requests
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from tracks.nessie_data_generator import generate_realistic_transactions

load_dotenv()

mongo = PyMongo()

NESSIE_API_KEY = os.getenv("NESSIE_API_KEY")
BASE_URL = "http://api.nessieisreal.com"


def init_db(app):
    """
    Initialize connection to MongoDB Atlas using Flask-PyMongo.
    """
    
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")
    print(os.getenv("MONGO_URI"))
    global mongo
    mongo.init_app(app)
    print(app.config["MONGO_URI"])

    # testing the connection
    try:
        mongo.cx.server_info()
        print("Connected to MongoDB Atlas!")
    except Exception as e:
        print("Error connecting to MongoDB Atlas:", e)
        raise e


def get_db():
    """
    Return the database object.
    """
    if not mongo:
        raise Exception("DB not initialized. Call init_db(app) first.")
    return mongo.db

def find_user_by_email(email):
    """
    Retrieve a user document by email.
    """
    db = get_db()
    user = db.users.find_one({"email": email})
    if user:
        user["_id"] = str(user["_id"])
        return user
    return None

def create_user(name, email, password, nessie_id):
    """
    Create a new user with the plain text password.
    WARNING: Storing passwords in plain text is insecure.
    """
    db = get_db()


    user_data = {
        "name": name,
        "email": email,
        "password": password,
        "nessie_id": nessie_id,
        "onboarded": False,
        "pet_choice": -1,
        "goals": "",
        "response_style": "",
        "monthly_budget": -1,
    }

    db.users.insert_one(user_data)
    return find_user_by_email(email)


def verify_user(email, password):
    """
    Verify the user credentials by comparing plain text passwords.
    """
    user = find_user_by_email(email)
    if not user:
        return False
    return user["password"] == password

def update_user(email, updates: dict):
    """
    Update an existing user's fields (no password hashing for demo purposes).
    """
    db = get_db()

    result = db.users.update_one({"email": email}, {"$set": updates})

    if result.matched_count == 0:
        raise ValueError("User not found.")

    return find_user_by_email(email)

def add_generated_entries(account_id):
    filepath = "tracks/cleaned_merchant_ids_final.txt"
    transactions = generate_realistic_transactions(filepath, account_id)
    return transactions

def get_transasctions_from_email(email):
    print("Email!!", email)
    db = get_db()
    user = db.users.find_one({"email": email})
    print("User", user)

    if not user or "nessie_id" not in user:
        return {"error": "User or customer ID not found"}


    customer_id = user["nessie_id"]


    # Step 1: Get account id for the customer
    acc_url = f"{BASE_URL}/customers/{customer_id}/accounts?key={NESSIE_API_KEY}"
    acc_res = requests.get(acc_url)

    if acc_res.status_code != 200:
        return {"error": "Failed to get accounts"}

    accounts = acc_res.json()
    if not accounts:
        return {"error": "No accounts found"}

    account_id = accounts[0]["_id"]  # Assuming one account

    # Step 2: Get transactions for the account
    txn_url = f"{BASE_URL}/accounts/{account_id}/purchases?key={NESSIE_API_KEY}"
    txn_res = requests.get(txn_url)

    if txn_res.status_code != 200:
        return {"error": "Failed to get transactions"}

    return txn_res.json()
