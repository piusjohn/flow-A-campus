import json
import os
import tempfile
import unittest

import main
from campusflow.tickets import (
    add_note,
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
    load_tickets,
    next_note_id,
    next_ticket_id,
    save_tickets,
)


class TestTickets(unittest.TestCase):

    def setUp(self):
        # runs before every test, so each test gets fresh tickets
        self.tickets = []
        add_ticket("Wifi down", "network", "high", 20, self.tickets)
        add_ticket("Broken mouse", "hardware", "low", 1, self.tickets)
        add_ticket("App crash", "software", "medium", 5, self.tickets)

    # calculate_priority
    def test_priority_critical(self):
        self.assertEqual(calculate_priority("high", 10), "critical")

    def test_priority_high_by_urgency(self):
        self.assertEqual(calculate_priority("high", 1), "high")

    def test_priority_high_by_users(self):
        self.assertEqual(calculate_priority("low", 10), "high")

    def test_priority_medium(self):
        self.assertEqual(calculate_priority("medium", 1), "medium")
        self.assertEqual(calculate_priority("low", 3), "medium")

    def test_priority_low(self):
        self.assertEqual(calculate_priority("low", 1), "low")

    # validate_ticket_input
    def test_validate_cleans_input(self):
        result = validate_ticket_input("  Wifi down ", " NETWORK ", " High ", 5)
        self.assertEqual(result, ("Wifi down", "Network", "high", 5))

    def test_validate_empty_title(self):
        with self.assertRaises(ValueError):
            validate_ticket_input("   ", "network", "high", 5)

    def test_validate_bad_category(self):
        with self.assertRaises(ValueError):
            validate_ticket_input("Title", "food", "high", 5)

    def test_validate_bad_urgency(self):
        with self.assertRaises(ValueError):
            validate_ticket_input("Title", "network", "urgent", 5)

    def test_validate_bool_users(self):
        with self.assertRaises(TypeError):
            validate_ticket_input("Title", "network", "high", True)

    def test_validate_float_users(self):
        with self.assertRaises(ValueError):
            validate_ticket_input("Title", "network", "high", 2.5)

    def test_validate_zero_users(self):
        with self.assertRaises(ValueError):
            validate_ticket_input("Title", "network", "high", 0)

    def test_validate_text_users(self):
        with self.assertRaises(ValueError):
            validate_ticket_input("Title", "network", "high", "abc")

    # generate_ticket_id
    def test_id_first_ticket(self):
        self.assertEqual(generate_ticket_id([]), "T001")

    def test_id_next_ticket(self):
        self.assertEqual(generate_ticket_id([{"id": "T001"}]), "T002")
        self.assertEqual(generate_ticket_id([{"id": "T009"}]), "T010")

    # create_ticket and add_ticket
    def test_create_ticket_fields(self):
        ticket = create_ticket("Wifi down", "network", "high", 20, [])
        self.assertEqual(ticket["id"], "T001")
        self.assertEqual(ticket["priority"], "critical")
        self.assertEqual(ticket["status"], "open")
        self.assertIsNone(ticket["assigned_to"])

    def test_add_ticket_appends(self):
        self.assertEqual(len(self.tickets), 3)

    def test_add_ticket_invalid_does_not_append(self):
        with self.assertRaises(ValueError):
            add_ticket("", "network", "high", 20, self.tickets)
        self.assertEqual(len(self.tickets), 3)

    # find_ticket
    def test_find_ticket(self):
        self.assertEqual(find_ticket(self.tickets, "T002")["title"], "Broken mouse")

    def test_find_ticket_lowercase(self):
        self.assertEqual(find_ticket(self.tickets, " t001 ")["id"], "T001")

    def test_find_ticket_missing(self):
        with self.assertRaises(ValueError):
            find_ticket(self.tickets, "T999")

    # assign_ticket
    def test_assign_ticket(self):
        assign_ticket(self.tickets, "T001", "Sam")
        self.assertEqual(self.tickets[0]["assigned_to"], "Sam")

    def test_assign_empty_name(self):
        with self.assertRaises(ValueError):
            assign_ticket(self.tickets, "T001", "  ")

    # update_status
    def test_update_status(self):
        assign_ticket(self.tickets, "T001", "Sam")
        update_status(self.tickets, "T001", "In_Progress")
        self.assertEqual(self.tickets[0]["status"], "in_progress")

    def test_update_status_invalid(self):
        with self.assertRaises(ValueError):
            update_status(self.tickets, "T001", "done")

    # get_work_queue
    def test_work_queue_order(self):
        ids = [t["id"] for t in get_work_queue(self.tickets)]
        self.assertEqual(ids, ["T001", "T003", "T002"])

    def test_work_queue_skips_closed(self):
        assign_ticket(self.tickets, "T001", "Sam")
        update_status(self.tickets, "T001", "in_progress")
        update_status(self.tickets, "T001", "closed")
        ids = [t["id"] for t in get_work_queue(self.tickets)]
        self.assertNotIn("T001", ids)

    # generate_report
    def test_report(self):
        assign_ticket(self.tickets, "T001", "Sam")
        report = generate_report(self.tickets)
        self.assertEqual(report["total"], 3)
        self.assertEqual(report["unassigned"], 2)
        self.assertEqual(report["by_status"], {"open": 3})
        self.assertEqual(report["by_category"]["Network"], 1)




