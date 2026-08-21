#!/usr/bin/env python3
"""Publish a privacy-preserving weight-goal status from Garmin Connect."""

from __future__ import annotations

import json
import os
import sys
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any


WEIGHT_GOAL_TYPE_ID = 4
OUTPUT_PATH = Path(__file__).resolve().parents[1] / "health.json"


def _number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if result > 0 else None


def garmin_mass_to_kg(value: Any) -> float:
    """Convert Garmin's gram values to kg, tolerating kg-shaped fixtures."""
    number = _number(value)
    if number is None:
        raise ValueError("Garmin returned an invalid weight value")
    return number / 1000 if number >= 300 else number


def _first_number(mapping: dict[str, Any], keys: tuple[str, ...]) -> float | None:
    for key in keys:
        number = _number(mapping.get(key))
        if number is not None:
            return number
    return None


def _measurement_date(payload: dict[str, Any]) -> str | None:
    for key in ("date", "calendarDate", "summaryDate", "weightDate", "timestamp"):
        value = payload.get(key)
        if isinstance(value, str) and len(value) >= 10:
            return value[:10]
        number = _number(value)
        if number is not None and number > 1_000_000_000:
            seconds = number / 1000 if number > 10_000_000_000 else number
            return datetime.fromtimestamp(seconds, UTC).date().isoformat()
    return None


def extract_current_weight(payload: Any) -> tuple[float, str | None]:
    """Extract the latest weight from Garmin's latest/range response shapes."""
    if isinstance(payload, dict):
        raw_weight = _first_number(payload, ("weight", "latestWeight", "value"))
        if raw_weight is not None:
            return garmin_mass_to_kg(raw_weight), _measurement_date(payload)

        for key in ("dateWeightList", "dailyWeightSummaries", "items"):
            values = payload.get(key)
            if isinstance(values, list) and values:
                dated_values = []
                for item in values:
                    if isinstance(item, dict):
                        dated_values.append((_measurement_date(item) or "", item))
                if dated_values:
                    return extract_current_weight(max(dated_values, key=lambda pair: pair[0])[1])

    if isinstance(payload, list) and payload:
        dated_values = [
            (_measurement_date(item) or "", item)
            for item in payload
            if isinstance(item, dict)
        ]
        if dated_values:
            return extract_current_weight(max(dated_values, key=lambda pair: pair[0])[1])

    raise ValueError("Garmin Connect did not return a weigh-in")


def _is_weight_goal(goal: dict[str, Any]) -> bool:
    for key in ("userGoalTypePK", "goalTypeId", "typeId"):
        try:
            if int(goal.get(key)) == WEIGHT_GOAL_TYPE_ID:
                return True
        except (TypeError, ValueError):
            pass

    for key in ("goalType", "goalTypeKey", "type", "name"):
        if "weight" in str(goal.get(key, "")).lower():
            return True
    return False


def extract_target_weight(goals: Any) -> float:
    if isinstance(goals, dict):
        goals = goals.get("items") or goals.get("goals") or [goals]
    if not isinstance(goals, list):
        raise ValueError("Garmin Connect returned an invalid goals response")

    for goal in goals:
        if not isinstance(goal, dict) or not _is_weight_goal(goal):
            continue
        raw_target = _first_number(
            goal,
            ("goalValue", "targetValue", "targetWeight", "weight", "value"),
        )
        if raw_target is not None:
            return garmin_mass_to_kg(raw_target)

    fallback = _number(os.getenv("GARMIN_TARGET_WEIGHT_KG"))
    if fallback is not None:
        return fallback
    raise ValueError("No active Garmin weight goal was found")


def build_public_status(
    current_weight_kg: float,
    target_weight_kg: float,
    measurement_date: str | None,
) -> dict[str, Any]:
    status: dict[str, Any] = {
        "kgToLose": round(max(0, current_weight_kg - target_weight_kg), 1),
        "source": "Garmin Connect",
    }
    if measurement_date:
        status["measurementDate"] = measurement_date
    return status


def connect_to_garmin() -> Any:
    try:
        from garminconnect import Garmin
    except ImportError as error:
        raise RuntimeError(
            "garminconnect is not installed; run pip install -r requirements-garmin.txt"
        ) from error

    token_json = os.getenv("GARMIN_TOKENS_JSON", "").strip()
    if token_json:
        client = Garmin()
        client.login(token_json)
        return client

    email = os.getenv("GARMIN_EMAIL", "").strip()
    password = os.getenv("GARMIN_PASSWORD", "")
    if not email or not password:
        raise RuntimeError(
            "Set GARMIN_TOKENS_JSON, or set both GARMIN_EMAIL and GARMIN_PASSWORD"
        )

    client = Garmin(email=email, password=password)
    client.login()
    return client


def fetch_status(client: Any) -> dict[str, Any]:
    today = date.today().isoformat()
    latest = client.connectapi(
        "/weight-service/weight/latest",
        params={"date": today},
    )
    current_weight, measurement_date = extract_current_weight(latest)
    target_weight = extract_target_weight(client.get_goals(status="active"))
    return build_public_status(current_weight, target_weight, measurement_date)


def write_status(status: dict[str, Any], output_path: Path = OUTPUT_PATH) -> None:
    output_path.write_text(
        json.dumps(status, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    try:
        status = fetch_status(connect_to_garmin())
        write_status(status)
    except Exception as error:
        print(f"Garmin weight sync failed: {error}", file=sys.stderr)
        return 1

    print("Garmin weight status updated without publishing exact weights.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
