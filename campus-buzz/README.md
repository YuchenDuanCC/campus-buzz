# Campus Buzz

Campus Buzz is a small hybrid cloud application for campus event submission and automated background validation. It was developed for **COMP3041J Mini-Project 1: Cloud Execution Models (Containers and Serverless)**.

The system allows a user to submit a campus event by entering:

- event title
- description
- location
- date
- organiser name

After submission, the system stores the record, triggers background processing, applies the required validation and classification rules, updates the result, and lets the user view the final outcome.

## Project Goal

This project demonstrates how a single application can combine:

- **3 container-based services**
- **3 serverless functions**

The design follows the required workflow:

**user submits input → workflow creates record → event function starts processing → processing function produces outcome → result function updates system → user views result**

---

## Architecture

### Container Services (Alibaba Cloud ECS)

1. **Presentation Service**
   - Serves the frontend page
   - Accepts user input
   - Displays final results

2. **Workflow Service**
   - Receives submissions
   - Creates the initial submission record
   - Starts the background processing workflow

3. **Data Service**
   - Stores and retrieves submission records
   - Uses SQLite for lightweight persistence

### Serverless Functions (Alibaba Cloud Function Compute)

4. **Submission Event Function**
   - Turns a new submission event into a processing request

5. **Processing Function**
   - Applies the project rules
   - Computes status, category, priority, and note

6. **Result Update Function**
   - Updates the stored record with the computed result

### Supporting Cloud Service

- **Alibaba Cloud Container Registry (ACR)**
  - Stores the container images for the three serverless functions deployed on Function Compute

---

## Functional Rules

The processing logic follows the project specification exactly.

### Final Status

- **INCOMPLETE**
  - returned if any required field is missing

- **NEEDS REVISION**
  - returned if the date format is invalid
  - or if the description is shorter than 40 characters

- **APPROVED**
  - returned only if all required checks pass

### Category Assignment

Keyword matching is applied to the title and description with this order of precedence:

1. **OPPORTUNITY**
   - keywords: `career`, `internship`, `recruitment`

2. **ACADEMIC**
   - keywords: `workshop`, `seminar`, `lecture`

3. **SOCIAL**
   - keywords: `club`, `society`, `social`

4. **GENERAL**
   - if none of the above apply

### Priority Assignment

- **HIGH** for `OPPORTUNITY`
- **MEDIUM** for `ACADEMIC`
- **NORMAL** for `SOCIAL` or `GENERAL`

---

## Tech Stack

- **Frontend:** HTML, CSS, JavaScript, Nginx
- **Backend services:** FastAPI
- **Database:** SQLite
- **Containers:** Docker, Docker Compose
- **Cloud platform:** Alibaba Cloud
  - ECS
  - Function Compute
  - ACR

---

## Repository Structure

```text
campus-buzz/
├── presentation-service/
│   ├── Dockerfile
│   ├── index.html
│   └── nginx.conf
├── workflow-service/
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── data-service/
│   ├── Dockerfile
│   ├── main.py
│   ├── requirements.txt
│   └── submissions.db
├── submission-event-function/
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── processing-function/
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── result-update-function/
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── docker-compose.yml
├── docker-compose.ecs.yml
└── README.md
```

---

## Local Deployment

### Prerequisites

- Docker Desktop or Docker Engine
- Docker Compose
- Python 3.x (for running the automated test script, if needed)

### Run Locally

```bash
docker compose up --build
```

Typical local access points:

- Frontend: `http://localhost:8081`
- Workflow Service: `http://localhost:5001`
- Data Service: `http://localhost:5002`

### Local Test Script

A Python test script can be used to verify the required cases:

- Approved Opportunity
- Needs Revision - Invalid Date
- Needs Revision - Short Description
- Incomplete Submission
- Approved General

Example:

```bash
python run_campus_buzz_tests.py
```

---

## Alibaba Cloud Deployment

### ECS
The following services are deployed on Alibaba Cloud ECS:

- presentation-service
- workflow-service
- data-service

### Function Compute
The following functions are deployed on Alibaba Cloud Function Compute:

- submission-event-function
- processing-function
- result-update-function

### ACR
The three serverless functions are packaged as container images and pushed to Alibaba Cloud Container Registry before being deployed to Function Compute.

---

## Testing Summary

The system was validated in both local and cloud environments.

The following representative cases were tested successfully:

| Test Case | Expected Status | Expected Category | Expected Priority |
|---|---|---|---|
| Approved Opportunity | APPROVED | OPPORTUNITY | HIGH |
| Invalid Date | NEEDS REVISION | ACADEMIC | MEDIUM |
| Short Description | NEEDS REVISION | SOCIAL | NORMAL |
| Incomplete Submission | INCOMPLETE | — | — |
| Approved General | APPROVED | GENERAL | NORMAL |

Both local and cloud-based automated testing passed all 5 cases.

---

## Screenshots and Evidence

Recommended evidence for demonstration or report writing:

- system architecture diagram
- frontend submission page
- frontend result page
- local test results
- cloud test results
- ECS build and runtime screenshots
- Function Compute deployment screenshots

---

## Notes

- This project keeps the frontend intentionally simple in order to focus on **service decomposition**, **execution-model choice**, **event-driven workflow**, and **integration between containers and serverless functions**.
- ACR is used as a supporting deployment component and is **not counted** as one of the six required application components.

---

## Group Information

- **Group ID:** Group 11
- **Module:** COMP3041J Mini-Project 1

---

## License

This repository was created for academic coursework demonstration and submission.
