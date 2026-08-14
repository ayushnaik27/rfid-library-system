from app.adapters.koha_rest import KohaRestAdapter


def main():
    adapter = KohaRestAdapter()

    patron = adapter.get_patron("K001")

    print()
    print("[KOHA] Patron lookup successful")
    print(f"[KOHA] Patron ID: {patron.get('patron_id')}")
    print(f"[KOHA] Card number: {patron.get('cardnumber')}")
    print(f"[KOHA] Name: {patron.get('surname')}, {patron.get('firstname')}")


if __name__ == "__main__":
    main()