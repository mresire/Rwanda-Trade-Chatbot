import json
import os
from dotenv import load_dotenv
import openai
import chromadb
from sentence_transformers import SentenceTransformer
from chromadb.utils import embedding_functions
from openai import OpenAI
import logging
logging.getLogger("chromadb").setLevel(logging.ERROR)
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)


# 🔐 Load OpenAI Key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# 📥 Load Rwanda Trade Data
with open("rwanda_trade_data/rwanda_trade_procedures.json", "r") as file:
    data = json.load(file)

# 🧱 Prepare Documents and Metadata
documents = []
metadatas = []
for i, entry in enumerate(data):
    if entry.get("description"):
        content = f"{entry['title']}. {entry['description']}"
        documents.append(content)
        metadatas.append({"url": entry["url"]})

# 🤖 Use Local Embedding Model
sentence_transformer_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

client = chromadb.Client()
collection = client.get_or_create_collection(
    name="rwanda-trade-gpt",
    embedding_function=sentence_transformer_fn
)

# 🧠 Add to ChromaDB if not present
if collection.count() == 0:
    ids = [f"doc_{i}" for i in range(len(documents))]
    collection.add(documents=documents, metadatas=metadatas, ids=ids)
    print("✅ Documents embedded locally and stored.")


# 🤝 Ask GPT-4o for a full answer

clientai = OpenAI(api_key=openai.api_key) 

def ask_trade_question(question, n_results=5):
    results = collection.query(query_texts=[question], n_results=n_results)
    top_doc = results["documents"][0][0]
    top_url = results["metadatas"][0][0]["url"]

    prompt = f"""
You are an expert assistant specialized in Rwanda import and export requirements.
Answer the user's question about trade regulations, procedures, and requirements in Rwanda.

Use ONLY the context provided below to answer the question. If the information is not available in the context,
respond with: "I don't have enough information about that. Please visit the Rwanda Trade Portal for more details."

Instructions:
- When applicable, include:
    1. Required documents
    2. Fees (if available)
    3. Step-by-step process (if available)
    4. Any special requirements or restrictions
    5. Where to apply or obtain the necessary permits/licenses

- Cite the official source by ending the response with:
  “For more information, refer to the official Rwanda Trade Portal: {top_url}”

Consider different phrasings of the same question (e.g., "car" = "vehicle") and infer context accordingly.

---

User Question:
"{question}"

Context (from Rwanda Trade Portal):
{top_doc}

---
Answer:
"""

    response = clientai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content.strip()

# 🔁 CLI Interface
if __name__ == "__main__":
    print("🇷🇼 Rwanda Trade Chatbot (Local Search + GPT-4o Response)")
    print("Type 'exit' to quit.")
    while True:
        q = input("\nAsk your question: ")
        if q.lower() in ["exit", "quit"]:
            break
        response = ask_trade_question(q)
        print("\n💬", response)
