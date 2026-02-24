"""Yapı Sağlığı — Türkçe Karakter Normalizasyonu"""

import unicodedata
from typing import Optional


def normalize_key(text: Optional[str]) -> str:
    """
    Türkçe karakterleri güvenli İngilizce karakterlere çevirir.
    Optional[str] tip desteği eklendi.
    """
    if not text:
        return ""

    # Türkçe Karakter Eşleşmesi
    tr_map = str.maketrans(
        {
            "ğ": "g",
            "Ğ": "g",
            "ı": "i",
            "İ": "i",
            "I": "i",
            "ö": "o",
            "Ö": "o",
            "ş": "s",
            "Ş": "s",
            "ü": "u",
            "Ü": "u",
            "ç": "c",
            "Ç": "c",
        }
    )

    text = text.strip().translate(tr_map).lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.replace(" ", "").replace("-", "")

    return text
