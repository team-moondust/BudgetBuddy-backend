import os
from flask_pymongo import PyMongo
from dotenv import load_dotenv

load_dotenv()

mongo = PyMongo()


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
    }

    db.users.insert_one(user_data)
    return find_user_by_email(email)


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


def verify_user(email, password):
    """
    Verify the user credentials by comparing plain text passwords.
    """
    user = find_user_by_email(email)
    if not user:
        return False
    return user["password"] == password
