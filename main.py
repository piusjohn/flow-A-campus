import os

from campusflow.tickets import (
    add_note,
    add_ticket,
    assign_ticket,
    find_ticket,
    generate_report,
    get_work_queue,
    load_tickets as _load_tickets,
    save_tickets as _save_tickets,
    update_status,
)

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "tickets.json")


def load_tickets():
    tickets = _load_tickets(DATA_FILE)
    print(f"Loaded {len(tickets)} ticket(s) from {DATA_FILE}")
    return tickets


def save_tickets(tickets):
    return _save_tickets(DATA_FILE, tickets)


def show_menu():
    print("\n=== CampusFlow ===")
    print("1. Create ticket")
    print("2. List all tickets")
    print("3. View ticket details")
    print("4. Assign ticket")
    print("5. Update ticket status")
    print("6. Work queue")
    print("7. Reports")
    print("8. Exit")


def create_ticket_menu(tickets):
    title = input("Title: ")
    category = input("Category (network/hardware/software/other): ")
    urgency = input("Urgency (high/medium/low): ")
    affected = input("Affected users: ")
    try:
        ticket = add_ticket(title, category, urgency, int(affected), tickets)
        save_tickets(tickets)
        print(f"Created {ticket['id']} (priority: {ticket['priority']})")
    except (ValueError, TypeError) as e:
        print(f"Error: {e}")


def list_tickets(tickets):
    if not tickets:
        print("No tickets yet.")
        return
    for t in tickets:
        print(f"{t['id']} | {t['title']} | {t['category']} | {t['priority']} | {t['status']}")


def view_ticket(tickets):
    ticket_id = input("Ticket ID: ")
    try:
        ticket = find_ticket(tickets, ticket_id)
        for key, value in ticket.items():
            print(f"{key}: {value}")
    except ValueError as e:
        print(f"Error: {e}")


def assign_ticket_menu(tickets):
    ticket_id = input("Ticket ID: ")
    assignee = input("Assign to: ")
    try:
        ticket = assign_ticket(tickets, ticket_id, assignee)
        save_tickets(tickets)
        print(f"{ticket['id']} assigned to {ticket['assigned_to']}")
    except ValueError as e:
        print(f"Error: {e}")


def update_status_menu(tickets):
    ticket_id = input("Ticket ID: ")
    new_status = input("New status (open/in_progress/resolved/closed): ")
    try:
        ticket = update_status(tickets, ticket_id, new_status)
        save_tickets(tickets)
        print(f"{ticket['id']} is now {ticket['status']}")
    except ValueError as e:
        print(f"Error: {e}")


def show_work_queue(tickets):
    queue = get_work_queue(tickets)
    if not queue:
        print("Queue is empty.")
        return
    for t in queue:
        print(f"{t['id']} | {t['priority']} | {t['affected_users']} users | {t['title']} | {t['assigned_to']}")


def show_reports(tickets):
    report = generate_report(tickets)
    print(f"Total: {report['total']}")
    print(f"Unassigned: {report['unassigned']}")
    print(f"By status: {report['by_status']}")
    print(f"By priority: {report['by_priority']}")
    print(f"By category: {report['by_category']}")


def main():
    tickets = load_tickets()

    while True:
        show_menu()
        choice = input("> ").strip()

        if choice == "1":
            create_ticket_menu(tickets)
        elif choice == "2":
            list_tickets(tickets)
        elif choice == "3":
            view_ticket(tickets)
        elif choice == "4":
            assign_ticket_menu(tickets)
        elif choice == "5":
            update_status_menu(tickets)
        elif choice == "6":
            show_work_queue(tickets)
        elif choice == "7":
            show_reports(tickets)
        elif choice == "8":
            break
        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()