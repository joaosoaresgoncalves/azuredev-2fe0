"""Simulated email backend – FastAPI + SQLite (in-memory)."""

from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Query
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base

# ── Database setup ──────────────────────────────────────────────
engine = create_engine("sqlite:///emails.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class EmailRow(Base):
    __tablename__ = "emails"
    id = Column(Integer, primary_key=True, autoincrement=True)
    sender = Column(String, nullable=False)
    recipient = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    body = Column(String, default="")
    timestamp = Column(DateTime, default=datetime.utcnow)
    read = Column(Boolean, default=False)


SEED_EMAILS = [
    {"sender": "eric@work.com", "recipient": "you@email.com",
     "subject": "Happy Hour", "body": "We're planning drinks this Friday!",
     "timestamp": datetime.fromisoformat("2025-06-13T04:48:59.096908"), "read": False},
    {"sender": "boss@email.com", "recipient": "you@email.com",
     "subject": "Q3 Review", "body": "Please prepare your quarterly report by EOD.",
     "timestamp": datetime.fromisoformat("2025-06-12T09:15:00.000000"), "read": False},
    {"sender": "alice@work.com", "recipient": "you@email.com",
     "subject": "Design Feedback", "body": "Can you review the latest mockups?",
     "timestamp": datetime.fromisoformat("2025-06-11T14:30:00.000000"), "read": False},
    {"sender": "newsletter@updates.com", "recipient": "you@email.com",
     "subject": "Weekly Digest", "body": "Here are this week's top stories.",
     "timestamp": datetime.fromisoformat("2025-06-10T07:00:00.000000"), "read": True},
    {"sender": "boss@email.com", "recipient": "you@email.com",
     "subject": "Team Lunch", "body": "Lunch at noon on Thursday. Don't be late!",
     "timestamp": datetime.fromisoformat("2025-06-09T11:45:00.000000"), "read": False},
]


def _reset_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    db = SessionLocal()
    for e in SEED_EMAILS:
        db.add(EmailRow(**e))
    db.commit()
    db.close()


# Initialise on import
_reset_db()

# ── FastAPI app ─────────────────────────────────────────────────
app = FastAPI()


class SendPayload(BaseModel):
    sender: str = "you@email.com"
    recipient: str
    subject: str
    body: str = ""


def _row_to_dict(row: EmailRow) -> dict:
    return {
        "id": row.id,
        "sender": row.sender,
        "recipient": row.recipient,
        "subject": row.subject,
        "body": row.body,
        "timestamp": row.timestamp.isoformat() if row.timestamp else None,
        "read": row.read,
    }


@app.post("/send")
def send_email(payload: SendPayload):
    db = SessionLocal()
    email = EmailRow(
        sender=payload.sender,
        recipient=payload.recipient,
        subject=payload.subject,
        body=payload.body,
    )
    db.add(email)
    db.commit()
    db.refresh(email)
    result = _row_to_dict(email)
    db.close()
    return result


@app.get("/emails")
def list_emails():
    db = SessionLocal()
    rows = db.query(EmailRow).order_by(EmailRow.timestamp.desc()).all()
    result = [_row_to_dict(r) for r in rows]
    db.close()
    return result


@app.get("/emails/unread")
def unread_emails(sender: Optional[str] = None):
    db = SessionLocal()
    q = db.query(EmailRow).filter(EmailRow.read == False)
    if sender:
        q = q.filter(EmailRow.sender == sender)
    rows = q.order_by(EmailRow.timestamp.desc()).all()
    result = [_row_to_dict(r) for r in rows]
    db.close()
    return result


@app.get("/emails/search")
def search_emails(q: str = Query(...)):
    db = SessionLocal()
    like = f"%{q}%"
    rows = (
        db.query(EmailRow)
        .filter(
            (EmailRow.subject.ilike(like))
            | (EmailRow.body.ilike(like))
            | (EmailRow.sender.ilike(like))
        )
        .order_by(EmailRow.timestamp.desc())
        .all()
    )
    result = [_row_to_dict(r) for r in rows]
    db.close()
    return result


@app.get("/emails/filter")
def filter_emails(
    recipient: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    db = SessionLocal()
    q = db.query(EmailRow)
    if recipient:
        q = q.filter(EmailRow.recipient == recipient)
    if start_date:
        q = q.filter(EmailRow.timestamp >= datetime.fromisoformat(start_date))
    if end_date:
        q = q.filter(EmailRow.timestamp <= datetime.fromisoformat(end_date))
    rows = q.order_by(EmailRow.timestamp.desc()).all()
    result = [_row_to_dict(r) for r in rows]
    db.close()
    return result


@app.get("/emails/{email_id}")
def get_email(email_id: int):
    db = SessionLocal()
    row = db.query(EmailRow).filter(EmailRow.id == email_id).first()
    if not row:
        db.close()
        return {"error": "Email not found"}
    result = _row_to_dict(row)
    db.close()
    return result


@app.patch("/emails/{email_id}/read")
def mark_read(email_id: int):
    db = SessionLocal()
    row = db.query(EmailRow).filter(EmailRow.id == email_id).first()
    if not row:
        db.close()
        return {"error": "Email not found"}
    row.read = True
    db.commit()
    result = _row_to_dict(row)
    db.close()
    return result


@app.patch("/emails/{email_id}/unread")
def mark_unread(email_id: int):
    db = SessionLocal()
    row = db.query(EmailRow).filter(EmailRow.id == email_id).first()
    if not row:
        db.close()
        return {"error": "Email not found"}
    row.read = False
    db.commit()
    result = _row_to_dict(row)
    db.close()
    return result


@app.delete("/emails/{email_id}")
def delete_email(email_id: int):
    db = SessionLocal()
    row = db.query(EmailRow).filter(EmailRow.id == email_id).first()
    if not row:
        db.close()
        return {"error": "Email not found"}
    db.delete(row)
    db.commit()
    db.close()
    return {"status": "deleted", "id": email_id}


@app.get("/reset_database")
def reset_database():
    _reset_db()
    return {"status": "database reset"}
