from dotenv import load_dotenv
import time
import urllib
import requests
from personality import process_transactions, make_notification
import json

load_dotenv()

ACCOUNT_EMAIL = "abc"
BACKEND_URL = "https://budgetbuddy-backend-1060199417258.us-central1.run.app/api"
NOTIFICATION_URL = (
    "https://budgetbuddy-notifications-api-1060199417258.us-central1.run.app/"
)

# deduping
previous_new_spend = None

def notify(email):
    global previous_new_spend
    emailEncoded = urllib.parse.quote(email)

    spend_history = requests.get(
        f"{BACKEND_URL}/test/transactions?email={emailEncoded}"
    ).json()

    print(spend_history)

    new_spend, recent_spends, big_spends = process_transactions(spend_history)
    if new_spend != "" and new_spend != "none" and new_spend != previous_new_spend:
        previous_new_spend = new_spend
        notification = make_notification(new_spend, recent_spends, big_spends)
        return notification, email
    else:
        return None


print("Starting initial attempt...")
while True:
    result = notify(ACCOUNT_EMAIL)
    if result:
        print(result)
        notification, email = result

        emailEncoded = urllib.parse.quote(email)

        person = requests.get(f"{BACKEND_URL}/user?email={emailEncoded}").json()
        res = requests.post(
            f"{BACKEND_URL}/compute_score",
            data=json.dumps(
                {"email": ACCOUNT_EMAIL, "monthly_budget": person["monthly_budget"]}
            ),
            headers={"Content-Type": "application/json"},
        ).json()

        image = res["res"]["image"]
        pet_choice = person["pet_choice"]

        print(
            requests.post(
                NOTIFICATION_URL + "/push",
                headers={"Content-Type": "application/json"},
                data=json.dumps(
                    {
                        "email": email,
                        "title": "Buddy Checking In!",
                        "body": notification,
                        "imageId": image,
                        "pet_choice": pet_choice,
                    }
                ),
            )
        )

    print("Retrying in 5 seconds...")
    time.sleep(5)
