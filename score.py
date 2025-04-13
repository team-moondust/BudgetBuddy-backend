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
    Compute a score (0–100) based on how responsibly the user is spending,
    factoring in how far we are into the current month.

    Penalizes more harshly for overspending early in the month.

    Returns:
        float: Score between 0 (bad) and 100 (great).
    """
    now = datetime.now()
    current_day = now.day
    days_in_month = (datetime(now.year, now.month % 12 + 1, 1) - timedelta(days=1)).day

    # Time progress: how far we are into the month (0.0 to 1.0)
    time_progress = current_day / days_in_month
    expected_spending = monthly_budget * time_progress

    # Filter transactions from the current month
    filtered_transactions = [
        txn for txn in transactions
        if datetime.strptime(txn["purchase_date"], "%Y-%m-%d %H:%M").month == now.month
        and datetime.strptime(txn["purchase_date"], "%Y-%m-%d %H:%M").year == now.year
    ]

    total_spent = sum(txn["amount"] for txn in filtered_transactions)

    if total_spent <= expected_spending:
        return 100.0
    else:
        overspend = total_spent - expected_spending
        overspend_ratio = overspend / monthly_budget

        # The earlier it is in the month, the higher this boost
        early_penalty_multiplier = 1 + ((1 - time_progress) * 2)

        penalty = overspend_ratio * 100 * early_penalty_multiplier
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
    goals = person.get("goals", "")
    budget = person.get("monthly_budget", 0)
    
    prompt = (
        "You are a financial advisor. Given the following spending data and user priorities, "
        "return only a single integer penalty between 0 and 50 (without any explanation). "
        "A penalty of 0 means the spending perfectly aligns with the user's priorities and budget, "
        "while 50 means the spending is extremely wasteful.\n\n"
        "User's goals: " + goals + "\n"
        "Monthly budget: " + str(budget) + "\n"
        "Spending data (transactions):\n" + json.dumps(transactions, indent=4)
    )
    
    gemini_api_key = os.getenv("gemini_api_key")
    client = genai.Client(api_key=gemini_api_key)
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=prompt
        )
        try:
            penalty = float(response.text.strip())
        except Exception:
            penalty = 0  # fallback if parsing fails
    except Exception:
        penalty = 0  # fallback if API call fails.
    
    penalty = min(penalty, 50)
    llm_score = max(0, 100 - (penalty * 2))
    return llm_score

# -----------------------------
# 3. Explanation Generator
# -----------------------------
def explanation_to_score(person):
    """
    Generate a combined explanation using both a math-based summary and a Gemini-based explanation.
    This version works with the new user_data structure which includes keys:
        "email_id", "name", "nessie_id", "goals", "response_style", and "monthly_budget".
    """
    # Use provided spend_history if available; otherwise, default to an empty list.
    transactions = person.get("spend_history", [])
    monthly_budget = person.get("monthly_budget", 0)
    
    # Filter transactions from the past 30 days.
    now = datetime.now()
    cutoff = now - timedelta(days=30)
    filtered_transactions = [
        txn for txn in transactions
        if datetime.strptime(txn["purchase_date"], "%Y-%m-%d %H:%M") >= cutoff
    ]
    
    total_spent = sum(txn["amount"] for txn in filtered_transactions)
    ideal_ratio = 0.75
    ideal_spending = monthly_budget * ideal_ratio
    math_deviation = total_spent - ideal_spending
    math_explanation = (
        f"In the past 30 days, total spending is ${total_spent:.2f} versus an ideal spending of "
        f"${ideal_spending:.2f} for a budget of ${monthly_budget}. This is a deviation of ${math_deviation:.2f}."
    )
    
    # Use the user's goals from the new JSON structure.
    goals = person.get("goals", "")
    prompt = (
        "you are a small, cute financial tomagachi, a bit fed up but still caring. "
        "Respond in a slightly sarcastic way, all lowercase, and a bit lowkey, like you're their slightly fed up tomagachi. "
        "Examples: 'good job staying under your lunch budget!', 'a bit pricy for tacos, huh...', "
        "'a tad expensive, but you've earned it!', 'new monitor? you just got a new phone...'\n\n"
        "here's some info on your owner's finances:\n\n"
        "user goals: " + goals + "\n"
        "monthly budget: " + str(monthly_budget) + "\n"
        "spending data (past 30 days):\n" + json.dumps(filtered_transactions, indent=4) + "\n\n"
        "explain in exactly 2 short sentences why there's a penalty on their spending. "
        "if they’re staying under budget, drop a tiny compliment; if not, be sarcastic and ask why they made those budget choices."
    )
        
    gemini_api_key = os.getenv("gemini_api_key")
    client = genai.Client(api_key=gemini_api_key)
    
    try:
        explanation_response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        gemini_explanation = explanation_response.text.strip()
    except Exception:
        gemini_explanation = "No detailed explanation available due to an API error."
    
    explanation = math_explanation + " " + gemini_explanation
    return explanation

# -----------------------------
# 4. Explanation Generator
# -----------------------------
def sentence_for_score(person, score):
    prompt = (
        "you are a small, cute financial tomagachi, a bit fed up but still caring. "
        "respond in a lowkey sarcastic yet supportive tone, all lowercase. "
        f"here's the owner's current score: {score}.\n\n"
        "respond with a SINGLE, short opener (under 10 words) that sets the tone: "
        "if the score is high (close to 100), say something positive; "
        "if the score is low, say something offering constructive criticism. "
        "do not mention the actual score, and avoid excessive sarcasm. "
        "examples: 'we can do better...', 'keep it up!', 'awesome, keep it rolling!', "
        "'not looking too shabby!', 'c'mon, step it up' BE UNIQUE"
    )

    gemini_api_key = os.getenv("gemini_api_key")
    client = genai.Client(api_key=gemini_api_key)
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        sentence = response.text.strip()
    except Exception:
        sentence = "No detailed explanation available due to an API error."
    
    return sentence