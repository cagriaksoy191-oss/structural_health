# -*- coding: utf-8 -*-
"""
V12 Titanium - CI/CD Health Check Script
=========================================
GPU, CUDA, gerekli kutuphaneler ve Ollama baglantisini kontrol eder.
CI/CD pipeline icinde calistirilmak uzere tasarlanmistir.
"""

import sys
import os

# Windows encoding sorunu icin
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def check_gpu():
    """CUDA ve GPU durumunu kontrol eder."""
    print("\n[GPU & CUDA Kontrolu]")
    print("-" * 40)

    try:
        import torch

        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            cuda_version = torch.version.cuda
            gpu_count = torch.cuda.device_count()

            print(f"   [OK] GPU Aktif: {gpu_name}")
            print(f"   [OK] CUDA Version: {cuda_version}")
            print(f"   [OK] GPU Sayisi: {gpu_count}")

            # VRAM bilgisi
            total_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            print(f"   [OK] VRAM: {total_memory:.1f} GB")
            return True
        else:
            print("   [WARN] GPU bulunamadi (CPU modunda calisilacak)")
            print("   [INFO] PyTorch yuklu ama CUDA destegi yok")
            return True  # CPU modunda da calisabilir

    except ImportError:
        print("   [FAIL] PyTorch yuklu degil!")
        return False


def check_libraries():
    """Gerekli kutuphanelerin yuklu oldugunu kontrol eder."""
    print("\n[Kutuphane Kontrolu]")
    print("-" * 40)

    required = [
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("sklearn", "scikit-learn"),
        ("joblib", "joblib"),
        ("torch", "torch"),
        ("fastapi", "fastapi"),
        ("skfuzzy", "scikit-fuzzy"),
        ("pydantic", "pydantic"),
        ("requests", "requests"),
        ("supabase", "supabase"),
        ("dotenv", "python-dotenv"),
    ]

    all_ok = True
    for module_name, pip_name in required:
        try:
            module = __import__(module_name)
            version = getattr(module, "__version__", "N/A")
            print(f"   [OK] {pip_name} ({version})")
        except ImportError:
            print(f"   [FAIL] {pip_name} eksik!")
            all_ok = False

    return all_ok


def check_models():
    """Model dosyalarinin varligini kontrol eder."""
    print("\n[Model Dosyalari Kontrolu]")
    print("-" * 40)

    # Script'in bulundugu dizinin parent'i (proje koku)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    models = [
        ("concrete_model.joblib", "Beton Dayanim Modeli (RF)"),
        ("anfis_model_agirliklari.pth", "ANFIS Agirliklari"),
    ]

    all_found = True
    for filename, description in models:
        filepath = os.path.join(project_root, filename)
        if os.path.exists(filepath):
            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            print(f"   [OK] {description}: {size_mb:.2f} MB")
        else:
            print(f"   [WARN] {description}: Bulunamadi ({filename})")
            # Model yoksa uyari ver ama hata verme (manuel yonetim)

    return True  # Manuel yonetim oldugu icin her zaman True


def check_ollama():
    """Ollama API baglantisini kontrol eder."""
    print("\n[Ollama LLM Baglanti Kontrolu]")
    print("-" * 40)

    try:
        import requests

        # Environment variable veya default URL
        ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434")

        # Ollama health endpoint
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)

        if response.status_code == 200:
            data = response.json()
            models = data.get("models", [])
            print(f"   [OK] Ollama baglantisi basarili ({ollama_url})")
            print(f"   [OK] Yuklu model sayisi: {len(models)}")

            # Qwen modelini ara
            qwen_found = any("qwen" in m.get("name", "").lower() for m in models)
            if qwen_found:
                print("   [OK] Qwen modeli mevcut")
            else:
                print(
                    "   [WARN] Qwen modeli bulunamadi (diger modeller kullanilabilir)"
                )

            return True
        else:
            print(f"   [WARN] Ollama yanit verdi ama hata kodu: {response.status_code}")
            return True  # Baglanti var, sadece uyari

    except Exception:
        print(f"   [WARN] Ollama servisi calismiyor veya erisilemiyorr")
        print("   [INFO] Ollama olmadan da sistem calisabilir (AI yorumu devre disi)")
        return True  # Ollama opsiyonel


def main():
    """Ana health check fonksiyonu."""
    print("=" * 50)
    print("   V12 Titanium - System Health Check")
    print("   CI/CD Pipeline Dogrulama")
    print("=" * 50)

    # Tum kontrolleri calistir
    libs_ok = check_libraries()
    gpu_ok = check_gpu()
    models_ok = check_models()
    ollama_ok = check_ollama()

    # Sonuc ozeti
    print("\n" + "=" * 50)
    print("   SONUC OZETI")
    print("=" * 50)

    results = [
        ("Kutuphaneler", libs_ok),
        ("GPU/CUDA", gpu_ok),
        ("Model Dosyalari", models_ok),
        ("Ollama LLM", ollama_ok),
    ]

    for name, status in results:
        icon = "[OK]" if status else "[FAIL]"
        print(f"   {icon} {name}")

    print("=" * 50)

    # Kritik kontroller (libs ve gpu)
    if libs_ok and gpu_ok:
        print("\n>>> TUM KRITIK KONTROLLER BASARILI!")
        print("    V12 Titanium sistemi calismaya hazir.\n")
        sys.exit(0)
    else:
        print("\n>>> KRITIK KONTROLLER BASARISIZ!")
        print("    Lutfen eksik bagimliliklari yukleyin.\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
