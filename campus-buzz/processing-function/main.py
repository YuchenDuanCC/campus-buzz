from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()


class SubmissionRecord(BaseModel):
    id: int
    title: str = ""
    description: str = ""
    location: str = ""
    date: str = ""
    organiser: str = ""
    status: str = ""
    category: str = ""
    priority: str = ""
    note: str = ""


def is_missing(value: str) -> bool:
    return value is None or str(value).strip() == ""


def is_valid_date_format(date_str: str) -> bool:
    try:
        parsed = datetime.strptime(date_str, "%Y-%m-%d")
        return parsed.strftime("%Y-%m-%d") == date_str
    except ValueError:
        return False


def assign_category(title: str, description: str) -> str:
    text = f"{title} {description}".lower()

    if any(keyword in text for keyword in ["career", "internship", "recruitment"]):
        return "OPPORTUNITY"
    if any(keyword in text for keyword in ["workshop", "seminar", "lecture"]):
        return "ACADEMIC"
    if any(keyword in text for keyword in ["club", "society", "social"]):
        return "SOCIAL"
    return "GENERAL"


def assign_priority(category: str) -> str:
    if category == "OPPORTUNITY":
        return "HIGH"
    if category == "ACADEMIC":
        return "MEDIUM"
    return "NORMAL"


@app.get("/health")
def health():
    return {"message": "Processing Function is running"}


@app.post("/invoke")
def invoke(record: SubmissionRecord):
    required_fields = {
        "title": record.title,
        "description": record.description,
        "location": record.location,
        "date": record.date,
        "organiser": record.organiser,
    }

    missing = [field for field, value in required_fields.items() if is_missing(value)]
    if missing:
        return {
            "submission_id": record.id,
            "status": "INCOMPLETE",
            "category": "",
            "priority": "",
            "note": f"Missing required field(s): {', '.join(missing)}."
        }

    category = assign_category(record.title, record.description)
    priority = assign_priority(category)

    if not is_valid_date_format(record.date):
        return {
            "submission_id": record.id,
            "status": "NEEDS REVISION",
            "category": category,
            "priority": priority,
            "note": "The date format is invalid. Please use YYYY-MM-DD."
        }


    if len(record.description.strip()) < 40:
        return {
            "submission_id": record.id,
            "status": "NEEDS REVISION",
            "category": category,
            "priority": priority,
            "note": "The description is too short. It must be at least 40 characters long."
        }


    return {
        "submission_id": record.id,
        "status": "APPROVED",
        "category": category,
        "priority": priority,
        "note": f"Submission approved. Category: {category}. Priority: {priority}."
    }