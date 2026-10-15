import unittest

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


if __name__ == "__main__":
    unittest.main()