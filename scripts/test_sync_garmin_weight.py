import os
import unittest
from unittest.mock import patch

from sync_garmin_weight import (
    build_public_status,
    extract_current_weight,
    extract_target_weight,
    fetch_status,
    garmin_mass_to_kg,
)


class GarminWeightSyncTests(unittest.TestCase):
    def test_converts_garmin_grams_to_kilograms(self):
        self.assertEqual(garmin_mass_to_kg(82_500), 82.5)

    def test_tolerates_kilogram_values(self):
        self.assertEqual(garmin_mass_to_kg(82.5), 82.5)

    def test_extracts_latest_weight_and_date(self):
        weight, measured = extract_current_weight(
            {"weight": 82_500, "date": "2026-08-22"}
        )
        self.assertEqual(weight, 82.5)
        self.assertEqual(measured, "2026-08-22")

    def test_extracts_weight_goal(self):
        target = extract_target_weight(
            [{"userGoalTypePK": 4, "goalValue": 80_000}]
        )
        self.assertEqual(target, 80.0)

    @patch.dict(os.environ, {"GARMIN_TARGET_WEIGHT_KG": "80"}, clear=False)
    def test_uses_explicit_target_only_when_garmin_has_no_goal(self):
        self.assertEqual(extract_target_weight([]), 80.0)

    def test_public_status_contains_only_the_difference(self):
        status = build_public_status(82.5, 80.0, "2026-08-22")
        self.assertEqual(status["kgToLose"], 2.5)
        self.assertNotIn("currentWeight", status)
        self.assertNotIn("targetWeight", status)

    def test_fetches_latest_weight_and_active_garmin_goal(self):
        class FakeGarmin:
            def connectapi(self, path, params):
                self.path = path
                self.params = params
                return {"weight": 82_500, "date": "2026-08-22"}

            def get_goals(self, status):
                self.goal_status = status
                return [{"userGoalTypePK": 4, "goalValue": 80_000}]

        client = FakeGarmin()
        status = fetch_status(client)

        self.assertEqual(client.path, "/weight-service/weight/latest")
        self.assertEqual(client.goal_status, "active")
        self.assertEqual(status["kgToLose"], 2.5)


if __name__ == "__main__":
    unittest.main()
