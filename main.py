from campusflow.tickets import add_ticket

def main():
    tickets = []

    while True:
        print("\n1. Add ticket\n2. View tickets\n3. Quit")
        choice = input("Choose: ").strip()

        if choice == "1":
            title = input("Title: ")
            category = input("Category (network/hardware/software/other): ")
            urgency = input("Urgency (high/medium/low): ")
            affected = input("Affected users: ")

            try:
                affected = int(affected)
                ticket = add_ticket(title, category, urgency, affected, tickets)
                print(f"Created {ticket['id']} (priority: {ticket['priority']})")
            except (ValueError, TypeError) as e:
                print(f"Error: {e}")

        elif choice == "2":
            if not tickets:
                print("No tickets yet.")
            for t in tickets:
                print(f"{t['id']} | {t['title']} | {t['category']} | {t['priority']} | {t['status']}")

        elif choice == "3":
            break
        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()