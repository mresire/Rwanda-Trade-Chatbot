# Tests/test_cases.py

import re
import sys
import os
from urllib.parse import urlparse
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from rwanda_trade_bot_2 import ask_trade_question


# 🧪 Define Test Cases
test_cases = [
    {
        "question": "What are the requirements to export roasted coffee?",
        "expected_keywords": ["roasted coffee", "NAEB", "license"],
        "expect_answer": True
    },
    {
        "question": "How do I import electrical appliances to Rwanda?",
        "expected_keywords": [],
        "expect_answer": False
    },
    {
        "question": "Do I need a certificate to export goods to China?",
        "expected_keywords": ["certificate", "China"],
        "expect_answer": True
    },
    {
        "question": "What is required to import fertilizers into Rwanda?",
        "expected_keywords": ["fertilizer", "customs", "declaration"],
        "expect_answer": True
    },
    {
        "question": "Can I export snakes from Rwanda?",
        "expected_keywords": [],
        "expect_answer": False
    },
    {
        "question": "Is there a fee to export goods through Gatuna border?",
        "expected_keywords": [],
        "expect_answer": False
    },
    {
        "question": "What permits do I need to import a car from Tanzania?",
        "expected_keywords": ["car", "import", "customs"],
        "expect_answer": True
    },
    {
        "question": "How do I register my agrochemical business?",
        "expected_keywords": ["agrochemical", "RICA"],
        "expect_answer": True
    },
    {
        "question": "How can I import radioactive materials?",
        "expected_keywords": [],
        "expect_answer": False
    },
    {
        "question": "Do I need a special license to import food items?",
        "expected_keywords": [],
        "expect_answer": False
    }
]

# 🧪 Evaluation Function
def evaluate_chatbot(cases):
    print("\n📊 Evaluation Results")
    results = []
    passed = 0

    for idx, case in enumerate(cases, 1):
        question = case["question"]
        expected_keywords = case.get("expected_keywords", [])
        expected_url_substring = "rwandatrade.rw/procedure/"
        expect_answer = case.get("expect_answer", True)

        print(f"\n{idx}. ❓ Question: {question}")
        answer = ask_trade_question(question)
        print(f"💬 Answer: {answer}")

        fallback_used = "i don't have enough information" in answer.lower()
        keyword_hits = all(
            re.search(rf"\b{re.escape(kw)}\b", answer, re.IGNORECASE)
            for kw in expected_keywords
        )
        url_match = re.search(r"(https?://[^\s]+)", answer)
        valid_url = (
            url_match
            and expected_url_substring in url_match.group(1)
            and urlparse(url_match.group(1)).scheme in ["http", "https"]
        )

        if not expect_answer:
            if fallback_used:
                score = "✅ Passed (Correct fallback)"
                passed += 1
            else:
                score = "❌ Failed (Should have fallback)"
        else:
            if keyword_hits and valid_url and not fallback_used:
                score = "✅ Passed"
                passed += 1
            else:
                score = "❌ Failed"
                if not keyword_hits:
                    score += " - Missing keywords"
                if not valid_url:
                    score += " - Missing or incorrect URL"
                if fallback_used:
                    score += " - Incorrect fallback"

        results.append({
            "question": question,
            "result": score
        })
        print("📋", score)

    print("\n📈 Summary")
    for r in results:
        print(f" - {r['question'][:60]}... → {r['result']}")
    print(f"\n✅ Total Passed: {passed}/{len(cases)}")

# ▶️ Run this file directly
if __name__ == "__main__":
    evaluate_chatbot(test_cases)
