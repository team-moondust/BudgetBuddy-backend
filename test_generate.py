import requests


payload = {
    "email": asdfasdfasdf,
    "monthly_budget": asdfasdfasdf,
}

score = requests.post("http://127.0.0.1:8080/api/compute_score", json=payload)


