from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os

app = FastAPI()

DATA_SERVICE_URL = os.environ.get("DATA_SERVICE_URL", "http://localhost:5002")


class ProcessingResult(BaseModel):
    submission_id: int
    status: str
    category: str = ""
    priority: str = ""
    note: str = ""


@app.get("/health")
def health():
    return {"message": "Result Update Function is running"}


@app.post("/invoke")
def invoke(result: ProcessingResult):
    payload = {
        "status": result.status,
        "category": result.category,
        "priority": result.priority,
        "note": result.note
    }

    try:
        response = requests.put(
            f"{DATA_SERVICE_URL}/submissions/{result.submission_id}",
            json=payload,
            timeout=10
        )
    except requests.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to connect to Data Service: {str(e)}"
        )

    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Submission not found")

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Data Service error: {response.text}"
        )

    return {
        "message": "Submission updated successfully",
        "submission_id": result.submission_id,
        "updated": response.json()
    }