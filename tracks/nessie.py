# import os
# import requests
# from flask import Blueprint, jsonify
# from dotenv import load_dotenv

# load_dotenv()

# NESSIE_API_KEY = os.getenv("NESSIE_API_KEY")
# BASE_URL = "https://api.nessieisreal.com"

# nessie_bp = Blueprint('nessie', __name__)

# @nessie_bp.route('/transactions/<account_id>', methods=['GET'])
# def get_transactions(account_id):
#     try:
#         url = f"{BASE_URL}/accounts/{account_id}/purchases?key={NESSIE_API_KEY}"
#         response = requests.get(url)
#         response.raise_for_status()
#         return jsonify(response.json())
#     except requests.exceptions.RequestException as e:
#         print(f"Error fetching from Nessie: {e}")
#         return jsonify({"error": "Failed to fetch transactions"}), 500

# ------------------------------------------------------------------------------------------

# import os
# from flask import Blueprint, jsonify

# # Load environment variables 
# from dotenv import load_dotenv
# load_dotenv()

# # Blueprint
# nessie_bp = Blueprint('nessie', __name__)

# # Route for fake transactions
# @nessie_bp.route('/transactions/<account_id>', methods=['GET'])
# def get_mock_transactions(account_id):
#     """
#     Returns mock transactions for a given account_id.
#     """

#     account_id = str(account_id)

#     # Example mock data (expand this as needed)
#     fake_data = {
#         "1": [
#             {
#                 "id": "txn1",
#                 "merchant": "Panera Bread",
#                 "category": "Food",
#                 "amount": 12.50,
#                 "date": "2025-04-10 12:30"
#             },
#             {
#                 "id": "txn2",
#                 "merchant": "Uber",
#                 "category": "Transport",
#                 "amount": 23.40,
#                 "date": "2025-04-09 09:00"
#             }
#         ],
#         "2": [
#             {
#                 "id": "txn1",
#                 "merchant": "Steam",
#                 "category": "Entertainment",
#                 "amount": 59.99,
#                 "date": "2025-04-11 16:45"
#             },
#             {
#                 "id": "txn2",
#                 "merchant": "Netflix",
#                 "category": "Entertainment",
#                 "amount": 15.49,
#                 "date": "2025-04-10 21:00"
#             }
#         ]
#     }

#     if account_id in fake_data:
#         return jsonify(fake_data[account_id])
#     else:
#         return jsonify({"error": "No transactions found for this account"}), 404


# @nessie_bp.errorhandler(404)
# def page_not_found(e):
#     return jsonify({"error": "This route does not exist"}), 404


# ----------------------------------------------------------------------

import os
import requests
from flask import Blueprint, jsonify
from dotenv import load_dotenv

load_dotenv()

NESSIE_API_KEY = os.getenv("NESSIE_API_KEY")
BASE_URL = "http://api.nessieisreal.com"

nessie_bp = Blueprint('nessie', __name__)

@nessie_bp.route('/customers', methods=['GET'])
def get_all_customers():
    """
    Get all customers from the Nessie API.
    """
    try:
        url = f"{BASE_URL}/customers?key={NESSIE_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error fetching customers: {e}")
        return jsonify({"error": "Failed to fetch customers"}), 500


@nessie_bp.route('/customers/<customer_id>/accounts', methods=['GET'])
def get_accounts_for_customer(customer_id):
    """
    Get all accounts associated with a customer.
    """
    try:
        url = f"{BASE_URL}/customers/{customer_id}/accounts?key={NESSIE_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error fetching accounts: {e}")
        return jsonify({"error": "Failed to fetch accounts"}), 500


@nessie_bp.route('/accounts/<account_id>/purchases', methods=['GET'])
def get_purchases_for_account(account_id):
    """
    Get all purchases for an account (transaction history).
    """
    try:
        url = f"{BASE_URL}/accounts/{account_id}/purchases?key={NESSIE_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error fetching transactions: {e}")
        return jsonify({"error": "Failed to fetch transactions"}), 500
