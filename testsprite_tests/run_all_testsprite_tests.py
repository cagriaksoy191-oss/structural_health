import unittest
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def run_all_tests():
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern="TC*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if result.wasSuccessful():
        print("\n" + "=" * 60)
        print(
            f"[BASARILI]  TUM TESTSPRITE TESTLERI BASARIYLA GECTI ({result.testsRun} TEST)"
        )
        print("=" * 60 + "\n")
        return 0
    else:
        print("\n" + "=" * 60)
        print(
            f"[HATA]  BAZI TESTLER BASARISIZ OLDU ({len(result.failures)} HATA, {len(result.errors)} KRITIK HATA)"
        )
        return 1


if __name__ == "__main__":
    exit(run_all_tests())
