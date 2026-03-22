import json
import sqlite3
from datetime import datetime

DB_PATH = "/home/vniverse77/Projects/Vniverse-AI/personal/memory.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            summary TEXT,
            topics TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_summary(summary: str, topics: list):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO conversations (date, summary, topics, created_at)
        VALUES (?, ?, ?, ?)
    """,
        (
            datetime.now().strftime("%Y-%m-%d"),
            summary,
            json.dumps(topics),
            datetime.now().isoformat(),
        ),
    )
    conn.commit()
    conn.close()


def get_recent_summaries(limit=5):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT date, summary, topics FROM conversations ORDER BY created_at DESC LIMIT ?",
        (limit,),
    )
    rows = c.fetchall()
    conn.close()
    result = []
    for row in rows:
        result.append({"date": row[0], "summary": row[1], "topics": json.loads(row[2])})
    return result


def get_memory_context():
    summaries = get_recent_summaries(5)
    if not summaries:
        return ""
    context = "## Geçmiş sohbetlerden öğrendiklerin:\n"
    for s in summaries:
        context += f"- [{s['date']}] {s['summary']}\n"
    return context
