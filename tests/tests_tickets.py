import pytest

from campusflow.tickets import (
    calculate_priority,
    validate_ticket_input,
    generate_ticket_id,
    create_ticket,
    add_ticket,
    find_ticket,
    assign_ticket,
    update_status,
    get_work_queue,
    generate_report,
)


def make_tickets():
    tickets = []
    add_ticket("Wifi down", "network", "high", 20, tickets)
    add_ticket("Broken mouse", "hardware", "low", 1, tickets)
    add_ticket("App crash", "software", "medium", 5, tickets)
    return tickets


# calculate_priority
def test_priority_critical():
    assert calculate_priority("high", 10) == "critical"


def test_priority_high_by_urgency():
    assert calculate_priority("high", 1) == "high"


def test_priority_high_by_users():
    assert calculate_priority("low", 10) == "high"


def test_priority_medium():
    assert calculate_priority("medium", 1) == "medium"
    assert calculate_priority("low", 3) == "medium"


def test_priority_low():
    assert calculate_priority("low", 1) == "low"


# validate_ticket_input
def test_validate_cleans_input():
    result = validate_ticket_input("  Wifi down ", " NETWORK ", " High ", 5)
    assert result == ("Wifi down", "Network", "high", 5)


def test_validate_empty_title():
    with pytest.raises(ValueError):
        validate_ticket_input("   ", "network", "high", 5)


def test_validate_bad_category():
    with pytest.raises(ValueError):
        validate_ticket_input("Title", "food", "high", 5)


def test_validate_bad_urgency():
    with pytest.raises(ValueError):
        validate_ticket_input("Title", "network", "urgent", 5)


def test_validate_bool_users():
    with pytest.raises(TypeError):
        validate_ticket_input("Title", "network", "high", True)


def test_validate_float_users():
    with pytest.raises(ValueError):
        validate_ticket_input("Title", "network", "high", 2.5)


def test_validate_zero_users():
    with pytest.raises(ValueError):
        validate_ticket_input("Title", "network", "high", 0)


def test_validate_text_users():
    with pytest.raises(ValueError):
        validate_ticket_input("Title", "network", "high", "abc")


# generate_ticket_id
def test_id_first_ticket():
    assert generate_ticket_id([]) == "T001"


def test_id_next_ticket():
    assert generate_ticket_id([{"id": "T001"}]) == "T002"
    assert generate_ticket_id([{"id": "T009"}]) == "T010"


# create_ticket and add_ticket
def test_create_ticket_fields():
    ticket = create_ticket("Wifi down", "network", "high", 20, [])
    assert ticket["id"] == "T001"
    assert ticket["priority"] == "critical"
    assert ticket["status"] == "open"
    assert ticket["assigned_to"] is None


def test_add_ticket_appends():
    tickets = []
    add_ticket("Wifi down", "network", "high", 20, tickets)
    assert len(tickets) == 1


def test_add_ticket_invalid_does_not_append():
    tickets = []
    with pytest.raises(ValueError):
        add_ticket("", "network", "high", 20, tickets)
    assert tickets == []


# find_ticket
def test_find_ticket():
    tickets = make_tickets()
    assert find_ticket(tickets, "T002")["title"] == "Broken mouse"


def test_find_ticket_lowercase():
    tickets = make_tickets()
    assert find_ticket(tickets, " t001 ")["id"] == "T001"


def test_find_ticket_missing():
    with pytest.raises(ValueError):
        find_ticket(make_tickets(), "T999")


# assign_ticket
def test_assign_ticket():
    tickets = make_tickets()
    assign_ticket(tickets, "T001", "Sam")
    assert tickets[0]["assigned_to"] == "Sam"


def test_assign_empty_name():
    with pytest.raises(ValueError):
        assign_ticket(make_tickets(), "T001", "  ")


# update_status
def test_update_status():
    tickets = make_tickets()
    update_status(tickets, "T001", "In_Progress")
    assert tickets[0]["status"] == "in_progress"


def test_update_status_invalid():
    with pytest.raises(ValueError):
        update_status(make_tickets(), "T001", "done")


# get_work_queue
def test_work_queue_order():
    queue = get_work_queue(make_tickets())
    ids = [t["id"] for t in queue]
    assert ids == ["T001", "T003", "T002"]


def test_work_queue_skips_closed():
    tickets = make_tickets()
    update_status(tickets, "T001", "closed")
    ids = [t["id"] for t in get_work_queue(tickets)]
    assert "T001" not in ids


# generate_report
def test_report():
    tickets = make_tickets()
    assign_ticket(tickets, "T001", "Sam")
    report = generate_report(tickets)
    assert report["total"] == 3
    assert report["unassigned"] == 2
    assert report["by_status"] == {"open": 3}
    assert report["by_category"]["Network"] == 1