import unittest
from services.earthquake import (
    deprem_seviyesi_bul,
    deprem_seviyesi_puan,
    tahmini_zemin_sinifi
)

class TestEarthquakeServices(unittest.TestCase):
    def test_deprem_seviyesi_bul_known(self):
        # Known city and district
        self.assertEqual(deprem_seviyesi_bul("istanbul", "avcılar"), "yüksek")
        self.assertEqual(deprem_seviyesi_bul("ankara", "elmadağ"), "orta")
        self.assertEqual(deprem_seviyesi_bul("trabzon", "merkez"), "düşük")

    def test_deprem_seviyesi_bul_city_default(self):
        # Known city, unknown district -> returns city _default
        # istanbul _default is "yüksek"
        self.assertEqual(deprem_seviyesi_bul("istanbul", "bilinmeyen_ilce"), "yüksek")
        # ankara _default is "düşük"
        self.assertEqual(deprem_seviyesi_bul("ankara", "bilinmeyen_ilce"), "düşük")

    def test_deprem_seviyesi_bul_global_default(self):
        # Unknown city -> returns "orta"
        self.assertEqual(deprem_seviyesi_bul("bilinmeyen_sehir", "herhangi_ilce"), "orta")

    def test_deprem_seviyesi_bul_normalization(self):
        # Test case and Turkish character normalization
        self.assertEqual(deprem_seviyesi_bul("İSTANBUL", "Sarıyer"), "orta")
        self.assertEqual(deprem_seviyesi_bul("izmir", "KİRAZ"), "orta")
        self.assertEqual(deprem_seviyesi_bul("  Antalya  ", "ALANYA"), "düşük")

    def test_deprem_seviyesi_puan(self):
        # Known levels
        self.assertEqual(deprem_seviyesi_puan("yüksek"), 3)
        self.assertEqual(deprem_seviyesi_puan("orta"), 1)
        self.assertEqual(deprem_seviyesi_puan("düşük"), 0)
        # Unknown level
        self.assertEqual(deprem_seviyesi_puan("bilinmeyen"), 0)

    def test_tahmini_zemin_sinifi_known(self):
        # Known city and district
        self.assertEqual(tahmini_zemin_sinifi("istanbul", "avcılar"), "Z4")
        self.assertEqual(tahmini_zemin_sinifi("ankara", "etimesgut"), "Z4")
        self.assertEqual(tahmini_zemin_sinifi("izmir", "bayraklı"), "Z4")

    def test_tahmini_zemin_sinifi_city_default(self):
        # Known city, unknown district -> city _default
        # istanbul _default is "Z3"
        self.assertEqual(tahmini_zemin_sinifi("istanbul", "bilinmeyen"), "Z3")
        # ankara _default is "Z2"
        self.assertEqual(tahmini_zemin_sinifi("ankara", "bilinmeyen"), "Z2")

    def test_tahmini_zemin_sinifi_global_default(self):
        # Unknown city -> "Z3"
        self.assertEqual(tahmini_zemin_sinifi("bilinmeyen_sehir", "merkez"), "Z3")

if __name__ == "__main__":
    unittest.main()
