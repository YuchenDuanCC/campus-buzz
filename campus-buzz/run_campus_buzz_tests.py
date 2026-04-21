import json
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict, List

try:
    import requests
except ImportError:
    print("This script requires the 'requests' package. Install it with: pip install requests")
    sys.exit(1)

API_BASE = os.environ.get("API_BASE", "http://localhost:5001")
OUTPUT_FILE = os.environ.get("OUTPUT_FILE", "test-results.md")
POLL_SECONDS = float(os.environ.get("POLL_SECONDS", "0.5"))
POLL_TIMEOUT = float(os.environ.get("POLL_TIMEOUT", "10"))

TEST_CASES: List[Dict[str, Any]] = [
    {
        "name": "Approved Opportunity",
        "input": {
            "title": "Career Workshop for Final Year Students",
            "description": "This workshop helps students prepare CVs and internship applications for summer recruitment events.",
            "location": "Room A101",
            "date": "2026-04-20",
            "organiser": "Career Office"
        },
        "expected": {
            "status": "APPROVED",
            "category": "OPPORTUNITY",
            "priority": "HIGH"
        }
    },
    {
        "name": "Needs Revision - Invalid Date",
        "input": {
            "title": "Seminar on Academic Writing",
            "description": "This seminar gives students practical advice on academic writing and citation skills for coursework.",
            "location": "Library Hall",
            "date": "20-04-2026",
            "organiser": "Writing Centre"
        },
        "expected": {
            "status": "NEEDS REVISION",
            "category": "ACADEMIC",
            "priority": "MEDIUM"
        }
    },
    {
        "name": "Needs Revision - Short Description",
        "input": {
            "title": "Club Meetup",
            "description": "Join our club.",
            "location": "Student Centre",
            "date": "2026-04-20",
            "organiser": "Music Society"
        },
        "expected": {
            "status": "NEEDS REVISION",
            "category": "SOCIAL",
            "priority": "NORMAL"
        }
    },
    {
        "name": "Incomplete Submission",
        "input": {
            "title": "General Campus Event",
            "description": "This event provides useful information for all students on campus and will include a Q and A session.",
            "location": "",
            "date": "2026-04-20",
            "organiser": "Student Office"
        },
        "expected": {
            "status": "INCOMPLETE",
            "category": "",
            "priority": ""
        }
    },
    {
        "name": "Approved General",
        "input": {
            "title": "Campus Notice Board Update",
            "description": "This event shares general campus updates, useful notices, and timetable reminders for all students.",
            "location": "Main Building",
            "date": "2026-04-20",
            "organiser": "Admin Office"
        },
        "expected": {
            "status": "APPROVED",
            "category": "GENERAL",
            "priority": "NORMAL"
        }
    }
]


def pretty_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)



def submit_case(payload: Dict[str, Any]) -> Dict[str, Any]:
    response = requests.post(f"{API_BASE}/submit", json=payload, timeout=15)
    response.raise_for_status()
    return response.json()



def fetch_result(submission_id: int) -> Dict[str, Any]:
    response = requests.get(f"{API_BASE}/result/{submission_id}", timeout=15)
    response.raise_for_status()
    return response.json()



def wait_for_final_result(submission_id: int) -> Dict[str, Any]:
    start = time.time()
    last = None
    while time.time() - start < POLL_TIMEOUT:
        last = fetch_result(submission_id)
        if last.get("status") != "PENDING":
            return last
        time.sleep(POLL_SECONDS)
    return last or {}



def compare_expected(expected: Dict[str, Any], actual: Dict[str, Any]) -> List[str]:
    mismatches = []
    for key, expected_value in expected.items():
        actual_value = actual.get(key, None)
        if actual_value != expected_value:
            mismatches.append(f"{key}: expected {expected_value!r}, got {actual_value!r}")
    return mismatches



def run_one(index: int, case: Dict[str, Any]) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "index": index,
        "name": case["name"],
        "input": case["input"],
        "expected": case["expected"],
        "submitted": None,
        "actual": None,
        "pass": False,
        "errors": [],
    }

    try:
        submitted = submit_case(case["input"])
        result["submitted"] = submitted
        submission_id = submitted.get("submission_id")
        if not submission_id:
            result["errors"].append("submit response did not include submission_id")
            return result

        actual = wait_for_final_result(submission_id)
        result["actual"] = actual
        mismatches = compare_expected(case["expected"], actual)
        if mismatches:
            result["errors"].extend(mismatches)
        else:
            result["pass"] = True
        return result
    except requests.RequestException as exc:
        result["errors"].append(f"HTTP error: {exc}")
        return result
    except Exception as exc:  # noqa: BLE001
        result["errors"].append(f"Unexpected error: {exc}")
        return result



def write_markdown(results: List[Dict[str, Any]], path: str) -> None:
    passed = sum(1 for r in results if r["pass"])
    total = len(results)
    lines: List[str] = []
    lines.append("# Campus Buzz Test Results")
    lines.append("")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append(f"API Base: `{API_BASE}`")
    lines.append("")
    lines.append(f"Summary: **{passed}/{total}** test cases passed.")
    lines.append("")

    for r in results:
        lines.append(f"## Test Case {r['index']} - {r['name']}")
        lines.append("")
        lines.append("### Input")
        lines.append("```json")
        lines.append(pretty_json(r["input"]))
        lines.append("```")
        lines.append("")
        lines.append("### Expected")
        lines.append("```json")
        lines.append(pretty_json(r["expected"]))
        lines.append("```")
        lines.append("")
        lines.append("### Submit Response")
        lines.append("```json")
        lines.append(pretty_json(r["submitted"]))
        lines.append("```")
        lines.append("")
        lines.append("### Actual")
        lines.append("```json")
        lines.append(pretty_json(r["actual"]))
        lines.append("```")
        lines.append("")
        lines.append("### Result")
        if r["pass"]:
            lines.append("**Pass**")
        else:
            lines.append("**Fail**")
            if r["errors"]:
                lines.append("")
                lines.append("### Errors")
                for err in r["errors"]:
                    lines.append(f"- {err}")
        lines.append("")
        lines.append("---")
        lines.append("")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))



def main() -> int:
    print(f"Running tests against {API_BASE}")
    results = []
    for idx, case in enumerate(TEST_CASES, start=1):
        print(f"- Running test {idx}: {case['name']}")
        results.append(run_one(idx, case))

    write_markdown(results, OUTPUT_FILE)
    passed = sum(1 for r in results if r["pass"])
    total = len(results)
    print(f"Done. {passed}/{total} passed.")
    print(f"Markdown report written to: {os.path.abspath(OUTPUT_FILE)}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
