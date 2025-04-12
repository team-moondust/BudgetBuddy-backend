from dotenv import load_dotenv
import os
import json
from datetime import datetime, timedelta
from data.generate_data import generate_data
import google.generativeai as genai2
from google import genai

# -----------------------------
# 1. Math Analyzer
# -----------------------------

load_dotenv()   

def math_analyzer(transactions, monthly_budget):
    """
    Compute a numeric score (0-100) based on how close total spending is to an ideal percentage 
    of the monthly budget. Here, the ideal spending is set to 75% of monthly_budget.
    
    The score is 100 if total spending equals 75% of the monthly_budget,
    and decreases linearly as spending deviates from that ideal.
    """
    total_spent = sum(t["amount"] for t in transactions)
    ideal_ratio = 0.75
    ideal_spending = monthly_budget * ideal_ratio
    # Calculate deviation ratio (as a fraction of ideal_spending)
    deviation = abs(total_spent - ideal_spending) / ideal_spending
    # Scale deviation to a penalty between 0 and 100:
    penalty = deviation * 100
    # The math score is 100 minus the penalty (capped between 0 and 100)
    score = max(0, 100 - penalty)
    return round(score, 2)
 

# -----------------------------
# 2. LLM (Gemini) Analyzer Simulation
# -----------------------------
def gemini_analyze_transactions(person):
    """
    Performs an analysis of a person's spending data using Gemini's API.
    The input is a dictionary representing a person's data that includes:
      - "spend_history": a list of transaction objects,
      - "necessary_purchases": a string of what purchases the user considers necessary,
      - "unnecessary_purchases": a string of what purchases the user considers unnecessary,
      - "budget": an integer representing the monthly budget.
    
    This function builds a prompt and sends it to the Gemini API.
    It expects Gemini to return a numeric penalty (0-50) as text.
    The penalty is then converted into a simulated LLM score on a 0-100 scale.
    
    Returns:
        float: The final Gemini-based score (0-100), where lower numbers indicate more wasteful spending.
    """
    transactions = person.get("spend_history", [])
    necessary = person.get("necessary_purchases", "")
    unnecessary = person.get("unnecessary_purchases", "")
    budget = person.get("budget", 0)
    
    prompt = (
        "You are a financial advisor. Given the following spending data and user priorities, "
        "return only a single integer penalty between 0 and 50 (without any explanation). "
        "A penalty of 0 means the spending perfectly aligns with the user's priorities and budget, "
        "while 50 means the spending is extremely wasteful.\n\n"
        "User's necessary purchases: " + necessary + "\n"
        "User's unnecessary purchases: " + unnecessary + "\n"
        "Monthly budget: " + str(budget) + "\n"
        "Spending data (transactions):\n" + json.dumps(transactions, indent=4)
    )
    
    gemini_api_key = os.getenv("gemini_api_key")
    client = genai.Client(api_key=gemini_api_key)
    
    try:
        notification_response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=prompt
        )

        try:
            penalty = float(notification_response.text.strip())
        except Exception as e:
            penalty = 0  # fallback penalty if parsing fails
    except Exception as api_error:
        penalty = 0  # fallback penalty if the API call fails.
    
    # Cap the penalty at 50.
    penalty = min(penalty, 50)
    
    # Convert penalty into a Gemini score on a scale of 0 to 100.
    # 0 penalty -> score 100; 50 penalty -> score 0.
    llm_score = max(0, 100 - (penalty * 2))
    print(f'this is the {llm_score}')
    return llm_score

# -----------------------------
# 3. Final Aggregator
# -----------------------------
def compute_final_score_for_person(person, w_math=0.7, w_llm=0.3):
    """
    Compute the final financial health score for one person by combining:
      - The math analyzer score (which measures budget adherence using only the past 30 days of transactions)
      - The LLM analyzer (simulated) score (which penalizes wasteful spending) also using only the past 30 days.
    
    The weights (w_math and w_llm) should sum to 1.
    """
    transactions = person.get("spend_history", [])
    monthly_budget = person.get("budget", 0)
    
    # Filter transactions to only include those from the past 30 days.
    now = datetime.now()
    cutoff = now - timedelta(days=30)
    filtered_transactions = [
        txn for txn in transactions
        if datetime.strptime(txn["purchase_date"], "%Y-%m-%d %H:%M") >= cutoff
    ]
    
    # Calculate math analyzer score using only the filtered transactions.
    score_math = math_analyzer(filtered_transactions, monthly_budget)
    
    # Create a copy of the person data with only the filtered spend_history.
    person_filtered = person.copy()
    person_filtered["spend_history"] = filtered_transactions
    
    # Calculate the LLM (Gemini) analyzer score using the filtered person data.
    score_llm = gemini_analyze_transactions(person_filtered)
    
    final_score = round((w_math * score_math) + (w_llm * score_llm), 2)
    return final_score

# -----------------------------
# 4. Main Function
# -----------------------------
def main():
    # Generate JSON data for 50 people from generate_data.py.
    data = generate_data(15)
    
    results = []
    for person in data["people"]:
        final_score = compute_final_score_for_person(person, w_math=0.7, w_llm=0.3)
        results.append({
            "person_id": person["person_id"],
            "email_id": person["email_id"],
            "spend_history": person["spend_history"],
            "budget": person["budget"],
            "necessary_purchases": person["necessary_purchases"],
            "unnecessary_purchases": person["unnecessary_purchases"],
            "final_score": final_score
        })
    
    # Output the final scores as a JSON string.
    print(json.dumps(results, indent=4))


if __name__ == "__main__":
    main()
