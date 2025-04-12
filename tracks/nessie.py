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


import os
from flask import Blueprint, jsonify

# Load environment variables 
from dotenv import load_dotenv
load_dotenv()

# Blueprint
nessie_bp = Blueprint('nessie', __name__)

# Route for fake transactions
@nessie_bp.route('/transactions/<account_id>', methods=['GET'])
def get_mock_transactions(account_id):
    """
    Returns mock transactions for a given account_id.
    """

    account_id = str(account_id)

    # Example mock data (expand this as needed)
    fake_data = {
        "1": [
            {
                "id": "txn1",
                "merchant": "Panera Bread",
                "category": "Food",
                "amount": 12.50,
                "date": "2025-04-10 12:30"
            },
            {
                "id": "txn2",
                "merchant": "Uber",
                "category": "Transport",
                "amount": 23.40,
                "date": "2025-04-09 09:00"
            }
        ],
        "2": [
            {
                "id": "txn1",
                "merchant": "Steam",
                "category": "Entertainment",
                "amount": 59.99,
                "date": "2025-04-11 16:45"
            },
            {
                "id": "txn2",
                "merchant": "Netflix",
                "category": "Entertainment",
                "amount": 15.49,
                "date": "2025-04-10 21:00"
            }
        ]
    }

    if account_id in fake_data:
        return jsonify(fake_data[account_id])
    else:
        return jsonify({"error": "No transactions found for this account"}), 404


@nessie_bp.errorhandler(404)
def page_not_found(e):
    return jsonify({"error": "This route does not exist"}), 404
