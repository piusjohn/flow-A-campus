import json
import os
import tempfile

VALID_STATUSES = ["open", "in_progress", "resolved", "closed"]
VALID_CATEGORIES = {
    "network": "Network",
    "hardware": "Hardware",
    "software": "Software",
    "other": "Other",
}
PRIORITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def validate_note(note):
    if not isinstance(note, dict):
        raise ValueError("Note must be a dictionary")

    note_id = str(note.get("id", "")).strip()
    if note_id == "":
        raise ValueError("Note ID is required")

    author = str(note.get("author", "")).strip()
    if author == "":
        raise ValueError("Author cannot be empty")

    message = str(note.get("message", "")).strip()
    if message == "":
        raise ValueError("Message cannot be empty")

    normalized = dict(note)
    normalized["id"] = note_id
    normalized["author"] = author
    normalized["message"] = message
    return normalized


def next_note_id(ticket):
    notes = ticket.get("notes", []) or []
    note_numbers = []
    for note in notes:
        if not isinstance(note, dict):
            continue
        note_id = str(note.get("id", "")).strip().upper()
        if note_id.startswith("N") and note_id[1:].isdigit():
            note_numbers.append(int(note_id[1:]))
    next_number = max(note_numbers, default=0) + 1
    return f"N{next_number:03d}"


def calculate_priority(urgency, affected_users):
    urgency = str(urgency).strip().lower()
    if urgency == "high" and affected_users >= 10:
        return "critical"
    if urgency == "high" or affected_users >= 10:
        return "high"
    if urgency == "medium" or affected_users >= 3:
        return "medium"
    return "low"


def validate_ticket_input(title, category, urgency, affected_users):
    title = str(title).strip()
    if title == "":
        raise ValueError("Invalid Input")

    category = str(category).strip().lower()
    if category not in VALID_CATEGORIES:
        raise ValueError("Invalid category")
    category = VALID_CATEGORIES[category]

    urgency = str(urgency).strip().lower()
    if urgency not in ["high", "medium", "low"]:
        raise ValueError("Invalid urgency")

    if isinstance(affected_users, bool):
        raise TypeError("Input an integer number")

    if isinstance(affected_users, float):
        raise ValueError("Decimals not allowed")

    try:
        affected_users = int(affected_users)
    except (TypeError, ValueError):
        raise ValueError("Must be a positive number")

    if affected_users <= 0:
        raise ValueError("Affected users must be greater than zero")

    return title, category, urgency, affected_users


def next_ticket_id(tickets):
    ticket_numbers = []
    for ticket in tickets or []:
        if not isinstance(ticket, dict):
            continue
        ticket_id = str(ticket.get("id", "")).strip().upper()
        if ticket_id.startswith("T") and ticket_id[1:].isdigit():
            ticket_numbers.append(int(ticket_id[1:]))
    next_number = max(ticket_numbers, default=0) + 1
    return f"T{next_number:03d}"


def generate_ticket_id(tickets):
    return next_ticket_id(tickets)


def validate_ticket(ticket):
    if not isinstance(ticket, dict):
        raise ValueError("Ticket must be a dictionary")

    ticket_id = str(ticket.get("id", "")).strip().upper()
    if ticket_id == "":
        raise ValueError("Ticket ID is required")
    if not ticket_id.startswith("T") or not ticket_id[1:].isdigit():
        raise ValueError("Ticket ID must use the T### format")

    title = str(ticket.get("title", "")).strip()
    if title == "":
        raise ValueError("Ticket title cannot be empty")

    category = str(ticket.get("category", "")).strip().lower()
    if category not in VALID_CATEGORIES:
        raise ValueError("Invalid category")
    category = VALID_CATEGORIES[category]

    urgency = str(ticket.get("urgency", "")).strip().lower()
    if urgency not in ["high", "medium", "low"]:
        raise ValueError("Invalid urgency")

    affected_users = ticket.get("affected_users")
    if isinstance(affected_users, bool):
        raise TypeError("Input an integer number")
    if isinstance(affected_users, float):
        raise ValueError("Decimals not allowed")
    try:
        affected_users = int(affected_users)
    except (TypeError, ValueError):
        raise ValueError("Must be a positive number")
    if affected_users <= 0:
        raise ValueError("Affected users must be greater than zero")

    status = str(ticket.get("status", "")).strip().lower()
    if status not in VALID_STATUSES:
        raise ValueError("Invalid status")

    priority = str(ticket.get("priority", "")).strip().lower()
    if priority == "":
        priority = calculate_priority(urgency, affected_users)
    if priority not in PRIORITY_ORDER:
        raise ValueError("Invalid priority")

    assigned_to = ticket.get("assigned_to")
    if assigned_to is not None:
        assigned_to = str(assigned_to).strip() or None

    notes = ticket.get("notes", []) or []
    if not isinstance(notes, list):
        raise ValueError("Notes must be a list")
    normalized_notes = [validate_note(note) for note in notes]

    return {
        "id": ticket_id,
        "title": title,
        "category": category,
        "urgency": urgency,
        "affected_users": affected_users,
        "priority": priority,
        "status": status,
        "assigned_to": assigned_to,
        "notes": normalized_notes,
    }


