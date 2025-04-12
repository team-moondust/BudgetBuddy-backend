import os
import requests
from flask import Blueprint, jsonify
from dotenv import load_dotenv

load_dotenv()

NESSIE_API_KEY = os.getenv("NESSIE_API_KEY")
BASE_URL = "https://api.nessieisreal.com"

nessie_bp = Blueprint('nessie', __name__)

@nessie_bp.route('/transactions/<account_id>', methods=['GET'])
def get_transactions(account_id):
    try:
        url = f"{BASE_URL}/accounts/{account_id}/purchases?key={NESSIE_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error fetching from Nessie: {e}")
        return jsonify({"error": "Failed to fetch transactions"}), 500
