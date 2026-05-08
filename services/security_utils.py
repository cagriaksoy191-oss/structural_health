import hashlib
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Hardcoded SHA256 hashes for critical model artifacts
# These hashes ensure that the files have not been tampered with.
EXPECTED_HASHES = {
    "concrete_model.joblib": "1887eceb08f7c09c13c12d449ef60da8d49a37eaf8437f3a78d35632a18251e0",
    "etiket_encoder.joblib": "001909da3066d6676f073c19d5cd580bae7a0a63bdbff205ced4a0bdef6cd6e9",
    "scaler_x.pkl": "3a2deeba26a594e4839031062d70eba053e40c12836371adcda5daf9c75cb3db",
    "scaler_y.pkl": "6b33500b16aa1181335d9ce6f7e8a0dae7898f77d0e81e863cfc7f413f4f1804",
    "risk_model.joblib": "UNKNOWN", # Placeholder if needed, but not found in repo
}

def verify_file_integrity(filepath: Path, expected_sha256: str = None) -> bool:
    """
    Computes the SHA256 hash of the file and compares it with the expected hash.
    If expected_sha256 is None, it looks up the filename in EXPECTED_HASHES.
    Fail-closed: Returns False if hash is unknown or does not match.
    """
    if not filepath.exists():
        logger.error(f"[HATA] Dosya bulunamadı: {filepath}")
        return False

    if expected_sha256 is None:
        expected_sha256 = EXPECTED_HASHES.get(filepath.name)
        if expected_sha256 is None or expected_sha256 == "UNKNOWN":
            logger.critical(f"[GÜVENLİK HATASI] '{filepath.name}' için beklenen hash tanımlı değil! Dosya yüklenemez.")
            return False

    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            # Read in chunks to handle large files
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)

        computed_hash = sha256_hash.hexdigest()
        if computed_hash == expected_sha256:
            return True
        else:
            logger.critical(f"[GÜVENLİK İHLALİ] '{filepath.name}' dosyası bütünlük kontrolünden geçemedi!")
            logger.critical(f"Beklenen: {expected_sha256}")
            logger.critical(f"Hesaplanan: {computed_hash}")
            return False
    except Exception as e:
        logger.error(f"[HATA] Dosya hash hesaplama hatası: {type(e).__name__}")
        return False
