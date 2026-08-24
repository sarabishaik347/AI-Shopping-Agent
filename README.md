# 🛒 AI Smart Shopping Agent

A Streamlit-based shopping recommendation app that helps users choose the best product based on their **purpose, budget, and priorities**.

The app compares products using **price, rating, reviews, RAM, and specifications**, then recommends the product with the highest overall score.

## ✨ Features

* 🎯 Purpose-based product recommendation
* 💰 Budget-aware scoring
* ⭐ Rating and review-based comparison
* 💻 RAM and specification scoring
* 🏆 Best Overall, Lowest Price, Highest Rating, and Best Specifications priorities
* 🤖 Optional OpenAI-powered recommendation explanation
* 📊 Simple Streamlit interface

## ⚙️ How It Works

```text
User Input
   ↓
Purpose + Budget + Priority
   ↓
Product Scoring
   ↓
Price + Rating + Reviews + RAM
   ↓
Highest Scoring Product
   ↓
Recommendation + Explanation
```

The main scoring logic is handled by:

```python
get_ram_number()
calculate_score()
get_ai_recommendation()
```

The application first calculates a score for each product. The product with the best score is selected, and the app generates reasons explaining the recommendation.

## 🛠️ Tech Stack

* Python
* Streamlit
* Pandas
* OpenAI API
* Regular Expressions

## 🚀 Run Locally

Install the required packages:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
streamlit run app.py
```

## 🔑 OpenAI

OpenAI integration is optional. If an API key is available, the app can generate a more natural explanation for the recommended product.

Keep your API key private and never commit it to GitHub.

## 📁 Project Structure

```text
AI-Smart-Shopping-Agent/
│
├── app.py
├── requirements.txt
└── README.md
```

## 🔮 Future Improvements

* Live product prices and availability
* More product categories
* Better personalized scoring
* More detailed product comparisons
* Integration with e-commerce APIs

## 👨‍💻 Project

AI Smart Shopping Agent — a simple recommendation system that combines **rule-based product scoring with optional AI assistance**.
