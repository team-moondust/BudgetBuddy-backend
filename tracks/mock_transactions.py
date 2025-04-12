from flask import Blueprint, jsonify

mock_bp = Blueprint('mock', __name__)

@mock_bp.route('/mock/transactions/<account_id>', methods=['GET'])
def mock_transactions(account_id):
    # Ensure account_id is treated as string for URL matching
    account_id = str(account_id)

    if account_id == "1":
        # Account one is for a balanced user, moderate spending
        mock_data = [
            {
                "id": "txn1",
                "merchant_id": "food_merchant_id",
                "vendor_name": "Panera Bread",
                "purchase_date": "2025-04-10 12:30",
                "amount": 18.50
            },
            {
                "id": "txn2",
                "merchant_id": "transport_id",
                "vendor_name": "Uber",
                "purchase_date": "2025-04-09 09:15",
                "amount": 22.75
            },
            {
                "id": "txn3",
                "merchant_id": "groceries_id",
                "vendor_name": "Whole Foods",
                "purchase_date": "2025-04-07 16:20",
                "amount": 65.00
            }
        ]

    elif account_id == "2":
        # Account 2 is for a unbalanced user, overspending on food
        mock_data = [
            {
                "id": "txn1",
                "merchant_id": "food_merchant_id",
                "vendor_name": "Chipotle",
                "purchase_date": "2025-04-10 13:45",
                "amount": 21.50
            },
            {
                "id": "txn2",
                "merchant_id": "food_merchant_id",
                "vendor_name": "McDonald's",
                "purchase_date": "2025-04-09 18:10",
                "amount": 13.00
            },
            {
                "id": "txn3",
                "merchant_id": "food_merchant_id",
                "vendor_name": "Domino's",
                "purchase_date": "2025-04-08 19:00",
                "amount": 26.00
            },
            {
                "id": "txn4",
                "merchant_id": "food_merchant_id",
                "vendor_name": "Taco Bell",
                "purchase_date": "2025-04-07 22:30",
                "amount": 11.75
            },
            {
                "id": "txn5",
                "merchant_id": "food_merchant_id",
                "vendor_name": "Wendy's",
                "purchase_date": "2025-04-06 20:15",
                "amount": 15.25
            }
        ]

    elif account_id == "3":
        # Account 3 is for a unbalanced user, overspending on entertainment
        mock_data = [
            {
                "id": "txn1",
                "merchant_id": "entertainment_id",
                "vendor_name": "Spotify",
                "purchase_date": "2025-04-08 08:00",
                "amount": 9.99
            },
            {
                "id": "txn2",
                "merchant_id": "entertainment_id",
                "vendor_name": "Netflix",
                "purchase_date": "2025-04-06 21:00",
                "amount": 15.49
            },
            {
                "id": "txn3",
                "merchant_id": "entertainment_id",
                "vendor_name": "Steam",
                "purchase_date": "2025-04-04 14:30",
                "amount": 59.99
            },
            {
                "id": "txn4",
                "merchant_id": "entertainment_id",
                "vendor_name": "Twitch Donations",
                "purchase_date": "2025-04-03 17:15",
                "amount": 20.00
            }
        ]

    else:
        return jsonify({ "error": "Account does not exist" }), 404

    return jsonify(mock_data)
