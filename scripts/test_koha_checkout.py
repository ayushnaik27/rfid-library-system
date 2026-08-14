from app.adapters.koha_rest import KohaRestAdapter


def main():
    adapter = KohaRestAdapter()

    patron_id = 93
    item_id = 1

    print("[TEST] Checking checkout availability...")

    availability = adapter.checkout_availability(
        patron_id,
        item_id,
    )

    print()
    print("[KOHA] Checkout availability:")
    print(f"Blockers: {availability.get('blockers')}")
    print(f"Warnings: {availability.get('warnings')}")
    print(f"Confirms: {availability.get('confirms')}")
    print(
        "Confirmation token received:",
        bool(availability.get("confirmation_token"))
    )

    if availability.get("blockers"):
        print()
        print("[KOHA] Checkout blocked.")
        return

    print()
    print("[TEST] Creating checkout...")

    checkout = adapter.issue_book(
        patron_id,
        item_id,
    )

    print()
    print("[KOHA] BOOK ISSUED SUCCESSFULLY")
    print(f"Checkout ID: {checkout.get('checkout_id')}")
    print(f"Patron ID: {checkout.get('patron_id')}")
    print(f"Item ID: {checkout.get('item_id')}")
    print(f"Due date: {checkout.get('due_date')}")


if __name__ == "__main__":
    main()