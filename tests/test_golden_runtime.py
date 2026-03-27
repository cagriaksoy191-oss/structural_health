import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from main import app

client = TestClient(app)

# ---------------------------------------------------------
# GOLDEN RUNTIME TEST - EXPECTATION CONTRACT (Sabit Sözleşme)
# ---------------------------------------------------------
# Bu değerler, mevcut "v2_fuzzy27" motoru üzerinden ilk tasarımla
# ölçülerek (snapshot/baseline capture) sabitlenmiştir. 
# Test asla çalışma anında kendi baseline'ını tekrar okumaz.
# Mimari veya kural tabanı kasten değiştirilirse, bu test kasten
# kırılacaktır ve geliştiricinin bu değerleri kendinden emin olarak
# (manuel) güncellemesi gerekmektedir.
# ---------------------------------------------------------
EXPECTED_HEALTH_SCORE_A = 93  # Sağlıklı / Yeni Bina (Cap Yok)
EXPECTED_HEALTH_SCORE_B = 35  # Yalnız Zayıf Beton (TBDY)
EXPECTED_HEALTH_SCORE_C = 35  # Yalnız Aktif Korozyon (ASTM)
EXPECTED_HEALTH_SCORE_D = 13  # Dual Cap İhbar (Hem Zayıf Beton Hem Çok Kötü Korozyon + Kötü Yapı)
EXPECTED_ENGINE_VERSION = "v2_fuzzy27"
MOCK_PDF_URL = "/static/golden_mock_report.pdf"
MOCK_AI_COMMENT = "Mocked Golden AI Response"

# ---------------------------------------------------------
# CANONICAL PAYLOADS
# ---------------------------------------------------------

BASE_PAYLOAD_A = {
    "il": "Istanbul",
    "ilce": "Kadikoy",
    "yapimYili": 2020,
    "katSayisi": 3,
    "zeminDukkan": "hayir",
    "bitisik": "hayir",
    "hasar": "yok",
    "kullanimAmaci": "konut",
    "kisaKolon": "yok",
    "agirCikma": "yok",
    "planTipi": "dikdortgen",
    "bitisikHiza": "yok",
    "ultrasonikSesHizi": 40.0,
    "geriSicramaSayisi": 45.0,
    "corrosion": -100.0,
    "zeminSinifi": "Z2"
}

# ---------------------------------------------------------
# MOCK FIXTURES (routes.risk.* Surface)
# ---------------------------------------------------------

@pytest.fixture
def mock_external_services():
    """Route düzeyinde (routes.risk.*) en güvenli patch yüzeyleri"""
    with patch("routes.risk.kayit_ekle_supabase") as m_sb, \
         patch("routes.risk.kayit_ekle_csv") as m_csv, \
         patch("routes.risk.get_llm_comment") as m_llm, \
         patch("routes.risk.create_ai_pdf_report") as m_pdf, \
         patch("routes.risk.deprem_analizi_async") as m_deprem:
         
        m_sb.return_value = {"id": "mock_id"}
        m_csv.return_value = True
        m_llm.return_value = MOCK_AI_COMMENT
        m_pdf.return_value = MOCK_PDF_URL
        # Default mock for earthquake - simulated successful AFAD response
        m_deprem.return_value = {
            "seviye": "Düsük",
            "puan": 10,
            "zemin_sinifi": "Z2",
            "pga": 0.15,
            "kaynak": "AFAD"
        }
        
        yield {
            "supabase": m_sb,
            "csv": m_csv,
            "llm": m_llm,
            "pdf": m_pdf,
            "deprem": m_deprem
        }

# ---------------------------------------------------------
# TESTS
# ---------------------------------------------------------

def test_vaka_a_saglikli_yeni_bina(mock_external_services):
    """
    Vaka A: Sağlıklı, yeni bina. Cap tetiklenmemeli.
    Skor EXPECTED_HEALTH_SCORE_A (93) dar toleranslı olmalıdır.
    """
    # AFAD -> default successful (AFAD_SUCCESS) in fixture
    response = client.post("/api/risk-hesapla", json=BASE_PAYLOAD_A)
    assert response.status_code == 200
    data = response.json()
    
    # 1. healthScore Check (Narrow-band for dynamic score)
    assert data["healthScore"] == pytest.approx(EXPECTED_HEALTH_SCORE_A, abs=2)
    
    # 2. engineVersion Exact Check
    assert data["engineVersion"] == EXPECTED_ENGINE_VERSION
    
    # 3. Persistence propagation (AI and PDF contract)
    assert data["aiYorum"] == MOCK_AI_COMMENT
    assert data["pdfDownloadUrl"] == MOCK_PDF_URL
    assert data["depremKaynak"] == "AFAD"  # As mock returned 'AFAD'
    
    # 4. TRACE checks (Presence only for fired_rules, no caps)
    trace = data.get("fuzzyTrace")
    assert trace is not None
    assert isinstance(trace["fired_rules"], list)
    assert len(trace["fired_rules"]) > 0
    # Sağlıklı binada cap olmamalı
    assert len(trace.get("applied_caps", [])) == 0


