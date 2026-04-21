from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os

app = FastAPI()

DATA_SERVICE_URL = os.environ.get("DATA_SERVICE_URL", "http://localhost:5002")
PROCESSING_FUNCTION_URL = os.environ.get(
    "PROCESSING_FUNCTION_URL",
    "http://localhost:5004/invoke"
)
RESULT_UPDATE_FUNCTION_URL = os.environ.get(
    "RESULT_UPDATE_FUNCTION_URL",
    "http://localhost:5005/invoke"
)


class SubmissionEvent(BaseModel):
    submission_id: int


@app.get("/health")
def health():
    return {"message": "Submission Event Function is running"}


@app.post("/invoke")
def invoke(event: SubmissionEvent):
    submission_id = event.submission_id

    # 1. 从 Data Service 读取完整记录
    try:
        response = requests.get(
            f"{DATA_SERVICE_URL}/submissions/{submission_id}",
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

    record = response.json()

    # 2. 调用 Processing Function 计算结果
    try:
        process_response = requests.post(
            PROCESSING_FUNCTION_URL,
            json=record,
            timeout=10
        )
    except requests.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to connect to Processing Function: {str(e)}"
        )

    if process_response.status_code != 200:
        raise HTTPException(
            status_code=process_response.status_code,
            detail=f"Processing Function error: {process_response.text}"
        )

    processed_result = process_response.json()

    # 3. 调用 Result Update Function 回写结果
    try:
        update_response = requests.post(
            RESULT_UPDATE_FUNCTION_URL,
            json=processed_result,
            timeout=10
        )
    except requests.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to connect to Result Update Function: {str(e)}"
        )

    if update_response.status_code != 200:
        raise HTTPException(
            status_code=update_response.status_code,
            detail=f"Result Update Function error: {update_response.text}"
        )

    return {
        "message": "Submission event processed successfully",
        "submission_id": submission_id,
        "processing_result": processed_result,
        "update_result": update_response.json()
    }