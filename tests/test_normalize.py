import pytest
from services.normalize import normalize_key

def test_normalize_key_none():
    assert normalize_key(None) == ""

def test_normalize_key_empty_string():
    assert normalize_key("") == ""

def test_normalize_key_whitespace():
    assert normalize_key("  istanbul  ") == "istanbul"

def test_normalize_key_turkish_chars_lowercase():
    # ğ -> g, ı -> i, ş -> s, ü -> u, ç -> c, ö -> o
    assert normalize_key("ğışüçö") == "gisuco"

def test_normalize_key_turkish_chars_uppercase():
    # Ğ -> g, İ -> i, I -> i, Ö -> o, Ş -> s, Ü -> u, Ç -> c
    assert normalize_key("ĞİIÖŞÜÇ") == "giiosuc"

def test_normalize_key_mixed_turkish_chars():
    assert normalize_key("İstanbul") == "istanbul"
    assert normalize_key("KADIKÖY") == "kadikoy"
    assert normalize_key("Beşiktaş") == "besiktas"

def test_normalize_key_spaces_and_hyphens():
    assert normalize_key("kadikoy-istanbul") == "kadikoyistanbul"
    assert normalize_key("kadikoy istanbul") == "kadikoyistanbul"

def test_normalize_key_accented_chars():
    # unicodedata.normalize("NFKD", text) should handle these
    assert normalize_key("éàë") == "eae"

def test_normalize_key_complex_input():
    assert normalize_key("  Şanlıurfa-Merkez  ") == "sanliurfamerkez"
    assert normalize_key("Küçükçekmece") == "kucukcekmece"
