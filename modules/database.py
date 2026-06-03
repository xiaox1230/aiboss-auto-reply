from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

DB_PATH = Path("data/job_booster.sqlite")


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS hr_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hr_message TEXT NOT NULL,
                user_reply TEXT NOT NULL,
                intent TEXT NOT NULL,
                strategy TEXT NOT NULL,
                probability INTEGER NOT NULL,
                risks TEXT,
                suggestions TEXT,
                outcome TEXT DEFAULT '未标记',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS resume_optimizations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resume_text TEXT NOT NULL,
                jd_text TEXT NOT NULL,
                matched_keywords TEXT,
                missing_keywords TEXT,
                optimized_resume TEXT,
                ats_advice TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS delivery_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL,
                title TEXT NOT NULL,
                match_score INTEGER NOT NULL,
                competition INTEGER NOT NULL,
                priority_score INTEGER NOT NULL,
                reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def insert_hr_interaction(record: dict[str, Any]) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO hr_interactions
            (hr_message, user_reply, intent, strategy, probability, risks, suggestions, outcome)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record["hr_message"],
                record["user_reply"],
                record["intent"],
                record["strategy"],
                record["probability"],
                record.get("risks", ""),
                record.get("suggestions", ""),
                record.get("outcome", "未标记"),
            ),
        )
        return int(cur.lastrowid)


def insert_resume_optimization(record: dict[str, Any]) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO resume_optimizations
            (resume_text, jd_text, matched_keywords, missing_keywords, optimized_resume, ats_advice)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                record["resume_text"],
                record["jd_text"],
                record.get("matched_keywords", ""),
                record.get("missing_keywords", ""),
                record.get("optimized_resume", ""),
                record.get("ats_advice", ""),
            ),
        )
        return int(cur.lastrowid)


def replace_delivery_records(records: list[dict[str, Any]]) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM delivery_records")
        conn.executemany(
            """
            INSERT INTO delivery_records
            (company, title, match_score, competition, priority_score, reason)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    item["company"],
                    item["title"],
                    item["match_score"],
                    item["competition"],
                    item["priority_score"],
                    item["reason"],
                )
                for item in records
            ],
        )


def fetch_hr_interactions() -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM hr_interactions ORDER BY created_at DESC, id DESC"
        ).fetchall()


def update_outcome(interaction_id: int, outcome: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "UPDATE hr_interactions SET outcome = ? WHERE id = ?",
            (outcome, interaction_id),
        )


def fetch_resume_optimizations() -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM resume_optimizations ORDER BY created_at DESC, id DESC LIMIT 10"
        ).fetchall()


def fetch_delivery_records() -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM delivery_records ORDER BY priority_score DESC, match_score DESC"
        ).fetchall()
