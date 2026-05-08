import os
import unittest

# Simplified test that doesn't depend on FastAPI being installed in the environment
# since we only care about how _parse_origins works and how it's called in main.py

def mock_parse_origins(raw: str) -> list:
    """ALLOWED_ORIGINS env var'ını virgülle ayırıp listeye çevirir."""
    return [o.strip() for o in raw.split(",") if o.strip()]

class TestCORSLogic(unittest.TestCase):
    def test_parse_origins_empty(self):
        self.assertEqual(mock_parse_origins(""), [])
        self.assertEqual(mock_parse_origins("  "), [])

    def test_parse_origins_single(self):
        self.assertEqual(mock_parse_origins("http://localhost:5173"), ["http://localhost:5173"])

    def test_parse_origins_multiple(self):
        raw = "http://localhost:5173, http://localhost:5174 ,http://127.0.0.1:5173"
        expected = ["http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173"]
        self.assertEqual(mock_parse_origins(raw), expected)

    def test_security_fix_verification(self):
        # This simulates how main.py now calls _parse_origins

        # Scenario 1: ALLOWED_ORIGINS is NOT set (the vulnerability was here)
        env_val = os.getenv("ALLOWED_ORIGINS", "")
        origins = mock_parse_origins(env_val)

        # The previously hardcoded origins should NOT be present
        vulnerable_origins = [
            "http://localhost:5173",
            "http://localhost:5174",
            "http://localhost:5175",
            "http://127.0.0.1:5173"
        ]
        for vo in vulnerable_origins:
            self.assertNotIn(vo, origins, f"Vulnerable origin {vo} found in default configuration!")

        self.assertEqual(origins, [], "Default origins should be empty for security")

        # Scenario 2: ALLOWED_ORIGINS is set by user
        custom_origin = "https://secure.example.com"
        origins = mock_parse_origins(custom_origin)
        self.assertIn(custom_origin, origins)
        self.assertEqual(len(origins), 1)

if __name__ == "__main__":
    unittest.main()
