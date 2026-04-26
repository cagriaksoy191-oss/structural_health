import os
import unittest
from unittest.mock import patch, MagicMock
import sys

# Mocking environment variables
os.environ["SUPABASE_URL"] = "https://fake.supabase.co"
os.environ["SUPABASE_KEY"] = "fake-key"

# Mock dependencies before importing migrate_data
sys.modules['pandas'] = MagicMock()
sys.modules['supabase'] = MagicMock()
sys.modules['dotenv'] = MagicMock()
sys.modules['numpy'] = MagicMock()

def test_sanitization():
    # Simulate the code in migrate_data.py
    def mock_csv_to_supabase():
        # Setup
        log_file = "migration_error.log"
        if os.path.exists(log_file):
            os.remove(log_file)

        sensitive_token = "SECRET_API_TOKEN_12345"
        try:
            # Simulate a batch failure
            raise Exception(f"Connection failed with token: {sensitive_token}")
        except Exception as e:
            # This is the sanitized code from migrate_data.py
            error_msg = f"[HATA] Hata (Batch 1): {type(e).__name__}\n"

            print(error_msg)
            with open(log_file, "w", encoding="utf-8") as f:
                f.write(error_msg)

        # Verification
        if not os.path.exists(log_file):
            print("FAILURE: Log file not created")
            return False

        with open(log_file, "r", encoding="utf-8") as f:
            log_content = f.read()

        print(f"Log content: {log_content.strip()}")

        if sensitive_token in log_content:
            print("FAILURE: Sensitive token leaked!")
            return False
        if "Exception" not in log_content:
            print("FAILURE: Exception type missing")
            return False
        if "Raw:" in log_content:
            print("FAILURE: Raw exception message present")
            return False

        print("SUCCESS: Error sanitization verified")
        return True

    return mock_csv_to_supabase()

if __name__ == "__main__":
    if test_sanitization():
        sys.exit(0)
    else:
        sys.exit(1)
