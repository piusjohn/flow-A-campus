
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

