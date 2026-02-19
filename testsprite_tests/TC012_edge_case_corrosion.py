import sys
import os
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import korozyon_olasiligi


class TestEdgeCaseCorrosion(unittest.TestCase):
    def test_extreme_low_corrosion(self):
        # -1000 mV -> Very High Risk -> Should cap at 98%
        yuzde, seviye, renk = korozyon_olasiligi(-1000.0)
        self.assertEqual(yuzde, 98)
        self.assertEqual(seviye, "Çok Yüksek")

    def test_extreme_high_corrosion(self):
        # +500 mV -> No Risk -> Should cap at 2% (min)
        yuzde, seviye, renk = korozyon_olasiligi(500.0)
        self.assertEqual(yuzde, 5)  # Logic: if mv >= -100: yuzde = 5
        self.assertEqual(seviye, "Düşük")

    def test_boundary_values(self):
        # -200 mV
        yuzde, _, _ = korozyon_olasiligi(-200.0)
        # Logic: if mv >= -200: ((-100 - (-200))/100)*5 + 5 = (100/100)*5 + 5 = 10
        self.assertEqual(yuzde, 10)


if __name__ == "__main__":
    unittest.main()
