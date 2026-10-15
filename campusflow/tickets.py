
def calculate_priority(urgency, affected_users):
    urgency = urgency.lower()
    if urgency == "high" and affected_users >= 10:
        return "critical"
    elif urgency == "high" or affected_users >= 10:
        return "high"
    elif urgency == "medium" or affected_users >= 3:
        return "medium"
    else:
        return "low"
    

def validate_ticket_input(title, category, urgency, affected_users):
    title = title.strip()
    if title == "":
        raise ValueError("Invalid Input")
    
    allowed_category = {
        "network": "Network",
        "hardware": "Hardware",
        "software": "Software",
        "other": "Other"
    }
    category = category.strip().lower()
    if category not in allowed_category:
        raise ValueError("Invalid category")
    category = allowed_category[category]
    
    urgency = urgency.strip().lower()
    if urgency not in ["high", "medium", "low"]:
        raise ValueError("Invalid urgency")
    
    if isinstance(affected_users, bool):
        raise TypeError("Input an integer number") 
    
    if isinstance(affected_users, float):
        raise ValueError("Decimals not allowed")
    
    try:
        affected_users = int(affected_users)
    except (ValueError, TypeError):
        raise ValueError("Must be a positive number")
    
    if affected_users <= 0:
        raise ValueError("Affected users must be greater than zero")
    
    return  title, category, urgency, affected_users

def generate_ticket_id(tickets):
    if tickets == []:
        return "T001"
    tickets_id = tickets[-1]["id"]
    number = tickets_id.replace("T", "")
    converted_number = int(number)
    increment_id = converted_number + 1
    result = f"T{increment_id:03d}"

    return result

def create_ticket(title, category, urgency, affected_users, tickets):
    title, category, urgency, affected_users = validate_ticket_input(title,category,urgency,affected_users)
    ticket_id = generate_ticket_id(tickets)
    priority = calculate_priority(urgency, affected_users)
    status = "open"
    assisged_to = None

    ticket = {
    "id": ticket_id,
    "title": title,
    "category": category,
    "urgency": urgency,
    "affected_users": affected_users,
    "priority": priority,
    "status": status,
    "assigned_to": assisged_to
    }

    return ticket

def add_ticket(title,category,urgency,affected_users,tickets):
        ticket = create_ticket(title,category,urgency,affected_users,tickets)
        tickets.append(ticket)
        return ticket

VALID_STATUSES = ["open", "in_progress", "resolved", "closed"]
PRIORITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def find_ticket(tickets, ticket_id):
    ticket_id = ticket_id.strip().upper()
    for t in tickets:
        if t["id"] == ticket_id:
            return t
    raise ValueError("Ticket not found")


def assign_ticket(tickets, ticket_id, assignee):
    assignee = assignee.strip()
    if assignee == "":
        raise ValueError("Assignee cannot be empty")
    ticket = find_ticket(tickets, ticket_id)
    ticket["assigned_to"] = assignee
    return ticket


def update_status(tickets, ticket_id, new_status):
    new_status = new_status.strip().lower()
    if new_status not in VALID_STATUSES:
        raise ValueError(f"Status must be one of: {', '.join(VALID_STATUSES)}")
    ticket = find_ticket(tickets, ticket_id)
    ticket["status"] = new_status
    return ticket


def get_work_queue(tickets):
    active = [t for t in tickets if t["status"] in ("open", "in_progress")]
    return sorted(active, key=lambda t: (PRIORITY_ORDER[t["priority"]], -t["affected_users"]))


def generate_report(tickets):
    report = {"total": len(tickets), "by_status": {}, "by_priority": {}, "by_category": {}, "unassigned": 0}
    for t in tickets:
        for key, field in (("by_status", "status"), ("by_priority", "priority"), ("by_category", "category")):
            report[key][t[field]] = report[key].get(t[field], 0) + 1
        if t["assigned_to"] is None:
            report["unassigned"] += 1
    return report