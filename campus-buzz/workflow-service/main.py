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
SUBMISSION_EVENT_URL = os.environ.get(
    "SUBMISSION_EVENT_URL",
    "http://localhost:5003/invoke"
)

class SubmissionCreate(BaseModel):
    title: str = ""
    description: str = ""
    location: str = ""
    date: str = ""
    organiser: str = ""


@app.get("/health")
def health():
    return {"message": "Workflow Service is running"}


@app.post("/submit")
def submit_event(submission: SubmissionCreate):

    try:
        response = requests.post(
            f"{DATA_SERVICE_URL}/submissions",
            json=submission.model_dump(),
            timeout=10
        )
    except requests.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to connect to Data Service: {str(e)}"
        )

    if response.status_code not in (200, 201):
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Data Service error: {response.text}"
        )

    created_record = response.json()
    submission_id = created_record["submission_id"]

    try:
        trigger_response = requests.post(
            SUBMISSION_EVENT_URL,
            json={"submission_id": submission_id},
            timeout=10
        )
    except requests.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to trigger Submission Event Function: {str(e)}"
        )

    if trigger_response.status_code != 200:
        raise HTTPException(
            status_code=trigger_response.status_code,
            detail=f"Submission Event Function error: {trigger_response.text}"
        )


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