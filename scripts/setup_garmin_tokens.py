#!/usr/bin/env python3
"""Create the local Garmin token file used to bootstrap GitHub Actions."""

from getpass import getpass
from pathlib import Path

from garminconnect import Garmin


def main() -> None:
    token_store = Path(__file__).resolve().parents[1] / ".garminconnect"
    email = input("Garmin email: ").strip()
    password = getpass("Garmin password: ")
    client = Garmin(
        email=email,
        password=password,
        prompt_mfa=lambda: input("Garmin MFA code: ").strip(),
    )
    client.login(str(token_store))
    print(f"Garmin tokens saved to {token_store / 'garmin_tokens.json'}")


if __name__ == "__main__":
    main()
