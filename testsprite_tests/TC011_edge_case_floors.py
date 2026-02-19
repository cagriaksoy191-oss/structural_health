import sys
import os
import unittest
from pydantic import ValidationError

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import RiskRequest


class TestEdgeCaseFloors(unittest.TestCase):
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

    def test_min_floor_1(self):
        payload = self.get_valid_payload()
        payload["katSayisi"] = 1
        try:
            RiskRequest(**payload)
        except ValidationError:
            self.fail("Floor 1 should be valid")

    def test_zero_floor(self):
        payload = self.get_valid_payload()
        payload["katSayisi"] = 0
        with self.assertRaises(ValidationError):
            RiskRequest(**payload)

    def test_max_floor_100(self):
        payload = self.get_valid_payload()
        payload["katSayisi"] = 100
        try:
            RiskRequest(**payload)
        except ValidationError:
            self.fail("Floor 100 should be valid")

    def test_over_max_floor_101(self):
        payload = self.get_valid_payload()
        payload["katSayisi"] = 101
        with self.assertRaises(ValidationError):
            RiskRequest(**payload)


if __name__ == "__main__":
    unittest.main()
