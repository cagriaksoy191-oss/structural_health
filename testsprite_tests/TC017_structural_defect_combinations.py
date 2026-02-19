import sys
import os
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import RiskRequest, yapisal_skor_hesapla


class TestStructuralDefectCombinations(unittest.TestCase):
    def setUp(self):
        self.base_req = RiskRequest(
            il="Istanbul",
            ilce="Kadikoy",
            yapimYili=2020,
            katSayisi=3,  # Year +1
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

    def test_lethal_combo(self):
        # Kisa Kolon (+3) + Agir Cikma (Buyuk +2) + Duzensiz Plan (L +2)
        self.base_req.kisaKolon = "var"
        self.base_req.agirCikma = "buyuk"
        self.base_req.planTipi = "L"

        skor, detaylar = yapisal_skor_hesapla(self.base_req, "Z1")

        # Check components
        self.assertIn("Kısa kolon (+3)", detaylar)
        self.assertIn("Büyük çıkma (+2)", detaylar)
        self.assertIn("Düzensiz plan L (+2)", detaylar)

        # Total = 1 (Year) + 3 + 2 + 2 = 8
        self.assertEqual(skor, 8)


if __name__ == "__main__":
    unittest.main()
