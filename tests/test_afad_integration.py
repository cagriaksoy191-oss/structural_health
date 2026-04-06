"""AFAD Deprem Tehlike Haritası API Entegrasyon Testleri"""

import sys
import os
import unittest
import unittest.mock
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.afad_api import (
    get_city_coordinates,
    cache_get,
    cache_set,
    cache_get as _cg,
    pga_to_risk_seviyesi,
    _haversine_km,
    _estimate_pga_from_earthquake,
    calculate_pga_from_events,
)
from services.earthquake import (
    deprem_seviyesi_bul,
    deprem_seviyesi_puan,
    deprem_analizi_async,
)


class TestCityCoordinates(unittest.TestCase):
    """İl koordinat tablosu testleri"""

    def test_istanbul_coordinates(self):
        coords = get_city_coordinates("istanbul")
        self.assertIsNotNone(coords)
        lat, lon = coords
        # İstanbul yaklaşık 41N, 29E
        self.assertAlmostEqual(lat, 41.0, delta=0.5)
        self.assertAlmostEqual(lon, 29.0, delta=0.5)

    def test_ankara_coordinates(self):
        coords = get_city_coordinates("Ankara")
        self.assertIsNotNone(coords)
        lat, lon = coords
        self.assertAlmostEqual(lat, 39.9, delta=0.5)
        self.assertAlmostEqual(lon, 32.9, delta=0.5)

    def test_unknown_city_returns_none(self):
        coords = get_city_coordinates("BilinmeyenSehir")
        self.assertIsNone(coords)

    def test_all_81_cities_exist(self):
        """81 il merkezi koordinat tablosunda olmalı"""
        from services.afad_api import CITY_COORDINATES
        self.assertEqual(len(CITY_COORDINATES), 81)

    def test_coordinates_valid_range(self):
        """Tüm koordinatlar Türkiye sınırları içinde olmalı"""
        from services.afad_api import CITY_COORDINATES
        for city, (lat, lon) in CITY_COORDINATES.items():
            self.assertTrue(
                35.0 <= lat <= 43.0,
                f"{city}: lat={lat} Türkiye sınırları dışında",
            )
            self.assertTrue(
                25.0 <= lon <= 45.0,
                f"{city}: lon={lon} Türkiye sınırları dışında",
            )


class TestCache(unittest.TestCase):
    """In-memory cache testleri"""

    def test_cache_set_and_get(self):
        test_data = {"pga": 0.35, "risk_seviyesi": "orta"}
        cache_set("test_il", "test_ilce", test_data)
        result = cache_get("test_il", "test_ilce")
        self.assertIsNotNone(result)
        self.assertEqual(result["pga"], 0.35)

    def test_cache_miss(self):
        result = cache_get("yok_il", "yok_ilce")
        self.assertIsNone(result)


class TestPGACalculation(unittest.TestCase):
    """PGA hesaplama testleri"""

    def test_haversine_same_point(self):
        dist = _haversine_km(41.0, 29.0, 41.0, 29.0)
        self.assertAlmostEqual(dist, 0.0, places=1)

    def test_haversine_known_distance(self):
        # İstanbul → Ankara yaklaşık 350 km
        dist = _haversine_km(41.0, 29.0, 39.9, 32.9)
        self.assertTrue(300 < dist < 400, f"İstanbul-Ankara mesafesi: {dist} km")

    def test_pga_decreases_with_distance(self):
        pga_close = _estimate_pga_from_earthquake(6.0, 10.0)
        pga_far = _estimate_pga_from_earthquake(6.0, 200.0)
        self.assertGreater(pga_close, pga_far)

    def test_pga_increases_with_magnitude(self):
        pga_small = _estimate_pga_from_earthquake(4.0, 50.0)
        pga_large = _estimate_pga_from_earthquake(7.0, 50.0)
        self.assertGreater(pga_large, pga_small)

    def test_pga_non_negative(self):
        pga = _estimate_pga_from_earthquake(3.0, 500.0)
        self.assertGreaterEqual(pga, 0.0)

    def test_pga_from_events(self):
        events = [
            {"magnitude": 5.5, "latitude": 41.0, "longitude": 29.0},
            {"magnitude": 4.0, "latitude": 40.5, "longitude": 28.5},
        ]
        pga = calculate_pga_from_events(events, 41.1, 29.1)
        self.assertGreater(pga, 0.0)

    def test_pga_from_empty_events(self):
        pga = calculate_pga_from_events([], 41.0, 29.0)
        self.assertEqual(pga, 0.0)


