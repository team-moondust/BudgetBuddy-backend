import os
import requests
from flask_pymongo import PyMongo
from dotenv import load_dotenv

load_dotenv()

mongo = PyMongo()

NESSIE_API_KEY = os.getenv("NESSIE_API_KEY")
BASE_URL = "http://api.nessieisreal.com"


def init_db(app):
    """
    Initialize connection to MongoDB Atlas using Flask-PyMongo.
    """
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")
    global mongo
    mongo.init_app(app)

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


def create_user(username, email, password, nessie_id):
    """
    Create a new user with the plain text password.
    WARNING: Storing passwords in plain text is insecure.
    """
    db = get_db()

    user_data = {
        "username": username,
        "email": email,
        "password": password,
        "nessie_id": nessie_id,
        "onboarded": False,
    }

    db.users.insert_one(user_data)
    return find_user_by_email(email)


def find_user_by_email(email):
    """
    Retrieve a user document by username.
    """
    db = get_db()
    user = db.users.find_one({"email": email})
    if user:
        user["_id"] = str(user["_id"])
        return user
    return None


def verify_user(email, password):
    """
    Verify the user credentials by comparing plain text passwords.
    """
    user = find_user_by_email(email)
    if not user:
        return False
    return user["password"] == password

def get_transasctions_from_email(email):
    db = get_db()
    user = db.users.find_one({"email": email})

    if not user or "nessie_customer_id" not in user:
        return {"error": "User or customer ID not found"}


    customer_id = user["nessie_customer_id"]


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
