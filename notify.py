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







print("--------------------------------------------------------------------------------------------------")

previous_new_spend = None

def notify(email):
    global previous_new_spend
    emailEncoded = urllib.parse.quote(email)

    spend_history = requests.get(f"http://localhost:8080/api/test/transactions?email={emailEncoded}").json()
    
    print(spend_history)

    new_spend, recent_spends, big_spends = process_transactions(spend_history)
    if new_spend != "none" and new_spend != previous_new_spend:
        previous_new_spend = new_spend
        notification = make_notification(new_spend, recent_spends, big_spends)
        return notification, email
    else:
        return None


while True:
    result = notify("johndoe@example.com")
    if result:
        notification, email = result

        emailEncoded = urllib.parse.quote(email)
        person = requests.get(f"http://localhost:8080/api/user?email={emailEncoded}").json()
        res = requests.post("http://localhost:8080/api/compute_score", data=json.dumps({"email": "johndoe@example.com", "monthly_budget":person["monthly_budget"]}), headers={
            "Content-Type": "application/json"
        }).json()

        # print(res)
        # if not res["success"]:
        #     print("fail")
        # else:
        #     print(res["res"])

        image = res["res"]["image"]

        data = {
            "email": email,
            "title": "Buddy Checking In!",
            "body": notification,
            "imageId": image,
        }

        jssssson = json.dumps(data)

        requests.post(os.getenv("notification_url"), headers={"Content-Type": "application/json"} , data=jssssson)

    time.sleep(5*60)
    
