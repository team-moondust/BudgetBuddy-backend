## Additional github repos for this project:

Front-end repo: https://github.com/team-moondust/BudgetBuddy-frontend

Back-end repo (current): https://github.com/team-moondust/BudgetBuddy-backend

Notification repo: https://github.com/team-moondust/BudgetBuddy-notifications-api

# BudgetBuddy with _Tamagotchi_ Twist 💸

# "Because your finances deserve a little fun."

A gamified financial wellness web app that turns your spending habits into the emotional and physical well-being of a virtual pet companion. Your pet thrives when you stick to your budget and struggles when you overspend or make poor financial decisions — making financial health feel personal, emotional, and fun!

---

## Project Overview

**BudgetBuddy with a Tamagotchi Twist** helps users improve their financial habits through a virtual pet that reacts to spending behaviors. Instead of cold numbers and charts, your financial journey is visualized as the life and growth of your own digital buddy.

---

## Core Features

### Reactive Pet Companion

- Pet gets sad, sick, or excited based on your real-world spending
- Visual and mood changes reflect financial habits like overspending or reaching milestones

### Smart Notifications

- Push alerts from your pet with snarky commentary about transactions
- “I’m feeling sluggish from too much takeout this week 😞”
- Custom generated feedback that reflects your unique tone preference (supportive, sarcastic, etc.)

### Budget Scoring

- Combined score from both machine learning and LLM analysis of your recent spending
- Real-time feedback on how well you're managing your money

### Chat Companion

- Gemini-powered chatbot lets your pet talk about your finances
- Reacts to your spending history, budget, and goals in a personalized way!

### Fraud Detection

- Uses IsolationForest ML model to detect abnormal purchases

---

## Tech Stack

| Layer    | Technology Used                                                                    |
| -------- | ---------------------------------------------------------------------------------- |
| Frontend | React + TypeScript, Vite, Zustand, TanStack Router, styled-components, HTML/CSS/JS |
| Backend  | Python (Flask), MongoDB Atlas, Nessie API (Capital One)                            |
| AI & ML  | Google Gemini (chat + analysis), IsolationForest (fraud detection)                 |
| Data Gen | Python-based custom transaction generator with emotional context                   |

---
