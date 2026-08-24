import os
import re
import pandas as pd
import streamlit as st

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

st.set_page_config(page_title="AI SMART SHOPPING AGENT", page_icon="🛒", layout="centered")
st.title("🛒 AI SMART SHOPPING AGENT")
st.caption("AI-powered product comparison and personalized recommendation")

PRODUCTS = [
    {
        "Product": "ASUS VivoBook",
        "Category": "Laptop",
        "Price": 29999,
        "Rating": 4.6,
        "Reviews": 2100,
        "RAM": "16 GB",
        "Storage": "512 GB SSD",
        "Processor": "Ryzen 5",
    },
    {
        "Product": "HP 15",
        "Category": "Laptop",
        "Price": 28999,
        "Rating": 4.4,
        "Reviews": 1250,
        "RAM": "16 GB",
        "Storage": "512 GB SSD",
        "Processor": "Intel Core i5",
    },
    {
        "Product": "Lenovo IdeaPad",
        "Category": "Laptop",
        "Price": 26999,
        "Rating": 4.3,
        "Reviews": 980,
        "RAM": "8 GB",
        "Storage": "512 GB SSD",
        "Processor": "Ryzen 5",
    },
    {
        "Product": "Dell Inspiron",
        "Category": "Laptop",
        "Price": 31999,
        "Rating": 4.5,
        "Reviews": 1800,
        "RAM": "32 GB",
        "Storage": "1 TB SSD",
        "Processor": "Intel Core i7",
    },
    {
        "Product": "Acer Aspire",
        "Category": "Laptop",
        "Price": 24999,
        "Rating": 4.1,
        "Reviews": 750,
        "RAM": "8 GB",
        "Storage": "512 GB SSD",
        "Processor": "Intel Core i3",
    },
]

# ---------------------------------------------------------------------------
# Sidebar - user requirements
# ---------------------------------------------------------------------------
st.sidebar.header("🎯 Your Requirements")

product_choice = st.sidebar.selectbox(
    "What product will you choose?",
    ["Laptop", "Smartphone", "Headphone", "Tablet"],
)

purpose = st.sidebar.selectbox(
    "🎯 Purpose",
    ["Coding", "Study", "Gaming", "Office", "General Use"],
)

budget = st.sidebar.number_input(
    "💰 Maximum Budget (₹)",
    min_value=5000,
    max_value=500000,
    value=30000,
    step=1000,
)

minimum_rating = st.sidebar.slider("⭐ Minimum Rating", 1.0, 5.0, 4.0, 0.1)

ram_option = st.sidebar.selectbox("💾 RAM", ["Any", "4 GB", "8 GB", "16 GB", "32 GB"])

priority = st.sidebar.selectbox(
    "🏆 Main Priority",
    ["Best Overall", "Lowest Price", "Highest Rating", "Best Specifications"],
)


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
def get_ram_number(ram):
    """Extract the numeric GB value from a RAM string like '16 GB'."""
    match = re.search(r"\d+", str(ram))
    return int(match.group()) if match else 0


def calculate_score(row, budget):
    """Score a product 0-100 based on rating, reviews, price fit, and RAM."""
    rating_score = (float(row["Rating"]) / 5) * 40
    review_score = min(float(row["Reviews"]) / 2000, 1) * 20

    if budget > 0:
        price_score = max(0, 1 - (float(row["Price"]) / budget)) * 25
    else:
        price_score = 0

    ram = get_ram_number(row["RAM"])
    if ram >= 32:
        ram_score = 15
    elif ram >= 16:
        ram_score = 12
    elif ram >= 8:
        ram_score = 8
    else:
        ram_score = 4

    return round(min(rating_score + review_score + price_score + ram_score, 100), 1)


def local_ai_recommendation(best, purpose, budget):
    """Build a human-readable recommendation without calling an LLM."""
    reasons = []

    if best["Price"] <= budget:
        reasons.append("it fits within your budget")

    if best["Rating"] >= 4.5:
        reasons.append("it has an excellent customer rating")
    elif best["Rating"] >= 4.2:
        reasons.append("it has a good customer rating")

    if best["Reviews"] >= 1000:
        reasons.append("it is backed by a large number of customer reviews")

    if get_ram_number(best["RAM"]) >= 16:
        reasons.append("it provides 16 GB or more RAM")

    reasons_text = ", ".join(reasons[:4]) if reasons else "it best matches your requirements overall"

    return f"""
### 🏆 Best Choice
**{best["Product"]}**

### 💡 Why?
For **{purpose}**, this product received the highest overall score among the products matching your requirements.

Main reasons: {reasons_text}.

### 💰 Price
₹{best["Price"]:,}

### ⭐ Rating
{best["Rating"]}/5

### 💻 Key Specifications
- RAM: {best["RAM"]}
- Storage: {best["Storage"]}
- Processor: {best["Processor"]}

### ✅ Final Verdict
**{best["Product"]}** is the best overall match for your requirements.
"""


