from app.adapters.koha_rest import KohaRestAdapter


def main():
    adapter = KohaRestAdapter()

    user_id = "K001"
    book_ids = ["B005","B006"]

    print("[TEST] Starting KOHA adapter issue test")
    print(f"[TEST] User: {user_id}")
    print(f"[TEST] Books: {book_ids}")

    try:
        result = adapter.issue_books(
            user_id,
            book_ids,
        )

        print()
        print("[TEST] Adapter issue successful")
        print(f"KOHA Patron ID: {result['patron_id']}")

        for item in result["successful"]:
            checkout = item["checkout"]

            print()
            print(f"Local book ID: {item['local_book_id']}")
            print(f"KOHA item ID: {item['koha_item_id']}")
            print(f"Checkout ID: {checkout.get('checkout_id')}")
            print(f"Patron ID: {checkout.get('patron_id')}")
            print(f"Item ID: {checkout.get('item_id')}")
            print(f"Due date: {checkout.get('due_date')}")

    except Exception as error:
        print()
        print("[TEST] Adapter issue failed")
        print(f"[ERROR] {type(error).__name__}: {error}")
        raise


if __name__ == "__main__":
    main()