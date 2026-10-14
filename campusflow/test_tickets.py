
import unittest

from tickets import (
    calculate_priority,
    validate_ticket_input,
    generate_ticket_id,
    create_ticket,
    add_ticket,
)


class TestCampusFlow(unittest.TestCase):

    # 1. Test priority calculation
    def test_critical_priority(self):
        self.assertEqual(calculate_priority("high", 15), "critical")

    def test_high_priority(self):
        self.assertEqual(calculate_priority("high", 2), "high")

    def test_medium_priority(self):
        self.assertEqual(calculate_priority("medium", 2), "medium")

    def test_low_priority(self):
        self.assertEqual(calculate_priority("low", 1), "low")

    # 2. Test input validation
    def test_valid_ticket_input(self):
        result = validate_ticket_input(
            "Wi-Fi is down", "network", "high", 15
        )

        self.assertEqual(
            result, ("Wi-Fi is down", "Network", "high", 15)
        )

    def test_blank_title_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_ticket_input("   ", "Network", "high", 5)

    def test_invalid_category_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_ticket_input(
                "Wi-Fi is down", "Furniture", "high", 5
            )

    def test_invalid_urgency_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_ticket_input(
                "Wi-Fi is down", "Network", "urgent", 5
            )

    def test_zero_affected_users_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_ticket_input(
                "Wi-Fi is down", "Network", "high", 0
            )

    # 3. Test ticket ID generation
    def test_first_ticket_id(self):
        self.assertEqual(generate_ticket_id([]), "T001")

    def test_next_ticket_id(self):
        tickets = [{"id": "T001"}]

        self.assertEqual(generate_ticket_id(tickets), "T002")

    # 4. Test ticket creation
    def test_create_ticket(self):
        ticket = create_ticket(
            "Wi-Fi is down", "network", "high", 15, []
        )

        self.assertEqual(ticket["id"], "T001")
        self.assertEqual(ticket["category"], "Network")
        self.assertEqual(ticket["priority"], "critical")
        self.assertEqual(ticket["status"], "open")
        self.assertIsNone(ticket["assigned_to"])

    # 5. Test adding tickets
    def test_add_ticket_to_list(self):
        tickets = []

        add_ticket("Wi-Fi is down", "Network", "high", 15, tickets)

        self.assertEqual(len(tickets), 1)
        self.assertEqual(tickets[0]["id"], "T001")

    def test_two_tickets_have_different_ids(self):
        tickets = []

        add_ticket("Wi-Fi is down", "Network", "high", 15, tickets)
        add_ticket("Laptop is faulty", "Hardware", "medium", 2, tickets)

        self.assertEqual(len(tickets), 2)
        self.assertEqual(tickets[0]["id"], "T001")
        self.assertEqual(tickets[1]["id"], "T002")


if __name__ == "__main__":
    unittest.main()