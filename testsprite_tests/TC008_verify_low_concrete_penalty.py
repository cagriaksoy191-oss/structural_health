import sys
import os
import unittest
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# We need to test the logic inside risk_hesapla endpoint function where concrete check happens.
# Since risk_hesapla is an endpoint, we can invoke it directly if we mock dependencies (db, ai).
from main import risk_hesapla, RiskRequest


class TestLowConcretePenalty(unittest.TestCase):
    @patch("main.kayit_ekle_supabase")
    @patch("main.get_llm_comment")
    @patch("main.tahmin_beton_dayanimi")
    def test_low_concrete_adds_penalty(self, mock_beton, mock_ai, mock_db):
        # Setup mocks
        mock_beton.return_value = 20.0  # Below 25 MPa
        mock_ai.return_value = "Test yorumu"

        req = RiskRequest(
            il="Istanbul",
            ilce="Kadikoy",
            yapimYili=2020,
            katSayisi=1,
            zeminDukkan="hayir",
            bitisik="hayir",
            hasar="yok",
            kullanimAmaci="konut",
            kisaKolon="yok",
            agirCikma="yok",
            planTipi="dikdortgen",
            bitisikHiza="yok",
            ultrasonikSesHizi=3000,
            geriSicramaSayisi=20,
            corrosion=0,
            zeminSinifi="Z1",
            crackPuan=0,
        )

        response = risk_hesapla(req)

        # Check for penalty details
        detaylar = response.detaylar

        # Expect "Yönetmelik altı beton nedeniyle ek risk (+5)"
        penalty_found = any("Yönetmelik altı beton" in d for d in detaylar)
        self.assertTrue(penalty_found, "Should add penalty for low concrete strength")

        # Check Total Risk Score
        # Year 2020 -> +1
        # Floor 1 -> +0
        # Concrete < 25 -> +5
        # Total Structural Risk should be at least 6.
        # Plus earthquake risk (Istanbul/Kadikoy -> High -> +3) for Total Risk calculation?
        # Main.py: toplam_yapisal_risk = yapisal_puan + deprem_puan
        # yapisal_puan = 1 (Year) + 5 (Concrete) = 6
        # deprem_puan (Istanbul/Kadikoy) = 3 (Yüksek)
        # Total Expected = 9

        self.assertEqual(response.toplamYapisalRisk, 9)


if __name__ == "__main__":
    unittest.main()
