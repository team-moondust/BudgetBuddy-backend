import requests
from data.generate_data import generate_data
from personality import process_transactions  # if it's named flask_app.py

json_data = generate_data(1)
person = json_data['people'][0]
budget = person['budget']
spend_history = person['spend_history']

new_spend, recent_spends, big_spends = process_transactions(spend_history)

# First message
msg = "what can i do to reduce my expenses :("
payload = {
    "chat": msg,
    "history": [],
    "recent_spends": recent_spends,
    "big_spends": big_spends,
    "budget": budget
}
response = requests.post("http://127.0.0.1:9000/chat", json=payload)



try:
    result = response.json()
    print("AI:", result["text"])
    msg = "hmm could you tell me more about overall strategy?"
    payload["chat"] = msg
    payload["history"] = result["history"]

    response = requests.post("http://127.0.0.1:9000/chat", json=payload)
    result = response.json()
    print("AI:", result["text"])

except Exception as e:
    print("Error parsing response as JSON:", e)
