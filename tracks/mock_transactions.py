from flask import Blueprint, jsonify

mock_bp = Blueprint('mock', __name__)

@mock_bp.route('/mock/transactions/<account_id>', methods=['GET'])
def mock_transactions(account_id):
    # This data mimics what Nessie would return
    mock_data = [
        {
            "id": "txn1",
            "merchant_id": "food_merchant_id",
            "vendor_name": "Domino's Pizza",
            "purchase_date": "2025-04-10",
            "amount": 35.50
        },
        {
            "id": "txn2",
            "merchant_id": "entertainment_id",
            "vendor_name": "Netflix Subscription",
            "purchase_date": "2025-04-08",
            "amount": 15.99
        },
        {
            "id": "txn3",
            "merchant_id": "groceries_id",
            "vendor_name": "Trader Joe's",
            "purchase_date": "2025-04-07",
            "amount": 72.00
        },
        {
            "id": "txn4",
            "merchant_id": "food_merchant_id",
            "vendor_name": "Uber Eats",
            "purchase_date": "2025-04-11",
            "amount": 16.69
        },
        {
            "id": "txn5",
            "merchant_id": "food_merchant_id",
            "vendor_name": "Taco Bell",
            "purchase_date": "2025-04-08",
            "amount": 12.69
        },
        {
            "id": "txn6",
            "merchant_id": "entertainment_id",
            "vendor_name": "Spotfy",
            "purchase_date": "2025-04-01",
            "amount": 20.45
        },
        {
            "id": "txn6",
            "merchant_id": "shopping_id",
            "vendor_name": "H&M",
            "purchase_date": "2025-03-15",
            "amount": 35.23
        }
    ]
    return jsonify(mock_data)
