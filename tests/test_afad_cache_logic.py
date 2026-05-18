import sys
from unittest.mock import MagicMock

# Global mocks for external dependencies that might be missing
# These must be set BEFORE importing the module under test
sys.modules["httpx"] = MagicMock()
sys.modules["supabase"] = MagicMock()
sys.modules["dotenv"] = MagicMock()

import unittest
import time
import os

from services.afad_api import _cache_key, cache_get, cache_set, _cache, AFAD_CACHE_TTL

class TestAFADCacheLogic(unittest.TestCase):
    def setUp(self):
        # Clear the internal cache before each test to ensure isolation
        _cache.clear()

    def test_cache_key_normalization(self):
        """_cache_key should lowercase and strip whitespace from input strings."""
        # Test case: Mixed case and leading/trailing whitespace
        key = _cache_key("  Istanbul  ", "  Kadikoy  ")
        self.assertEqual(key, "istanbul:kadikoy")

        # Test case: Purely uppercase
        key2 = _cache_key("ANKARA", "Cankaya")
        self.assertEqual(key2, "ankara:cankaya")

    def test_cache_set_stores_data(self):
        """cache_set should correctly store data in the internal dictionary with a timestamp."""
        test_data = {"pga": 0.25, "risk": "orta"}
        cache_set("izmir", "konak", test_data)

        key = "izmir:konak"
        self.assertIn(key, _cache)
        self.assertEqual(_cache[key]["data"], test_data)
        # Ensure timestamp is current (within 1 second)
        self.assertAlmostEqual(_cache[key]["timestamp"], time.time(), delta=1)

    def test_cache_get_hit(self):
        """cache_get should return the cached data when it is present and within TTL."""
        test_data = {"pga": 0.1, "risk": "dusuk"}
        cache_set("antalya", "kas", test_data)

        result = cache_get("antalya", "kas")
        self.assertEqual(result, test_data)

    def test_cache_get_miss(self):
        """cache_get should return None when the requested key is not in the cache."""
        result = cache_get("bursa", "nilufer")
        self.assertIsNone(result)

    def test_cache_get_expired(self):
        """cache_get should return None and remove the entry if the TTL has expired."""
        test_data = {"pga": 0.5, "risk": "yuksek"}
        key = "mugla:bodrum"

        # Simulate an expired entry
        # Default TTL is 3600 seconds
        expired_time = time.time() - (AFAD_CACHE_TTL + 10)

        _cache[key] = {
            "data": test_data,
            "timestamp": expired_time
        }

        # Verify it exists before get
        self.assertIn(key, _cache)

        result = cache_get("mugla", "bodrum")

        # Should return None and the entry should be deleted from cache
        self.assertIsNone(result)
        self.assertNotIn(key, _cache)

if __name__ == "__main__":
    unittest.main()