def test_vaka_b_tbdy_cap_presence(mock_external_services):
    """
    Vaka B: Yalnızca TBDY koşulunun (Beton < 25) karşılandığı uç durum.
    Ham skor halihazırda 40'ın altında olduğu için (35) matematiksel clamp etkisi gözlenmez.
    Test, engine contract doğruluğunu ve cap'in trace'te (presence) var olduğunu kanıtlar.
    """
    payload = BASE_PAYLOAD_A.copy()
    payload["ultrasonikSesHizi"] = 4.0
    payload["geriSicramaSayisi"] = 10.0  # Force < 25MPa concrete
    
    response = client.post("/api/risk-hesapla", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # Exact skor kontrolü (Ham skorun deterministik sınırı)
    assert data["healthScore"] == EXPECTED_HEALTH_SCORE_B
    
    # TRACE Applied Caps Presence Check
    applied_caps = data["fuzzyTrace"]["applied_caps"]
    # TBDY_ONELEME_CAP isminin exact varlığı
    assert any(cap["cap_name"] == "TBDY_ONELEME_CAP" for cap in applied_caps)


def test_vaka_c_astm_cap_presence(mock_external_services):
    """
    Vaka C: Yalnızca ASTM korozyon limitinin ihlal edildiği durum.
    Ham skor 40'ın altında olduğu için (35) clamp etkisi oluşmaz, trace presence denetlenir.
    """
    payload = BASE_PAYLOAD_A.copy()
    payload["corrosion"] = -450.0  # Aktif korozyon (< -350mV limiti)
    
    response = client.post("/api/risk-hesapla", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["healthScore"] == EXPECTED_HEALTH_SCORE_C
    
    # TRACE Applied Caps Presence Check
    applied_caps = data["fuzzyTrace"]["applied_caps"]
    assert any(cap["cap_name"] == "ASTM_C876_CAP" for cap in applied_caps)


def test_vaka_d_dual_cap_presence(mock_external_services):
    """
    Vaka D: Hem TBDY (Beton) hem ASTM (Korozyon) ihlali + Kötü yapı parametreleri.
    Tam çöküş vakası, skor zaten 25 cap limitinin altındadır (13).
    Dual cap trace varlığı (presence) doğrulanır.
    """
    payload = BASE_PAYLOAD_A.copy()
    payload["ultrasonikSesHizi"] = 4.0
    payload["geriSicramaSayisi"] = 10.0
    payload["corrosion"] = -450.0
    payload["katSayisi"] = 5
    payload["zeminDukkan"] = "evet"
    payload["kisaKolon"] = "var"
    
    response = client.post("/api/risk-hesapla", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # Exact score check for Dual Cap trace scenario
    assert data["healthScore"] == EXPECTED_HEALTH_SCORE_D
    
    # Cift cap tetiklenmis olmali
    applied_caps = data["fuzzyTrace"]["applied_caps"]
    
    # DUAL_CAP varliği string matcher exact-subset
    cap_names = [c["cap_name"] for c in applied_caps]
    assert "CAP_DUAL" in cap_names


def test_vaka_e1_afad_basari(mock_external_services):
    """
    Vaka E1: Hibrit senaryoda AFAD API basarisi. Vaka A Payload'inin +lat/lon hali.
    Mock default oldugundan source "AFAD" donecektir.
    """
    payload = BASE_PAYLOAD_A.copy()
    payload["latitude"] = 41.0
    payload["longitude"] = 29.0
    
    response = client.post("/api/risk-hesapla", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # Exact check
    assert data["depremKaynak"] == "AFAD"
    assert data["pga"] == 0.15     # from our external mock
    
    # Keyword/Substring kontrol: Detaylarda AFAD tasinmis mi
    assert any("AFAD Veri" in d for d in data["detaylar"])


def test_vaka_e2_statik_fallback(mock_external_services):
    """
    Vaka E2: Hibrit senaryoda AFAD API çökmesi sonucu fallback.
    Mock hata firlatir veya Statik Harita döner.
    """
    # Override the mock fixture behavior specifically for this test
    mock_external_services["deprem"].return_value = {
        "seviye": "Düşük",
        "puan": 10,
        "zemin_sinifi": "Z2",
        "pga": None,
        "kaynak": "Statik Harita"
    }
    
    payload = BASE_PAYLOAD_A.copy()
    payload["latitude"] = 41.0
    payload["longitude"] = 29.0
    
    response = client.post("/api/risk-hesapla", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # Fallback status propagated gracefully without failing
    assert data["healthScore"] == pytest.approx(EXPECTED_HEALTH_SCORE_A, abs=2)
    assert data["depremKaynak"] == "Statik Harita"
    assert data["pga"] is None
