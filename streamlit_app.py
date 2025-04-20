# streamlit_app.py
import streamlit as st
from importlib import import_module
import pandas as pd
import datetime
import os

# --- UI Setup ---
st.set_page_config(page_title="🇷🇼 Rwanda Trade Chatbot", layout="centered")
st.title("💬 Rwanda Trade Chatbot")
st.markdown("Ask about import/export requirements and get reliable answers from official data sources.")

# --- Model Selection ---
st.sidebar.header("⚙️ Settings")
model_choice = st.sidebar.selectbox("Choose a model version:", ["Model 1 (Keyword Search)", "Model 2 (Vector Search)"])

# --- Load selected model ---
if model_choice == "Model 1 (Keyword Search)":
    model = import_module("rwanda_trade_bot_1").RwandaTradeBot()
    model_version = "Model 1"
    is_model_1 = True
else:
    model = import_module("rwanda_trade_bot_2")
    model_version = "Model 2"
    is_model_1 = False

# --- Chat Input ---
st.markdown("### 🤖 Ask your question")
user_input = st.text_input("", placeholder="e.g. What are the requirements to export coffee?", label_visibility="collapsed")

if user_input:
    with st.spinner("Thinking..."):
        try:
            if is_model_1:
                response = model.query(user_input)
            else:
                response = model.ask_trade_question(user_input)

            st.markdown("### 📘 Answer")
            st.success(response)

            # Rating widget
            st.markdown("### 📝 How helpful was this answer?")
            rating = st.radio("Rate the answer:", ["⭐️⭐️⭐️⭐️⭐️ Excellent", "⭐️⭐️⭐️⭐️ Good", "⭐️⭐️⭐️ Okay", "⭐️⭐️ Poor", "⭐️ Terrible"], index=None)

            if rating:
                st.success(f"✅ Thanks for rating: {rating}")

                # Save rating
                log_data = {
                    "timestamp": datetime.datetime.now().isoformat(),
                    "model_version": model_version,
                    "question": user_input,
                    "response": response,
                    "rating": rating
                }
                df = pd.DataFrame([log_data])
                os.makedirs("logs", exist_ok=True)
                log_path = "logs/ratings.csv"
                if os.path.exists(log_path):
                    df.to_csv(log_path, mode='a', header=False, index=False)
                else:
                    df.to_csv(log_path, index=False)

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# --- Feedback Viewer ---
with st.expander("🗃 View Previous Feedback"):
    log_path = "logs/ratings.csv"
    if os.path.exists(log_path):
        df = pd.read_csv(log_path)
        if not df.empty:
            recent_feedback = df.tail(5)[["timestamp", "model_version", "question", "rating"]]
            st.dataframe(recent_feedback.rename(columns={
                "timestamp": "🕒 Timestamp",
                "model_version": "🧠 Model",
                "question": "❓ Question",
                "rating": "⭐️ Rating"
            }), use_container_width=True)
        else:
            st.info("No feedback entries yet.")
    else:
        st.info("Feedback log file not found.")

# --- Footer ---
st.markdown("---")
st.caption("Built with ❤️ for Rwanda trade intelligence")