def can_transition(ticket, new_status):
    if not isinstance(ticket, dict):
        return False
    try:
        normalized_ticket = validate_ticket(ticket)
    except (TypeError, ValueError):
        return False

    next_status = str(new_status).strip().lower()
    if next_status not in VALID_STATUSES:
        return False

    current_status = normalized_ticket["status"]
    if current_status in ("resolved", "closed") and current_status != next_status:
        return False

    if current_status == "open" and next_status == "closed":
        return False
    if current_status == "in_progress" and next_status == "open":
        return False
    if current_status == "open" and next_status == "in_progress" and normalized_ticket.get("assigned_to") in (None, ""):
        return False
    if current_status == "in_progress" and normalized_ticket.get("assigned_to") in (None, "") and next_status != "open":
        return False
    if current_status == "resolved" and next_status == "resolved":
        return True
    if current_status == "closed" and next_status == "closed":
        return True
    return True


def create_ticket(title, category, urgency, affected_users, tickets):
    title, category, urgency, affected_users = validate_ticket_input(title, category, urgency, affected_users)
    ticket_id = next_ticket_id(tickets)
    priority = calculate_priority(urgency, affected_users)
    return {
        "id": ticket_id,
        "title": title,
        "category": category,
        "urgency": urgency,
        "affected_users": affected_users,
        "priority": priority,
        "status": "open",
        "assigned_to": None,
        "notes": [],
    }


def add_ticket(title, category, urgency, affected_users, tickets):
    ticket = create_ticket(title, category, urgency, affected_users, tickets)
    tickets.append(ticket)
    return ticket


def find_ticket(tickets, ticket_id):
    if ticket_id is None:
        raise ValueError("Ticket ID is required")
    ticket_id = str(ticket_id).strip().upper()
    for ticket in tickets:
        if ticket.get("id", "").upper() == ticket_id:
            return ticket
    raise ValueError("Ticket not found")


def assign_ticket(tickets, ticket_id, assignee):
    assignee = str(assignee).strip()
    if assignee == "":
        raise ValueError("Assignee cannot be empty")
    ticket = find_ticket(tickets, ticket_id)
    if ticket.get("status") in ("resolved", "closed"):
        raise ValueError("Cannot modify a resolved or closed ticket")
    ticket["assigned_to"] = assignee
    return ticket


def update_status(tickets, ticket_id, new_status):
    new_status = str(new_status).strip().lower()
    if new_status not in VALID_STATUSES:
        raise ValueError(f"Status must be one of: {', '.join(VALID_STATUSES)}")
    ticket = find_ticket(tickets, ticket_id)
    if ticket.get("status") in ("resolved", "closed"):
        raise ValueError("Cannot mutate a resolved or closed ticket")
    if not can_transition(ticket, new_status):
        raise ValueError("Ticket cannot transition to that status")
    ticket["status"] = new_status
    return ticket


def add_note(*args):
    if len(args) == 3:
        ticket_id, author, message = args
        tickets = None
    elif len(args) == 4:
        tickets, ticket_id, author, message = args
    else:
        raise TypeError("add_note expects ticket_id, author, message or tickets, ticket_id, author, message")

    if tickets is None:
        current = globals().get("_ACTIVE_TICKETS")
        if current is None:
            raise ValueError("Ticket list is required")
        tickets = current

    ticket = find_ticket(tickets, ticket_id)
    if ticket.get("status") in ("resolved", "closed"):
        raise ValueError("Cannot add a note to a resolved or closed ticket")

    author = str(author).strip()
    if author == "":
        raise ValueError("Author cannot be empty")
    message = str(message).strip()
    if message == "":
        raise ValueError("Message cannot be empty")

    note = {"id": next_note_id(ticket), "author": author, "message": message}
    ticket.setdefault("notes", [])
    ticket["notes"].append(validate_note(note))
    return ticket["notes"][-1]


def load_tickets(path=None):
    if path is None:
        path = os.path.join(os.getcwd(), "data", "tickets.json")
    if not os.path.exists(path):
        return []

    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return []

    if payload is None:
        return []
    if isinstance(payload, dict):
        payload = payload.get("tickets", [payload])
    if not isinstance(payload, list):
        return []

    tickets = []
    seen_ids = set()
    for raw_ticket in payload:
        try:
            ticket = validate_ticket(raw_ticket)
        except (TypeError, ValueError):
            continue
        ticket_id = ticket["id"]
        if ticket_id in seen_ids:
            continue
        seen_ids.add(ticket_id)
        tickets.append(ticket)
    return tickets


def save_tickets(path, tickets=None):
    if tickets is None and not isinstance(path, str):
        tickets = path
        path = os.path.join(os.getcwd(), "data", "tickets.json")
    elif tickets is None:
        tickets = []

    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)

    normalized = []
    for ticket in tickets:
        normalized.append(validate_ticket(ticket))

    temp_path = f"{path}.tmp"
    with open(temp_path, "w", encoding="utf-8") as handle:
        json.dump(normalized, handle, indent=2)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp_path, path)
    return normalized


def get_work_queue(tickets):
    active = [ticket for ticket in tickets if ticket["status"] in ("open", "in_progress")]
    return sorted(active, key=lambda ticket: (PRIORITY_ORDER[ticket["priority"]], -ticket["affected_users"]))


def generate_report(tickets):
    report = {"total": len(tickets), "by_status": {}, "by_priority": {}, "by_category": {}, "unassigned": 0}
    for ticket in tickets:
        for key, field in (("by_status", "status"), ("by_priority", "priority"), ("by_category", "category")):
            report[key][ticket[field]] = report[key].get(ticket[field], 0) + 1
        if ticket["assigned_to"] is None:
            report["unassigned"] += 1
    return report