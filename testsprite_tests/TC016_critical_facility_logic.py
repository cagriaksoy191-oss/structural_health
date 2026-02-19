import sys
import os
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import RiskRequest, yapisal_skor_hesapla


class TestCriticalFacilityLogic(unittest.TestCase):
    def setUp(self):
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

    def test_konut_no_penalty(self):
        self.base_req.kullanimAmaci = "konut"
        skor, detaylar = yapisal_skor_hesapla(self.base_req, "Z1")
        # Should not have critical facility penalty
        self.assertFalse(any("Kritik kullanım" in d for d in detaylar))

    def test_okul_penalty(self):
        self.base_req.kullanimAmaci = "okul"
        skor, detaylar = yapisal_skor_hesapla(self.base_req, "Z1")
        # Kritik kullanım (okul) (+2)
        self.assertIn("Kritik kullanım (okul) (+2)", detaylar)
        # Base (Year 2020 -> +1) + Okul (+2) = 3
        self.assertEqual(skor, 3)

    def test_hastane_penalty(self):
        self.base_req.kullanimAmaci = "hastane"
        skor, detaylar = yapisal_skor_hesapla(self.base_req, "Z1")
        # Kritik kullanım (hastane) (+2)
        self.assertIn("Kritik kullanım (hastane) (+2)", detaylar)
        self.assertEqual(skor, 3)


if __name__ == "__main__":
    unittest.main()
