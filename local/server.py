import sys

import ollama
from flask import Flask, jsonify, request
from flask_cors import CORS

sys.path.insert(0, "/home/vniverse77/Projects/Vniverse-AI")
from personality import SYSTEM_PROMPT

app = Flask(__name__)
CORS(app)

conversation_history = {}


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    session_id = data.get("session_id", "default")

    if session_id not in conversation_history:
        conversation_history[session_id] = []

    conversation_history[session_id].append({"role": "user", "content": user_message})

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history[
        session_id
    ]

    response = ollama.chat(model="llama3.2", messages=messages)

    assistant_message = response["message"]["content"]

    conversation_history[session_id].append(
        {"role": "assistant", "content": assistant_message}
    )

    if len(conversation_history[session_id]) > 20:
        conversation_history[session_id] = conversation_history[session_id][-20:]

    return jsonify({"response": assistant_message})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "Vniverse-AI is online"})


if __name__ == "__main__":
    print("Vniverse-AI backend starting on port 8000...")
    app.run(host="0.0.0.0", port=8000)
