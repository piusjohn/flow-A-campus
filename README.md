# Flow-A-Campus

Flow-A-Campus is a small command-line ticket tracker for campus IT support. Use it to record issues, assign them to staff, track their status, and review a prioritized work queue or summary report. Ticket data is stored locally in a JSON file.

## Requirements

- Python 3
- No third-party packages

## Run

From the project directory, start the interactive menu with:

```bash
python3 main.py
```

CampusFlow loads tickets from `data/tickets.json` when it starts. The repository includes a sample ticket. If the file is missing, the application starts with an empty ticket list. Changes made through the menu are saved to that file.

## What You Can Do

The menu lets you:

- Create a ticket with a title, category, urgency, and number of affected users
- List all tickets or view one ticket's details
- Assign a ticket to a staff member
- Change a ticket's status
- View the active work queue
- Generate totals grouped by status, priority, and category, including the number of unassigned tickets

Categories are `network`, `hardware`, `software`, and `other`. Urgency is `high`, `medium`, or `low`. Status is `open`, `in_progress`, `resolved`, or `closed`.

### Priority Rules

Priority is calculated when a ticket is created:

| Priority | Rule |
| --- | --- |
| Critical | High urgency and at least 10 affected users |
| High | High urgency, or at least 10 affected users |
| Medium | Medium urgency, or at least 3 affected users |
| Low | Otherwise |

The work queue includes tickets with `open` or `in_progress` status. It orders them by priority (critical first), then by affected-user count (largest first).

## Run Tests

Run the unit tests from the project directory:

```bash
python3 -m unittest discover -v
```

## Project Layout

```text
.
├── campusflow/
│   └── tickets.py       # Ticket validation, priority, queue, and report logic
├── data/
│   └── tickets.json     # Local ticket storage
├── tests/
│   └── test_tickets.py  # Unit tests
└── main.py              # Interactive command-line application
```