def real_llm_recommendation(products, purpose, budget, priority):
    """Ask an LLM to explain the recommendation, if an API key is configured."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or not OPENAI_AVAILABLE:
        return None

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    products_text = ""
    for p in products:
        products_text += f"""
        Product: {p["Product"]}
        Price: ₹{p["Price"]}
        Rating: {p["Rating"]}
        Reviews: {p["Reviews"]}
        RAM: {p["RAM"]}
        Storage: {p["Storage"]}
        Processor: {p["Processor"]}
        AI Score: {p["Score"]}
        ---
        """

    prompt = f"""
    You are an intelligent shopping recommendation assistant.

    User purpose: {purpose}
    Maximum budget: ₹{budget}
    Priority: {priority}

    Available products:
    {products_text}

    Choose the best product. Explain:
    1. Best choice
    2. Why it is best
    3. Price
    4. Rating
    5. Specifications
    6. One alternative
    7. Final verdict

    Use only the provided information. Do not invent specifications or prices.
    """

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Main app logic
# ---------------------------------------------------------------------------
if st.button("🔎 Find My Best Product", use_container_width=True):
    df = pd.DataFrame(PRODUCTS)

    filtered = df[df["Category"].str.lower() == product_choice.lower()].copy()
    filtered = filtered[filtered["Price"] <= budget]
    filtered = filtered[filtered["Rating"] >= minimum_rating]

    if ram_option != "Any":
        required_ram = get_ram_number(ram_option)
        filtered = filtered[filtered["RAM"].apply(get_ram_number) >= required_ram]

    if filtered.empty:
        st.warning("No products match your requirements.")
        st.stop()

    filtered["Score"] = filtered.apply(lambda row: calculate_score(row, budget), axis=1)

    if priority == "Lowest Price":
        filtered = filtered.sort_values("Price")
    elif priority == "Highest Rating":
        filtered = filtered.sort_values("Rating", ascending=False)
    else:
        filtered = filtered.sort_values("Score", ascending=False)

    filtered = filtered.reset_index(drop=True)

    st.subheader("📊 Product Comparison")
    comparison = filtered[
        ["Product", "Price", "Rating", "Reviews", "RAM", "Storage", "Processor", "Score"]
    ].rename(columns={"Score": "AI Score"})
    st.dataframe(comparison, use_container_width=True, hide_index=True)

    best = filtered.iloc[0]

    st.subheader("🏆 Best Match")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Product", best["Product"])
    with c2:
        st.metric("Price", f"₹{best['Price']:,}")
    with c3:
        st.metric("AI Score", f"{best['Score']}/100")

    st.subheader("🤖 AI Recommendation")

    llm_result = real_llm_recommendation(
        filtered.head(5).to_dict("records"), purpose, budget, priority
    )

    if llm_result:
        st.success(llm_result)
        st.caption("Recommendation generated using LLM.")
    else:
        st.success(local_ai_recommendation(best, purpose, budget))
        st.caption("Local AI recommendation mode (no API key required).")

    st.subheader("💻 Recommended Specifications")
    s1, s2, s3 = st.columns(3)
    with s1:
        st.write("**💾 RAM**")
        st.write(best["RAM"])
    with s2:
        st.write("**💽 Storage**")
        st.write(best["Storage"])
    with s3:
        st.write("**⚙️ Processor**")
        st.write(best["Processor"])

with st.expander("🧠 How does this AI system work?"):
    st.write(
        """
        1. User selects product requirements.
        2. Products are filtered according to budget, rating and RAM.
        3. Each product receives an AI score.
        4. Products are ranked according to the user's priority.
        5. The shortlisted products are sent to the LLM when an API key is available.
        6. The LLM explains why the selected product is suitable.
        7. If no API key is available, the system automatically uses local
           recommendation logic.
        """
    )

st.divider()
st.caption("AI Smart Shopping Agent • Scholarship Project")