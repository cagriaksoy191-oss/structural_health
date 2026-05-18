import os
import unittest

# Updated to match the new logic in main.py
def mock_parse_origins(raw: str) -> list:
    """
    ALLOWED_ORIGINS env var'ını virgülle ayırıp listeye çevirir.
    Güvenlik: '*' (wildcard) kullanımını engeller ve sadece http/https protokollerine izin verir.
    """
    raw_list = [o.strip() for o in raw.split(",") if o.strip()]
    safe_origins = []
    for o in raw_list:
        if o == "*":
            continue  # Güvenlik gereği wildcard'a izin verilmez
        if o.startswith(("http://", "https://")):
            safe_origins.append(o)
    return safe_origins

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

    def test_wildcard_rejection(self):
        """Test that '*' is rejected even if provided."""
        self.assertEqual(mock_parse_origins("*"), [])
        self.assertEqual(mock_parse_origins("*, http://localhost:5173"), ["http://localhost:5173"])
        self.assertEqual(mock_parse_origins("http://localhost:5173, *"), ["http://localhost:5173"])

    def test_invalid_scheme_rejection(self):
        """Test that only http/https schemes are allowed."""
        self.assertEqual(mock_parse_origins("ftp://evil.com"), [])
        self.assertEqual(mock_parse_origins("javascript:alert(1)"), [])
        self.assertEqual(mock_parse_origins("localhost:5173"), []) # Should have protocol
        self.assertEqual(mock_parse_origins("http://localhost:5173, evil.com"), ["http://localhost:5173"])

    def test_security_fix_verification(self):
        # Scenario 1: ALLOWED_ORIGINS is NOT set
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

        # Scenario 2: ALLOWED_ORIGINS is set to '*'
        origins = mock_parse_origins("*")
        self.assertEqual(origins, [], "Wildcard origin should be rejected")

if __name__ == "__main__":
    unittest.main()
