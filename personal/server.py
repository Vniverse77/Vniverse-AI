import json
import sys

import ollama
from flask import Flask, jsonify, request
from flask_cors import CORS

sys.path.insert(0, "/home/vniverse77/Projects/Vniverse-AI")
from personal.memory import get_memory_context, init_db, save_summary
from personal.personality import get_prompt

app = Flask(__name__)
CORS(app)

init_db()
conversation_history = []


def summarize_conversation(messages):
    if len(messages) < 2:
        return None, []

    history_text = ""
    for m in messages:
        role = "Vniverse77" if m["role"] == "user" else "Vniverse-AI"
        history_text += f"{role}: {m['content']}\n"

    summary_response = ollama.chat(
        model="llama3.2",
        messages=[
            {
                "role": "user",
                "content": f"Aşağıdaki sohbeti Türkçe 2-3 cümleyle özetle. Proje, görev ve hedefleri vurgula. Sadece özeti yaz:\n\n{history_text}",
            }
        ],
    )
    summary = summary_response["message"]["content"]

    topics_response = ollama.chat(
        model="llama3.2",
        messages=[
            {
                "role": "user",
                "content": f"Bu özetten konuları JSON listesi olarak çıkar. Sadece JSON yaz:\n{summary}",
            }
        ],
    )

    try:
        topics_text = topics_response["message"]["content"].strip()
        if "[" in topics_text:
            topics_text = topics_text[
                topics_text.index("[") : topics_text.rindex("]") + 1
            ]
        topics = json.loads(topics_text)
    except Exception:
        topics = ["genel"]

    return summary, topics


@app.route("/chat", methods=["POST"])
def chat():
    global conversation_history
    data = request.json
    user_message = data.get("message", "")

    conversation_history.append({"role": "user", "content": user_message})

    messages = [
        {"role": "system", "content": get_prompt(get_memory_context())}
    ] + conversation_history

    response = ollama.chat(model="llama3.2", messages=messages)
    assistant_message = response["message"]["content"]

    conversation_history.append({"role": "assistant", "content": assistant_message})

    return jsonify({"response": assistant_message})


@app.route("/end_session", methods=["POST"])
def end_session():
    global conversation_history

    if len(conversation_history) < 2:
        conversation_history = []
        return jsonify({"status": "Sohbet çok kısa, kaydedilmedi."})

    summary, topics = summarize_conversation(conversation_history)

    if summary:
        save_summary(summary, topics)

    conversation_history = []
    return jsonify({"status": "Kaydedildi.", "summary": summary, "topics": topics})


@app.route("/memories", methods=["GET"])
def memories():
    from personal.memory import get_recent_summaries

    return jsonify({"memories": get_recent_summaries(10)})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "Vniverse-AI personal is online"})


if __name__ == "__main__":
    print("Vniverse-AI (Personal) starting on port 8001...")
    app.run(host="0.0.0.0", port=8001)
