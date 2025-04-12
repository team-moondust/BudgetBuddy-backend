# import the necessary libraries
import os
from flask_pymongo import PyMongo
from dotenv import load_dotenv

# load environment variables from the .env file
load_dotenv()

# create global variables for the mongo connection and database reference
mongo = None
db = None


def init_db(app):
    global mongo, db

    """
    Initialize connection to MongoDB Atlas using Flask-PyMongo.
    Sets up the global `mongo` and `db` objects.
    """

    # set up the Flask app config for MongoDB using .env variable
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")

    # create the PyMongo client
    mongo = PyMongo(app)

    #  try to connect to MongoDB and confirm connection
    try:
        mongo.cx.server_info()
        print("Connected to MongoDB Atlas!")

        # select the database name from the .env
        db_name = os.getenv("MONGO_DBNAME")

        # set the global db object to the client
        db = mongo.cx[db_name]  
    except Exception as e:
        # if there is an error, print that there is an error and raise an error
        print("Error connecting to MongoDB Atlas:", e)
        raise e


def get_db():
    """
    Return the active MongoDB database object.
    Throws an error if init_db wasn't called yet.
    """
    global db

    # if the database is not initialized, then raise an exception
    if db is None:
        raise Exception("Call init_db(app) first.")

    # else return the database
    return db

def create_user(username, email, password):
    """
    Create a new user document in the 'users' collection.
    WARNING: This stores passwords in plain text, which is not secure at this moment.
    """

    # set db to the database
    db = get_db()
    
    # store the user data in the following format
    user_data = {
        "username": username,
        "email": email,
        "password": password
    }
    
    # insert the user document into the collection
    result = db.users.insert_one(user_data)
    return result.inserted_id

def find_user_by_username(username):
    """
    Retrieve a user document from the 'users' collection by username
    """

    # find the user and return it
    db = get_db()
    return db.users.find_one({"username": username})

def verify_user(username, password):
    """
    Check if a user with given username and password exists.
    """
    # find the username
    user = find_user_by_username(username)

    # if the username doesnt exist then return false
    if not user:
        return False
    
    # else check of the user password is equal to the input password. If equal return true else return false
    return user["password"] == password
