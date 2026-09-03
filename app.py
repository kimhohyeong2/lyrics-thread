from __future__ import annotations

import sqlite3
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from lyrics_thread import analyze_lyrics, analyze_sentence

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "lyrics_thread.db"

app = Flask(__name__)


def connect() -> sqlite3.Connection:
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db


def init_db() -> None:
    with connect() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS lines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                song TEXT NOT NULL,
                artist TEXT NOT NULL DEFAULT '',
                section TEXT NOT NULL DEFAULT '',
                line_no INTEGER NOT NULL,
                text TEXT NOT NULL,
                language TEXT NOT NULL,
                pattern_id TEXT,
                label TEXT NOT NULL,
                template TEXT,
                function TEXT
            )
        """)
        db.commit()


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/analyze")
def analyze():
    payload = request.get_json(force=True)
    lyrics = payload.get("lyrics", "")
    language = payload.get("language") or None
    return jsonify(analyze_lyrics(lyrics, language))


@app.post("/api/save")
def save():
    payload = request.get_json(force=True)
    song = (payload.get("song") or "").strip()
    artist = (payload.get("artist") or "").strip()
    section = (payload.get("section") or "").strip()
    lyrics = payload.get("lyrics", "")
    language = payload.get("language") or None

    if not song:
        return jsonify({"error": "song is required"}), 400

    rows = analyze_lyrics(lyrics, language)
    with connect() as db:
        for row in rows:
            db.execute(
                """
                INSERT INTO lines
                (song, artist, section, line_no, text, language, pattern_id, label, template, function)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    song, artist, section, row["line_no"], row["text"], row["language"],
                    row["pattern_id"], row["label"], row["template"], row["function"],
                ),
            )
        db.commit()

    return jsonify({"saved": len(rows)})


@app.get("/api/search")
def search():
    text = (request.args.get("text") or "").strip()
    if not text:
        return jsonify([])

    matches = analyze_sentence(text)
    pattern_ids = [m.pattern_id for m in matches]
    if not pattern_ids:
        return jsonify([])

    marks = ",".join("?" for _ in pattern_ids)
    with connect() as db:
        rows = db.execute(
            f"""
            SELECT song, artist, section, line_no, text, language,
                   pattern_id, label, template, function
            FROM lines
            WHERE pattern_id IN ({marks})
            ORDER BY song, section, line_no
            """,
            pattern_ids,
        ).fetchall()

    return jsonify([dict(row) for row in rows])


@app.get("/api/stats")
def stats():
    with connect() as db:
        rows = db.execute(
            """
            SELECT pattern_id, label, template, function, COUNT(*) AS count
            FROM lines
            WHERE pattern_id IS NOT NULL
            GROUP BY pattern_id, label, template, function
            ORDER BY count DESC, pattern_id
            """
        ).fetchall()
    return jsonify([dict(row) for row in rows])


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5050)
