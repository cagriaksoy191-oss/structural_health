import sys
import os
import unittest
import skfuzzy.control as ctrl

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.fuzzy_engine import fuzzy_control_system_v2
from main import clamp


class TestFuzzyLogicConsistency(unittest.TestCase):
    def setUp(self):
        self.sim = ctrl.ControlSystemSimulation(fuzzy_control_system_v2)

    def get_fuzzy_score(self, strength, corrosion, survey_risk):
        self.sim.input["strength"] = clamp(float(strength), 0.0, 80.0)
        self.sim.input["corrosion"] = clamp(float(corrosion), -600.0, 100.0)
        self.sim.input["survey_risk"] = clamp(float(survey_risk), 0.0, 50.0)
        self.sim.compute()
        return self.sim.output["health"]

    def test_very_bad_building(self):
        # Low Strength (10), High Corrosion (-500), High Survey Risk (45)
        # Should be Very Bad -> Score < 25
        score = self.get_fuzzy_score(strength=10, corrosion=-500, survey_risk=45)
        print(f"Very Bad Inputs -> Score: {score}")
        self.assertTrue(
            score < 30, f"Expected low score (<30) for bad building, got {score}"
        )

    def test_very_good_building(self):
        # High Strength (50), Low Corrosion (-50), Low Survey Risk (2)
        # Should be Very Good -> Score > 75
        score = self.get_fuzzy_score(strength=50, corrosion=-50, survey_risk=2)
        print(f"Very Good Inputs -> Score: {score}")
        self.assertTrue(
            score > 70, f"Expected high score (>70) for good building, got {score}"
        )


if __name__ == "__main__":
    unittest.main()
