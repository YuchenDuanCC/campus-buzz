# Campus Buzz Test Results

Generated: 2026-04-21 21:19:25

API Base: `http://8.140.220.43:5001`

Summary: **5/5** test cases passed.

## Test Case 1 - Approved Opportunity

### Input
```json
{
  "title": "Career Workshop for Final Year Students",
  "description": "This workshop helps students prepare CVs and internship applications for summer recruitment events.",
  "location": "Room A101",
  "date": "2026-04-20",
  "organiser": "Career Office"
}
```

### Expected
```json
{
  "status": "APPROVED",
  "category": "OPPORTUNITY",
  "priority": "HIGH"
}
```

### Submit Response
```json
{
  "message": "Submission received and workflow started",
  "submission_id": 2,
  "status": "PENDING"
}
```

### Actual
```json
{
  "id": 2,
  "title": "Career Workshop for Final Year Students",
  "description": "This workshop helps students prepare CVs and internship applications for summer recruitment events.",
  "location": "Room A101",
  "date": "2026-04-20",
  "organiser": "Career Office",
  "status": "APPROVED",
  "category": "OPPORTUNITY",
  "priority": "HIGH",
  "note": "Submission approved. Category: OPPORTUNITY. Priority: HIGH."
}
```

### Result
**Pass**

---

## Test Case 2 - Needs Revision - Invalid Date

### Input
```json
{
  "title": "Seminar on Academic Writing",
  "description": "This seminar gives students practical advice on academic writing and citation skills for coursework.",
  "location": "Library Hall",
  "date": "20-04-2026",
  "organiser": "Writing Centre"
}
```

### Expected
```json
{
  "status": "NEEDS REVISION",
  "category": "ACADEMIC",
  "priority": "MEDIUM"
}
```

### Submit Response
```json
{
  "message": "Submission received and workflow started",
  "submission_id": 3,
  "status": "PENDING"
}
```

### Actual
```json
{
  "id": 3,
  "title": "Seminar on Academic Writing",
  "description": "This seminar gives students practical advice on academic writing and citation skills for coursework.",
  "location": "Library Hall",
  "date": "20-04-2026",
  "organiser": "Writing Centre",
  "status": "NEEDS REVISION",
  "category": "ACADEMIC",
  "priority": "MEDIUM",
  "note": "The date format is invalid. Please use YYYY-MM-DD."
}
```

### Result
**Pass**

---

## Test Case 3 - Needs Revision - Short Description

### Input
```json
{
  "title": "Club Meetup",
  "description": "Join our club.",
  "location": "Student Centre",
  "date": "2026-04-20",
  "organiser": "Music Society"
}
```

### Expected
```json
{
  "status": "NEEDS REVISION",
  "category": "SOCIAL",
  "priority": "NORMAL"
}
```

### Submit Response
```json
{
  "message": "Submission received and workflow started",
  "submission_id": 4,
  "status": "PENDING"
}
```

### Actual
```json
{
  "id": 4,
  "title": "Club Meetup",
  "description": "Join our club.",
  "location": "Student Centre",
  "date": "2026-04-20",
  "organiser": "Music Society",
  "status": "NEEDS REVISION",
  "category": "SOCIAL",
  "priority": "NORMAL",
  "note": "The description is too short. It must be at least 40 characters long."
}
```

### Result
**Pass**

---

## Test Case 4 - Incomplete Submission

### Input
```json
{
  "title": "General Campus Event",
  "description": "This event provides useful information for all students on campus and will include a Q and A session.",
  "location": "",
  "date": "2026-04-20",
  "organiser": "Student Office"
}
```

### Expected
```json
{
  "status": "INCOMPLETE",
  "category": "",
  "priority": ""
}
```

### Submit Response
```json
{
  "message": "Submission received and workflow started",
  "submission_id": 5,
  "status": "PENDING"
}
```

### Actual
```json
{
  "id": 5,
  "title": "General Campus Event",
  "description": "This event provides useful information for all students on campus and will include a Q and A session.",
  "location": "",
  "date": "2026-04-20",
  "organiser": "Student Office",
  "status": "INCOMPLETE",
  "category": "",
  "priority": "",
  "note": "Missing required field(s): location."
}
```

### Result
**Pass**

---

## Test Case 5 - Approved General

### Input
```json
{
  "title": "Campus Notice Board Update",
  "description": "This event shares general campus updates, useful notices, and timetable reminders for all students.",
  "location": "Main Building",
  "date": "2026-04-20",
  "organiser": "Admin Office"
}
```

### Expected
```json
{
  "status": "APPROVED",
  "category": "GENERAL",
  "priority": "NORMAL"
}
```

### Submit Response
```json
{
  "message": "Submission received and workflow started",
  "submission_id": 6,
  "status": "PENDING"
}
```

### Actual
```json
{
  "id": 6,
  "title": "Campus Notice Board Update",
  "description": "This event shares general campus updates, useful notices, and timetable reminders for all students.",
  "location": "Main Building",
  "date": "2026-04-20",
  "organiser": "Admin Office",
  "status": "APPROVED",
  "category": "GENERAL",
  "priority": "NORMAL",
  "note": "Submission approved. Category: GENERAL. Priority: NORMAL."
}
```

### Result
**Pass**

---
