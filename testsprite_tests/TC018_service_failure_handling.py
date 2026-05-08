import sys
import os
import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import httpx

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import get_llm_comment, kayit_ekle_supabase


class TestServiceFailureHandling(unittest.IsolatedAsyncioTestCase):
    @patch("httpx.AsyncClient.post")
    async def test_ollama_failure_handling(self, mock_post):
        # Simulator Ollama connection error (e.g. ConnectionRefusedError)
        mock_post.side_effect = httpx.RequestError(
            "Connection refused"
        )

        # Call the function
        comment = await get_llm_comment(
            skor=50, risk_durumu="Orta", beton=25, korozyon=-200, risk_puani=5
        )

        # Should not raise exception, but return a fallback message
        self.assertIn("Yapay Zeka Cevap Vermedi", comment)
        print(f"Ollama Failure Handled: {comment}")

    @patch(
        "main.supabase"
    )  # Mock the supabase client object directly if possible, or function that uses it
    def test_supabase_failure_handling(self, mock_supabase):
        # We need to test kayit_ekle_supabase.
        # It catches exceptions and prints them.

        # Setup mock to raise exception on insert
        mock_table = MagicMock()
        mock_insert = MagicMock()
        mock_execute = MagicMock()

        # Chain: supabase.table().insert().execute()
        # If supabase is None, it prints "Supabase istemcisi yüklü değil"
        # If supabase exists but fails:

        if mock_supabase:
            mock_supabase.table.return_value = mock_table
            mock_table.insert.return_value = mock_insert
            mock_insert.execute.side_effect = Exception("Database Connection Lost")

            # Capture stdout to verify print? Or just ensure it doesn't crash.
            try:
                kayit_ekle_supabase({"test": "data"})
            except Exception:
                self.fail("kayit_ekle_supabase raised Exception unexpectedly")
        else:
            # If main.supabase is None (becauseenv vars missing), it handles it gracefully already.
            pass


if __name__ == "__main__":
    unittest.main()
