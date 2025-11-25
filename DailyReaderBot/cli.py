import argparse
import json
import random
from pathlib import Path
import requests
from openai import OpenAI

# ===== 설정 =====
OPENAI_API_KEY = "sk-.."
TELEGRAM_TOKEN = ""
TELEGRAM_CHAT_ID = ""

EXTRACTED = Path("extracted")
CONCEPT_DB = Path("concepts.json")

client = OpenAI(api_key=OPENAI_API_KEY)

# ===============================
# 텔레그램 발송
# ===============================
def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text
    })

# ===============================
# 랜덤 원문 + GPT 설명
# ===============================
def send_random_text():
    book_file = random.choice(list(EXTRACTED.glob("*.json")))

    with open(book_file, encoding="utf-8") as f:
        pages = json.load(f)

    page = random.choice(pages)

    prompt = f"""
Create:
You are given an academic passage.

Your task is NOT to summarize or simplify casually.
You must accurately unpack what the text is explaining, based on its internal meaning.

Create:

1) A short section title (not poetic, just descriptive).

2) A clear, plain explanation of what the passage is saying.
   - No academic jargon
   - No decorative language
   - Just explain what is happening conceptually
   - Length is NOT restricted (long is fine)
   - Focus on: what the author is actually arguing, not what it "sounds like"

Do NOT write in an academic style.
Do NOT write like a textbook.
Write like you are calmly explaining to a very intelligent person who hates academic language.

Text:
\"\"\"{page["text"][:2500]}\"\"\"
"""

    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )

    explanation = resp.choices[0].message.content.strip()

    final_message = f"""
📖 Daily Core Text

Book: {book_file.stem}
Page: {page["page"]}

{explanation}

--- Original ---
{page["text"][:1500]}
"""

    send_telegram(final_message)
    print("✅ Random text sent to Telegram.")

# ===============================
# 개념 쿼리 모드
# ===============================
def concept_query(user_query):
    with open(CONCEPT_DB, encoding="utf-8") as f:
        concept_data = json.load(f)

    concept_list = []
    for book, items in concept_data.items():
        for item in items:
            concept_list.append(f"{item} ({book})")

    prompt = f"""
User query:
\"{user_query}\"

Concept candidates:
{concept_list}

Tasks:
1. Select the 10 most relevant concepts.
2. Rank them (1 = most relevant).
3. Give a short explanation ONLY for the top one:
   why it matches the query best.

Format:
1. concept
2. concept
...
10. concept

Top concept explanation:
...
"""

    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    print("\n=== Concept Result ===")
    print(resp.choices[0].message.content.strip())

# ===============================
# HELP
# ===============================
def show_help():
    print("""
Philo Core CLI

Usage:
  python cli.py               → Enter query interaction mode
  python cli.py --random      → Send random core text to Telegram
  python cli.py --help        → Show this help

Modes:
  default : query → concept ranking
  --random: random core text push to Telegram

Example:
  python cli.py
  > my identity dissolves in society
""")

# ===============================
# 엔트리 포인트
# ===============================
def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--random", action="store_true")
    parser.add_argument("--help", action="store_true")

    args = parser.parse_args()

    if args.help:
        show_help()
        return

    if args.random:
        send_random_text()
        return

    # 기본 모드: 쿼리 CLI
    print("🔍 Enter your query (type 'exit' to quit):")
    while True:
        user_input = input("> ")

        if user_input.lower() in ["exit", "quit"]:
            break

        concept_query(user_input)

if __name__ == "__main__":
    main()
