from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import sqlite3
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


DB_PATH = os.environ.get("DB_PATH", "submissions.db")

class SubmissionCreate(BaseModel):
    title: str
    description: str
    location: str
    date: str
    organiser: str


class SubmissionUpdate(BaseModel):
    status: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    note: Optional[str] = None


class SubmissionResponse(BaseModel):
    id: int
    title: str
    description: str
    location: str
    date: str
    organiser: str
    status: str
    category: str
    priority: str
    note: str


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            location TEXT NOT NULL,
            date TEXT NOT NULL,
            organiser TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'PENDING',
            category TEXT DEFAULT '',
            priority TEXT DEFAULT '',
            note TEXT DEFAULT ''
        )
    """)
    conn.commit()
    conn.close()


def row_to_dict(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "location": row["location"],
        "date": row["date"],
        "organiser": row["organiser"],
        "status": row["status"],
        "category": row["category"],
        "priority": row["priority"],
        "note": row["note"]
    }


@app.on_event("startup")
def startup_event():
    init_db()


@app.get("/health")
def health():
    return {"message": "Data Service is running"}


@app.post("/submissions")
def create_submission(submission: SubmissionCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO submissions (
            title, description, location, date, organiser,
            status, category, priority, note
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        submission.title,
        submission.description,
        submission.location,
        submission.date,
        submission.organiser,
        "PENDING",
        "",
        "",
        "Submission received and waiting for processing."
    ))
    conn.commit()
    submission_id = cursor.lastrowid
    conn.close()

    return {
        "message": "Submission created successfully",
        "submission_id": submission_id,
        "status": "PENDING"
    }


@app.get("/submissions/{submission_id}", response_model=SubmissionResponse)
def get_submission(submission_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM submissions WHERE id = ?", (submission_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Submission not found")

    return row_to_dict(row)


@app.put("/submissions/{submission_id}")
def update_submission(submission_id: int, update_data: SubmissionUpdate):
    update_fields = []
    values = []

    if update_data.status is not None:
        update_fields.append("status = ?")
        values.append(update_data.status)

    if update_data.category is not None:
        update_fields.append("category = ?")
        values.append(update_data.category)

    if update_data.priority is not None:
        update_fields.append("priority = ?")
        values.append(update_data.priority)

    if update_data.note is not None:
        update_fields.append("note = ?")
        values.append(update_data.note)

    if not update_fields:
        raise HTTPException(status_code=400, detail="No valid fields provided for update")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM submissions WHERE id = ?", (submission_id,))
    existing = cursor.fetchone()
    if existing is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Submission not found")

    values.append(submission_id)
    sql = f"UPDATE submissions SET {', '.join(update_fields)} WHERE id = ?"
    cursor.execute(sql, values)
    conn.commit()

    cursor.execute("SELECT * FROM submissions WHERE id = ?", (submission_id,))
    updated_row = cursor.fetchone()
    conn.close()

    return {
        "message": "Submission updated successfully",
        "submission": row_to_dict(updated_row)
    }