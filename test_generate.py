import requests


payload = {
    "email": "marv@dih.com",
    "monthly_budget": 500,
}

score = requests.post("http://127.0.0.1:8080/api/compute_score", json=payload)

print(score.json())


