from app.adapters.koha_rest import KohaRestAdapter


def main():
    adapter = KohaRestAdapter()

    token = adapter.get_access_token()

    print()
    print("[KOHA] Authentication successful")
    print(f"[KOHA] Token received: {bool(token)}")
    print(f"[KOHA] Token length: {len(token)}")


if __name__ == "__main__":
    main()