class TestPGAToRisk(unittest.TestCase):
    """PGA → Risk seviyesi dönüşüm testleri"""

    def test_high_risk(self):
        self.assertEqual(pga_to_risk_seviyesi(0.50), "yüksek")
        self.assertEqual(pga_to_risk_seviyesi(0.40), "yüksek")

    def test_medium_risk(self):
        self.assertEqual(pga_to_risk_seviyesi(0.30), "orta")
        self.assertEqual(pga_to_risk_seviyesi(0.20), "orta")

    def test_low_risk(self):
        self.assertEqual(pga_to_risk_seviyesi(0.10), "düşük")
        self.assertEqual(pga_to_risk_seviyesi(0.0), "düşük")


class TestHybridAnalysis(unittest.TestCase):
    """Hybrid deprem analizi testleri"""

    def test_fallback_for_unknown_city(self):
        """Bilinmeyen il → statik haritaya düşmeli, orta döndürmeli"""
        result = asyncio.run(
            deprem_analizi_async("BilinmeyenSehir", "Merkez")
        )
        self.assertIn("seviye", result)
        self.assertIn("kaynak", result)
        # Bilinmeyen şehir → API'de koordinat bulunamaz → fallback
        self.assertEqual(result["seviye"], "orta")

    def test_result_structure(self):
        """Sonuç dict yapısı doğru olmalı"""
        result = asyncio.run(deprem_analizi_async("istanbul", "Kadıköy"))
        self.assertIn("seviye", result)
        self.assertIn("puan", result)
        self.assertIn("kaynak", result)
        self.assertIn(result["seviye"], ["yüksek", "orta", "düşük"])
        self.assertIn(result["puan"], [0, 1, 3])

    @unittest.mock.patch("services.afad_api.calculate_seismic_hazard", new_callable=unittest.mock.AsyncMock)
    def test_scenario_3_honest_fallback(self, mock_calc):
        """Senaryo 3: AFAD düşük risk döndürürse, yüksek olan statik haritaya dürüst fallback yapılmalı."""
        mock_calc.return_value = {
            "pga": 0.15,
            "risk_seviyesi": "düşük",
            "deprem_sayisi": 2,
            "kaynak": "AFAD",
            "events": [{"magnitude": 4.1, "latitude": 41.0, "longitude": 28.0}],
            "koordinat": {"lat": 41.0, "lon": 28.0}
        }
        
        # Kadıköy statik haritada 'yüksek' düzeydir (Puan: 3)
        result = asyncio.run(deprem_analizi_async("istanbul", "Kadıköy"))
        
        self.assertEqual(result["seviye"], "yüksek")
        self.assertEqual(result["puan"], 3)
        self.assertIsNone(result["pga"]) # Karmaşık sinyali önlemek için pga None
        self.assertEqual(result["kaynak"], "Statik Harita")
        self.assertEqual(result["deprem_sayisi"], 2)
        # Events listesi dürüst bir şekilde içsözleşmeyle hedefe taşınmalı
        self.assertEqual(len(result["events"]), 1)
        self.assertEqual(result["events"][0]["magnitude"], 4.1)

    @unittest.mock.patch("services.afad_api.calculate_seismic_hazard", new_callable=unittest.mock.AsyncMock)
    def test_afad_normal_success(self, mock_calc):
        """AFAD skoru statik skordan yüksek veya eşitse AFAD kullanılmalı."""
        mock_calc.return_value = {
            "pga": 0.45,
            "risk_seviyesi": "yüksek",
            "deprem_sayisi": 1,
            "kaynak": "AFAD",
            "events": [{"magnitude": 6.1}],
            "koordinat": {"lat": 41.0, "lon": 28.0}
        }
        # Kadıköy statik haritada "yüksek"
        result = asyncio.run(deprem_analizi_async("istanbul", "Kadıköy"))
        
        self.assertEqual(result["seviye"], "yüksek")
        self.assertEqual(result["puan"], 3)
        self.assertEqual(result["pga"], 0.45)
        self.assertEqual(result["kaynak"], "AFAD")


class TestBackwardCompatibility(unittest.TestCase):
    """Mevcut sync fonksiyonların hala çalıştığını doğrula"""

    def test_sync_deprem_seviyesi_bul(self):
        seviye = deprem_seviyesi_bul("Istanbul", "Avcilar")
        self.assertEqual(seviye, "yüksek")

    def test_sync_deprem_seviyesi_puan(self):
        self.assertEqual(deprem_seviyesi_puan("yüksek"), 3)
        self.assertEqual(deprem_seviyesi_puan("orta"), 1)
        self.assertEqual(deprem_seviyesi_puan("düşük"), 0)


if __name__ == "__main__":
    unittest.main()
