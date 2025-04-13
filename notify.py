from dotenv import load_dotenv
import time

import urllib

from db import get_transasctions_from_email
load_dotenv()

import os
import requests

import pandas as pd

# from tracks.nessie import nessie_bp
from tracks.mock_transactions import mock_bp

from personality import process_transactions, make_notification
import google.generativeai as genai2
from score import (
    explanation_to_score,
    sentence_for_score,
)
from score import gemini_analyze_transactions, math_analyzer
from tracks.nessie_data_generator import generate_realistic_transactions
import json
from datetime import datetime, timedelta



previous_new_spend = None

def compute_final_score_for_person(email):
    """
    Compute the final financial health score for a person by combining:
      - A math analyzer score (for the past 30 days of transactions)
      - An LLM analyzer (Gemini) score on the same data.
    The weights (0.7 and 0.3) should sum to 1.
    """

    emailEncoded = urllib.parse.quote(email)

    person = requests.get(f"http://localhost:8080/api/user?email={emailEncoded}").json()
    transactions = requests.get(f"http://localhost:8080/api/test/transactions?email={emailEncoded}").json()

    now = datetime.now()
    cutoff = now - timedelta(days=30)
    filtered_transactions = [
        txn
        for txn in transactions
        if datetime.strptime(txn["purchase_date"], "%Y-%m-%d %H:%M") >= cutoff
    ]
    monthly_budget = person.monthly_budget

    score_math = math_analyzer(filtered_transactions, monthly_budget)

    # Update the person dict with the filtered spend_history.

    person_filtered = person.copy()
    person_filtered["spend_history"] = filtered_transactions
    score_llm = gemini_analyze_transactions(person_filtered)

    final_score = round((0.7 * score_math) + (0.3 * score_llm))
    explanation = explanation_to_score(person)
    startup_msg = sentence_for_score(person, final_score)

    image = 0
    if 80 <= final_score <= 100:
        image = 1
    elif 60 <= final_score < 80:
        image = 2
    elif 40 <= final_score < 60:
        image = 3
    elif 20 <= final_score < 40:
        image = 4
    else:
        image = 5

    return final_score, explanation, startup_msg, image

print(compute_final_score_for_person("johndoe@example.com"))


def notify(email):
    spend_history = get_transasctions_from_email(email)
    new_spend, recent_spends, big_spends = process_transactions(spend_history)
    if new_spend != "none" and new_spend != previous_new_spend:
        previous_new_spend = new_spend
        notification = make_notification(new_spend, recent_spends, big_spends)
        return notification, email
    else:
        return None


while True:
    result = notify("marv@dih.com")
    if result:

        notification, email = result
        _, _, _ , image_Id = compute_final_score_for_person(email)

        data = {
            "email": email,
            "title": "Buddy Checking In!",
            "body": notification,
            "imageId": image_Id,
        }

        jssssson = json.dumps(data)

        requests.post(os.getenv("notification_url"), data=jssssson)

    time.sleep(5*60)
    
    # email, title, body, imageId