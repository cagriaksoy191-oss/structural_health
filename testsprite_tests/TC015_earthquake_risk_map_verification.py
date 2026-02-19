import sys
import os
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import deprem_seviyesi_bul, deprem_seviyesi_puan


class TestEarthquakeRiskMap(unittest.TestCase):
    def test_istanbul_avcilar_yuksek(self):
        seviye = deprem_seviyesi_bul("Istanbul", "Avcilar")
        puan = deprem_seviyesi_puan(seviye)
        self.assertEqual(seviye, "yüksek")
        self.assertEqual(puan, 3)

    def test_rize_dusuk(self):
        seviye = deprem_seviyesi_bul("Rize", "Merkez")
        puan = deprem_seviyesi_puan(seviye)
        self.assertEqual(seviye, "düşük")
        self.assertEqual(puan, 0)

    def test_ankara_elmadag_orta(self):
        seviye = deprem_seviyesi_bul("Ankara", "Elmadag")
        puan = deprem_seviyesi_puan(seviye)
        self.assertEqual(seviye, "orta")
        self.assertEqual(puan, 1)

    def test_unknown_city_default(self):
        seviye = deprem_seviyesi_bul("BilinmeyenSehir", "Merkez")
        puan = deprem_seviyesi_puan(seviye)
        # Default behavior is "orta" -> 1
        self.assertEqual(seviye, "orta")
        self.assertEqual(puan, 1)


if __name__ == "__main__":
    unittest.main()
