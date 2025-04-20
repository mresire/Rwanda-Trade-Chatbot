# 🇷🇼 Rwanda Trade Chatbot 🤖

A smart assistant designed to help users retrieve Rwanda’s import/export requirements quickly, accurately, and with references to the official Rwanda Trade Portal.

This project was developed as a final project for the 17-630 Prompt Engineering course at Carnegie Mellon University Africa.

---

## 📌 Project Overview

Navigating trade regulations in Rwanda can be time-consuming and overwhelming. This chatbot streamlines that process by leveraging prompt engineering techniques to build two chatbot models capable of answering user questions with reference-backed answers.

---

## 🧠 Features

- **Model Selection** – Switch between:
  - `Model 1`: Keyword-based procedure match + GPT-3.5 summarization
  - `Model 2`: ChromaDB vector search + GPT-4o contextual response
- **Streamlit UI** – Simple, interactive chatbot frontend
- **Citations** – Each response includes direct links to the Rwanda Trade Portal
- **Fallback** – Graceful response when context is missing
- **Rating System** – Users rate answers (stored in `logs/ratings.csv`)
- **Feedback Viewer** – View recent feedback in-app

---

## 🚀 How to Run

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/rwanda-trade-chatbot.git
cd rwanda-trade-chatbot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

(You’ll need: `streamlit`, `openai`, `chromadb`, `sentence-transformers`, `python-dotenv`, `pandas`)

### 3. Add your OpenAI key

Create a `.env` file:

```
OPENAI_API_KEY=your-api-key-here
```

### 4. Launch the chatbot

```bash
streamlit run streamlit_app.py
```

---

## 📂 Project Structure

```
rwanda-trade-chatbot/
├── streamlit_app.py              # Main UI
├── rwanda_trade_bot_1.py         # Keyword-search model
├── rwanda_trade_bot_2.py         # Vector-search model
├── Tests/
│   └── test_cases.py             # Evaluation tests
├── logs/
│   └── ratings.csv               # User feedback storage
├── rwanda_trade_data/
│   └── rwanda_trade_procedures.json  # Base knowledge
├── .env                          # OpenAI API key (not committed)
└── README.md
```

---

## 🔍 Prompt Engineering Strategy

- Used structured system prompts to enforce:
  - Context-only answering
  - Citation with portal links
  - Fallback handling when data is missing
  - Procedural structure (docs, fees, steps, etc.)

- Model 1 uses simplified retrieval logic
- Model 2 applies semantic search via ChromaDB + Sentence Transformers

---

## 📊 Evaluation

- ✅ Keyword matching
- ✅ Citation checking
- ✅ Fallback detection
- ✅ User ratings (5-star scale)
- ✅ Model comparison

Run evaluation:

```bash
python Tests/test_cases.py
```

---

## 📈 Next Steps

- Add support for Kinyarwanda/French queries
- Improve ranking of vector results
- Add admin dashboard to analyze feedback
- Deploy chatbot to the web

---

## 📝 License

MIT License

---

## 🙏 Acknowledgments

Built for 17-630 Prompt Engineering @ CMU Africa – Spring 2025  
Inspired by Rwanda’s need for accessible trade information
