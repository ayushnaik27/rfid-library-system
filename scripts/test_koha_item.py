from app.adapters.koha_rest import KohaRestAdapter


def main():
    adapter = KohaRestAdapter()

    external_id = "PK5"

    print(
        f"[TEST] Looking up KOHA item "
        f"with external ID: {external_id}"
    )

    item = adapter.get_item(external_id)

    print()
    print("[KOHA] Item lookup successful")
    print(f"External ID: {item.get('external_id')}")
    print(f"Item ID: {item.get('item_id')}")
    print(f"Biblio ID: {item.get('biblio_id')}")
    print(f"Call number: {item.get('callnumber')}")
    print(
        f"Checked out: "
        f"{item.get('checked_out_date')}"
    )


if __name__ == "__main__":
    main()