import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.db.base import Base, engine  # noqa: E402
from app.services.rfid_mapping_service import create_mapping  # noqa: E402


def parse_args():
    parser = argparse.ArgumentParser(
        description="Register a physical RFID card UID to a local library user."
    )
    parser.add_argument("--rfid-uid", required=True, help="UID read from the RFID card.")
    parser.add_argument(
        "--user-id",
        required=True,
        help="Local mapped user/card id, for example K001.",
    )
    parser.add_argument("--user-name", required=True, help="Display name for this card.")
    return parser.parse_args()


def main():
    args = parse_args()
    Base.metadata.create_all(bind=engine)

    mapping = create_mapping(args.rfid_uid, args.user_id, args.user_name)

    if not mapping:
        print("Mapping failed. Check the RFID UID and user details.")
        return 1

    print(
        "Registered RFID card "
        f"{mapping['uid']} -> user {mapping['user_id']} ({mapping['user_name']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
