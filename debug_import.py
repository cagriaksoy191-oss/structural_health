import sys
import traceback

print(f"Python Executable: {sys.executable}")
print(f"Python Version: {sys.version}")

try:
    print("Attempting to import main...")

    print("[BASARILI] Success: main imported")
except Exception:
    print("[HATA] Error importing main:")
    traceback.print_exc()
