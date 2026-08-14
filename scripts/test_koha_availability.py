from app.adapters.koha_rest import KohaRestAdapter


def main():
    adapter = KohaRestAdapter()

    patron_id = 93
    item_id = 2

    print("[TEST] Checking KOHA checkout availability")
    print(f"[TEST] Patron ID: {patron_id}")
    print(f"[TEST] Item ID: {item_id}")

    try:
        result = adapter.checkout_availability(
            patron_id,
            item_id,
        )

        print()
        print("[KOHA] Availability response:")
        print(result)

        print()
        print(f"Blockers: {result.get('blockers')}")
        print(f"Warnings: {result.get('warnings')}")
        print(f"Confirms: {result.get('confirms')}")
        print(
            "Confirmation token:",
            bool(result.get("confirmation_token"))
        )

    except Exception as error:
        print()
        print("[TEST] Availability check failed")
        print(f"[ERROR] {type(error).__name__}: {error}")
        raise


if __name__ == "__main__":
    main()