class TestTicketStorageSafety(unittest.TestCase):

    def test_load_tickets_missing_file_returns_empty_list(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            data_path = os.path.join(tmpdir, "tickets.json")
            original = main.DATA_FILE
            main.DATA_FILE = data_path
            try:
                self.assertEqual(main.load_tickets(), [])
            finally:
                main.DATA_FILE = original

    def test_load_tickets_invalid_json_returns_empty_list(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            data_path = os.path.join(tmpdir, "tickets.json")
            with open(data_path, "w", encoding="utf-8") as f:
                f.write("{not-valid-json")

            original = main.DATA_FILE
            main.DATA_FILE = data_path
            try:
                self.assertEqual(main.load_tickets(), [])
            finally:
                main.DATA_FILE = original

    def test_save_tickets_creates_parent_directory_and_writes_valid_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            data_path = os.path.join(tmpdir, "nested", "tickets.json")
            original = main.DATA_FILE
            main.DATA_FILE = data_path
            try:
                ticket = {
                    "id": "T001",
                    "title": "Demo",
                    "category": "Network",
                    "urgency": "high",
                    "affected_users": 2,
                    "priority": "high",
                    "status": "open",
                    "assigned_to": None,
                    "notes": [],
                }
                main.save_tickets([ticket])
                with open(data_path, "r", encoding="utf-8") as f:
                    self.assertEqual(json.load(f), [ticket])
            finally:
                main.DATA_FILE = original

    def test_unassigned_ticket_cannot_progress(self):
        tickets = [create_ticket("Wifi down", "network", "high", 20, [])]
        with self.assertRaises(ValueError):
            update_status(tickets, "T001", "in_progress")
        self.assertEqual(tickets[0]["status"], "open")

    def test_resolved_ticket_mutation_rejected(self):
        tickets = [create_ticket("Wifi down", "network", "high", 20, [])]
        update_status(tickets, "T001", "resolved")
        with self.assertRaises(ValueError):
            assign_ticket(tickets, "T001", "Sam")
        with self.assertRaises(ValueError):
            update_status(tickets, "T001", "closed")
        self.assertEqual(tickets[0]["status"], "resolved")

    def test_note_can_be_added_to_open_ticket_only(self):
        tickets = [create_ticket("Wifi down", "network", "high", 20, [])]
        note = add_note(tickets, "T001", "Sam", "Investigating")
        self.assertEqual(note["message"], "Investigating")
        self.assertEqual(len(tickets[0]["notes"]), 1)

        update_status(tickets, "T001", "resolved")
        with self.assertRaises(ValueError):
            add_note(tickets, "T001", "Dana", "Should not be allowed")
        self.assertEqual(len(tickets[0]["notes"]), 1)

    def test_load_tickets_ignores_corrupted_or_duplicate_ids(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            data_path = os.path.join(tmpdir, "tickets.json")
            payload = [
                {"id": "T001", "title": "Good", "category": "Network", "urgency": "high", "affected_users": 2, "priority": "high", "status": "open", "assigned_to": None, "notes": []},
                {"id": "T001", "title": "Duplicate", "category": "Network", "urgency": "low", "affected_users": 1, "priority": "low", "status": "open", "assigned_to": None, "notes": []},
                {"id": "bad", "title": "Broken", "category": "Network", "urgency": "low", "affected_users": 1, "priority": "low", "status": "open", "assigned_to": None, "notes": []},
                {"title": "Missing id", "category": "Network", "urgency": "low", "affected_users": 1, "priority": "low", "status": "open", "assigned_to": None, "notes": []},
            ]
            with open(data_path, "w", encoding="utf-8") as f:
                json.dump(payload, f)

            tickets = load_tickets(data_path)
            self.assertEqual(len(tickets), 1)
            self.assertEqual(tickets[0]["id"], "T001")
            self.assertEqual(next_ticket_id(tickets), "T002")

    def test_next_ticket_and_note_ids_continue_after_reload(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            data_path = os.path.join(tmpdir, "tickets.json")
            tickets = [
                {"id": "T001", "title": "One", "category": "Network", "urgency": "low", "affected_users": 1, "priority": "low", "status": "open", "assigned_to": None, "notes": [{"id": "N001", "author": "A", "message": "Hello"}]},
                {"id": "T003", "title": "Two", "category": "Software", "urgency": "medium", "affected_users": 2, "priority": "medium", "status": "open", "assigned_to": None, "notes": [{"id": "N002", "author": "B", "message": "Hi"}]},
            ]
            save_tickets(data_path, tickets)
            reloaded = load_tickets(data_path)
            self.assertEqual(next_ticket_id(reloaded), "T004")
            self.assertEqual(next_note_id(reloaded[1]), "N003")


if __name__ == "__main__":
    unittest.main()