import argparse
import logging
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import (  # noqa: E402
    RFID_BAUD_RATE,
    RFID_READ_TIMEOUT_SECONDS,
    RFID_RECONNECT_DELAY_SECONDS,
    RFID_SERIAL_PORTS,
)
from app.hardware.serial_reader import SerialRFIDReader  # noqa: E402


def parse_args():
    parser = argparse.ArgumentParser(
        description="Test a serial RFID reader and print scanned UID/tag values."
    )
    parser.add_argument(
        "--ports",
        default=",".join(RFID_SERIAL_PORTS),
        help="Comma-separated serial ports to try. Default: COM4,COM5",
    )
    parser.add_argument(
        "--baud",
        type=int,
        default=RFID_BAUD_RATE,
        help="Serial baud rate. Common values: 9600, 19200, 38400, 57600, 115200",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=RFID_READ_TIMEOUT_SECONDS,
        help="Serial read timeout in seconds.",
    )
    parser.add_argument(
        "--reconnect-delay",
        type=float,
        default=RFID_RECONNECT_DELAY_SECONDS,
        help="Seconds to wait between reconnect attempts.",
    )
    return parser.parse_args()


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )

    args = parse_args()
    ports = [port.strip() for port in args.ports.split(",") if port.strip()]

    if not ports:
        print("No serial ports provided. Example: --ports COM4,COM5")
        return 2

    print("RFID serial reader test")
    print(f"Ports: {', '.join(ports)}")
    print(f"Baud: {args.baud}")
    print("Scan a card/tag now. Press Ctrl+C to stop.")

    try:
        with SerialRFIDReader(
            ports=ports,
            baud_rate=args.baud,
            timeout=args.timeout,
            reconnect_delay=args.reconnect_delay,
        ) as reader:
            while True:
                uid = reader.read_uid()

                if uid:
                    print(f"RFID UID: {uid}", flush=True)

                time.sleep(0.05)
    except KeyboardInterrupt:
        print("\nStopped.")
        return 0
    except RuntimeError as exc:
        print(exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
