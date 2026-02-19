import sys
import os
import unittest
from pydantic import ValidationError

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import RiskRequest
from datetime import datetime


class TestEdgeCaseYears(unittest.TestCase):
    def get_valid_payload(self):
        return {
            "il": "Istanbul",
            "ilce": "Kadikoy",
            "yapimYili": 2000,
            "katSayisi": 5,
            "zeminDukkan": "hayir",
            "bitisik": "hayir",
            "hasar": "yok",
            "kullanimAmaci": "konut",
            "kisaKolon": "yok",
            "agirCikma": "yok",
            "planTipi": "dikdortgen",
            "bitisikHiza": "yok",
            "ultrasonikSesHizi": 4000,
            "geriSicramaSayisi": 40,
            "corrosion": 0,
            "zeminSinifi": "Z1",
            "crackPuan": 0,
        }

    def test_minimum_year_1800(self):
        payload = self.get_valid_payload()
        payload["yapimYili"] = 1800
        # Should NOT raise error
        try:
            RiskRequest(**payload)
        except ValidationError:
            self.fail("Year 1800 should be valid")

    def test_below_minimum_year_1799(self):
        payload = self.get_valid_payload()
        payload["yapimYili"] = 1799
        with self.assertRaises(ValidationError):
            RiskRequest(**payload)

    def test_future_year(self):
        current_year = datetime.now().year
        payload = self.get_valid_payload()
        payload["yapimYili"] = current_year + 5
        with self.assertRaises(ValidationError) as cm:
            RiskRequest(**payload)
        self.assertIn("gelecekte olamaz", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
