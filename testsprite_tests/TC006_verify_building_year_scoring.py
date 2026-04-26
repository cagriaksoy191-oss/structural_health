import sys
import os
import unittest

# Add parent directory to path to import main
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import RiskRequest, yapisal_skor_hesapla


class TestBuildingYearScoring(unittest.TestCase):
    def setUp(self):
        # Create a base request with neutral values
        self.base_req = RiskRequest(
            il="Istanbul",
            ilce="Kadikoy",
            yapimYili=2020,
            katSayisi=3,
            zeminDukkan="hayir",
            bitisik="hayir",
            hasar="yok",
            kullanimAmaci="konut",
            kisaKolon="yok",
            agirCikma="yok",
            planTipi="dikdortgen",
            bitisikHiza="yok",
            ultrasonikSesHizi=4000,
            geriSicramaSayisi=40,
            corrosion=0,
            zeminSinifi="Z1",
            crackPuan=0,
        )

    def test_year_before_1975(self):
        self.base_req.yapimYili = 1970
        skor, detaylar = yapisal_skor_hesapla(self.base_req, "Z1")
        # 1975 ve öncesi (+5)
        self.assertIn("1970 ve öncesi (+5)", detaylar)
        # Base skor is 1 (year) + 0 (others). Wait, logic:
        # if <= 1975: +5.
        # So we expect at least 5 points from year.
        # Other factors are 0.
        self.assertEqual(skor, 5)

    def test_year_1976_1999(self):
        self.base_req.yapimYili = 1990
        skor, detaylar = yapisal_skor_hesapla(self.base_req, "Z1")
        # 1999 öncesi (+4)
        self.assertIn("1990 – 1999 öncesi (+4)", detaylar)
        self.assertEqual(skor, 4)

    def test_year_2000_2018(self):
        self.base_req.yapimYili = 2005
        skor, detaylar = yapisal_skor_hesapla(self.base_req, "Z1")
        # 2018 öncesi (+2)
        self.assertIn("2005 – 2018 öncesi (+2)", detaylar)
        self.assertEqual(skor, 2)

    def test_year_after_2018(self):
        self.base_req.yapimYili = 2021
        skor, detaylar = yapisal_skor_hesapla(self.base_req, "Z1")
        # 2018 sonrası (+1)
        self.assertIn("2021 sonrası (+1)", detaylar)
        self.assertEqual(skor, 1)


if __name__ == "__main__":
    unittest.main()
