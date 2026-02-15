import sys
import traceback

print(f"Python Executable: {sys.executable}")
print(f"Python Version: {sys.version}")

try:
    print("Attempting to import main...")
    import main

    print("✅ Success: main imported")
except Exception:
    print("❌ Error importing main:")
    traceback.print_exc()
