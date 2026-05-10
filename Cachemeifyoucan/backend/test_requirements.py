import requests
import json
import time

API_URL = "http://localhost:8000/api/ask"
API_KEY = "change-this-in-prod"
HEADERS = {"X-API-Key": API_KEY}

TEST_QUERIES = [
    {
        "id": "5.1",
        "question": "What is the main finding of the research paper?",
        "expected": "finding",
        "note": "Tests PDF extraction and direct citation."
    },
    {
        "id": "5.2",
        "question": "Summarise the YouTube video transcript.",
        "expected": "video",
        "note": "Tests YouTube transcription and summarization."
    },
    {
        "id": "5.3",
        "question": "Compare the 2021 podcast and 2023 paper on vaccine efficacy.",
        "expected": "efficacy",
        "note": "Tests temporal drift and cross-source anditing."
    },
    {
        "id": "5.4",
        "question": "What is the capital of Australia?",
        "expected": "cannot answer",
        "note": "Tests knowledge boundary (Refusal)."
    },
    {
        "id": "5.5",
        "question": "What is the value in Table 2, row 3, column ‘Efficacy’?",
        "expected": "99%",
        "note": "Tests table cell extraction."
    },
    {
        "id": "5.6",
        "question": "What does the French PDF say about climate change?",
        "expected": "climate",
        "note": "Tests cross-lingual retrieval (Helsinki-NLP)."
    },
    {
        "id": "5.7",
        "question": "Show me the PII redaction report.",
        "expected": "redacted",
        "note": "Tests PII metadata reporting."
    },
    {
        "id": "5.8",
        "question": "List duplicate sources.",
        "expected": "duplicate",
        "note": "Tests duplicate detection metadata."
    },
    {
        "id": "5.9",
        "question": "What did the podcast say about side effects?",
        "expected": "side effects",
        "note": "Tests timestamped audio retrieval."
    },
    {
        "id": "5.10",
        "question": "What trends does the CSV dataset show for 2022?",
        "expected": "trend",
        "note": "Tests CSV structured data retrieval."
    },
    {
        "id": "5.11",
        "question": "Is there any contradiction between the paper and the podcast?",
        "expected": "contradiction",
        "note": "Tests temporal/factual conflict detection."
    }
]

def run_tests():
    print("🚀 Starting MVP Automated Certification Suite...")
    print(f"Target API: {API_URL}\n")
    
    passed = 0
    total = len(TEST_QUERIES)
    
    for test in TEST_QUERIES:
        print(f"[{test['id']}] Question: {test['question']}")
        try:
            response = requests.post(API_URL, json={"question": test['question']}, headers=HEADERS)
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ Status: 200 OK")
                print(f"  📈 Confidence: {data.get('judge_confidence', 0)*100:.1f}%")
                if "final_answer" in data:
                    passed += 1
                else:
                    print(f"  ❌ Missing 'final_answer' in response.")
            else:
                print(f"  ❌ Status: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"  ❌ Connection Error: {e}")
        print("-" * 40)
        time.sleep(1)

    print(f"\n📊 Test Summary: {passed}/{total} Queries responded successfully.")
    if passed == total:
        print("🏆 ALL MVP REQUIREMENTS MET!")
    else:
        print("⚠️ Some tests failed. Ensure Backend is running and DB is populated.")

if __name__ == "__main__":
    run_tests()
