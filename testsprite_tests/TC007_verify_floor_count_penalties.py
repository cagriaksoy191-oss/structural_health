import sys
import os
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import RiskRequest, yapisal_skor_hesapla


class TestFloorCountPenalties(unittest.TestCase):
    def setUp(self):
        self.base_req = RiskRequest(
            il="Istanbul",
            ilce="Kadikoy",
            yapimYili=2020,
            katSayisi=1,  # Default safe
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
        # Year 2020 gives +1 base score. We need to account for that or reset it?
        # Actually yapisal_skor_hesapla sums everything up.
        # Let's keep year constant (2020 -> +1)

    def test_low_floors(self):
        self.base_req.katSayisi = 3
        skor, detaylar = yapisal_skor_hesapla(self.base_req, "Z1")
        # <= 3 kat (+0)
        self.assertIn("3 kat (+0)", detaylar)
        # Total = 1 (Year) + 0 (Floor) = 1
        self.assertEqual(skor, 1)

    def test_medium_floors(self):
        self.base_req.katSayisi = 5
        skor, detaylar = yapisal_skor_hesapla(self.base_req, "Z1")
        # <= 5 kat (+1)
        self.assertIn("5 kat (+1)", detaylar)
        # Total = 1 (Year) + 1 (Floor) = 2
        self.assertEqual(skor, 2)

    def test_high_structure_limit(self):
        self.base_req.katSayisi = 8
        skor, detaylar = yapisal_skor_hesapla(self.base_req, "Z1")
        # <= 8 kat (+2)
        self.assertIn("8 kat (+2)", detaylar)
        # High Structure Warning (>=8) (+2)
        found_warning = any("Yüksek Yapı Kategorisi" in d for d in detaylar)
        self.assertTrue(found_warning, "Should trigger High Structure Warning")

        # Total = 1 (Year) + 2 (Floor Base) + 2 (High Struct Penalty) = 5
        self.assertEqual(skor, 5)


if __name__ == "__main__":
    unittest.main()
