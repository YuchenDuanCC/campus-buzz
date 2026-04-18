from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
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

DATA_SERVICE_URL = os.environ.get("DATA_SERVICE_URL", "http://localhost:5002")

class SubmissionCreate(BaseModel):
    title: str
    description: str
    location: str
    date: str
    organiser: str


@app.get("/health")
def health():
    return {"message": "Workflow Service is running"}


@app.post("/submit")
def submit_event(submission: SubmissionCreate):
    try:
        response = requests.post(
            f"{DATA_SERVICE_URL}/submissions",
            json=submission.dict()
        )
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect to Data Service: {str(e)}")

    if response.status_code != 200 and response.status_code != 201:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Data Service error: {response.text}"
        )

    created_record = response.json()
    submission_id = created_record["submission_id"]

    # 这里先只是模拟“触发后台处理”
    print(f"Background processing triggered for submission {submission_id}")

    return {
        "message": "Submission received and workflow started",
        "submission_id": submission_id,
        "status": created_record.get("status", "PENDING")
    }


@app.get("/result/{submission_id}")
def get_result(submission_id: int):
    try:
        response = requests.get(f"{DATA_SERVICE_URL}/submissions/{submission_id}")
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect to Data Service: {str(e)}")

    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Submission not found")

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Data Service error: {response.text}"
        )

    return response.json()