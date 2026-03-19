"""Faz 2 Regression — Route cutover doğrulama testleri.

Dış bağımlılıklar (Ollama, Supabase, AFAD, PDF) monkeypatch ile izole edilmiştir.
Deterministik ve hızlı çalışır (~1s).
"""

import sys
import os

# Proje kökünü path'e ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient


# ---------- Mock'lar ----------
# Supabase, Ollama, AFAD API, PDF üretimi — tümünü devre dışı bırak

@pytest.fixture(autouse=True)
def mock_externals(monkeypatch):
    """Tüm dış bağımlılıkları izole et."""
    # Supabase — kayıt çağrısını no-op yap
    monkeypatch.setattr(
        "services.data_service.supabase", None
    )

    # CSV write — gerçek dosya oluşturmasın
    monkeypatch.setattr(
        "services.data_service.DATA_FILE",
        MagicMock(exists=lambda: False, stat=lambda: MagicMock(st_size=0)),
    )

    # Ollama LLM — senkron fonksiyon, mock string dönsün
    monkeypatch.setattr(
        "services.ai_comment.get_llm_comment",
        lambda **kwargs: "Mock AI yorum — test amaçlı.",
    )

    # PDF — dosya üretmesin, URL dönsün
    monkeypatch.setattr(
        "services.pdf_report.create_ai_pdf_report",
        lambda **kwargs: "/static/mock_report.pdf",
    )

    # AFAD API — deprem_analizi_async'i mock async fonksiyon yap
    async def mock_deprem(**kwargs):
        return {
            "seviye": "yüksek",
            "puan": 12,
            "pga": 0.35,
            "kaynak": "Mock AFAD",
            "deprem_sayisi": 5,
            "events": [],
        }

    monkeypatch.setattr(
        "routes.risk.deprem_analizi_async",
        mock_deprem,
    )


@pytest.fixture
def client():
    """FastAPI test client."""
    # Route import (mock'lar yerleştirildikten sonra)
    from routes.risk import router
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


# ---------- Test Payload ----------
VALID_PAYLOAD = {
    "il": "Istanbul",
    "ilce": "Kadıköy",
    "yapimYili": 1995,
    "katSayisi": 5,
    "zeminDukkan": "evet",
    "bitisik": "evet",
    "hasar": "hafif",
    "kullanimAmaci": "konut",
    "kisaKolon": "var",
    "agirCikma": "buyuk",
    "planTipi": "L",
    "bitisikHiza": "farkli",
    "ultrasonikSesHizi": 3200.0,
    "geriSicramaSayisi": 28.0,
    "corrosion": -400.0,
}


# ---------- Testler ----------

class TestRouteResponse:
    """Endpoint 200 ve temel response yapısı."""

    def test_returns_200(self, client):
        resp = client.post("/api/risk-hesapla", json=VALID_PAYLOAD)
        assert resp.status_code == 200, f"Beklenen 200, gelen {resp.status_code}: {resp.text}"

    def test_engine_version_in_response(self, client):
        resp = client.post("/api/risk-hesapla", json=VALID_PAYLOAD)
        data = resp.json()
        assert "engineVersion" in data, "engineVersion response'ta yok"
        assert data["engineVersion"] == "v2_fuzzy27", f"Yanlış versiyon: {data['engineVersion']}"

    def test_fuzzy_trace_structure(self, client):
        resp = client.post("/api/risk-hesapla", json=VALID_PAYLOAD)
        data = resp.json()
        assert "fuzzyTrace" in data, "fuzzyTrace response'ta yok"

        trace = data["fuzzyTrace"]
        assert "raw_score" in trace
        assert "capped_score" in trace
        assert "fired_rules" in trace
        assert "applied_caps" in trace
        assert isinstance(trace["fired_rules"], list)
        assert isinstance(trace["applied_caps"], list)

    def test_fired_rules_have_required_fields(self, client):
        resp = client.post("/api/risk-hesapla", json=VALID_PAYLOAD)
        trace = resp.json()["fuzzyTrace"]
        if trace["fired_rules"]:
            rule = trace["fired_rules"][0]
            for key in ("id", "output", "activation", "rationale"):
                assert key in rule, f"fired_rules içinde '{key}' eksik"

    def test_applied_caps_have_required_fields(self, client):
        resp = client.post("/api/risk-hesapla", json=VALID_PAYLOAD)
        trace = resp.json()["fuzzyTrace"]
        if trace["applied_caps"]:
            cap = trace["applied_caps"][0]
            for key in ("cap_name", "effective", "original_score", "capped_score"):
                assert key in cap, f"applied_caps içinde '{key}' eksik"


class TestGuardrailDetaylar:
    """Policy cap detayları kullanıcıya dönük detaylara yansıyor mu?"""

    def test_low_concrete_guardrail_in_detaylar(self, client):
        """Düşük beton (< 25 MPa) → KRİTİK ÖN TARAMA UYARISI detaylara eklenmeli."""
        # concrete_model mock → düşük dayanım döndürsün
        payload = VALID_PAYLOAD.copy()
        payload["ultrasonikSesHizi"] = 1500.0
        payload["geriSicramaSayisi"] = 15.0
        resp = client.post("/api/risk-hesapla", json=payload)
        data = resp.json()
        detaylar_text = " ".join(data["detaylar"])
        assert "KRİTİK" in detaylar_text or "Öneri" in detaylar_text, (
            f"Guardrail uyarısı detaylarda yok: {data['detaylar']}"
        )

    def test_high_corrosion_guardrail_in_detaylar(self, client):
        """Yüksek korozyon (≤ -350 mV) → korozyon uyarısı detaylara eklenmeli."""
        payload = VALID_PAYLOAD.copy()
        payload["corrosion"] = -500.0
        payload["ultrasonikSesHizi"] = 5000.0  # yüksek beton, sadece korozyon tetiklensin
        payload["geriSicramaSayisi"] = 50.0
        resp = client.post("/api/risk-hesapla", json=payload)
        data = resp.json()
        detaylar_text = " ".join(data["detaylar"])
        assert "Öneri" in detaylar_text, (
            f"Korozyon guardrail önerisi detaylarda yok: {data['detaylar']}"
        )


class TestPersistenceConsistency:
    """Kayıt dict'i her iki storage yüzeyine tutarlı gidiyor mu?"""

    def test_record_dict_has_engine_version(self, client, monkeypatch):
        """Supabase ve CSV hattına giden dict'te engine_version var mı?"""
        captured_records = []

        original_supabase = None  # already mocked to None

        def capture_csv(record_dict):
            captured_records.append(("csv", record_dict.copy()))

        def capture_supabase(record_dict):
            captured_records.append(("supabase", record_dict.copy()))

        monkeypatch.setattr("routes.risk.kayit_ekle_csv", capture_csv)
        monkeypatch.setattr("routes.risk.kayit_ekle_supabase", capture_supabase)

        resp = client.post("/api/risk-hesapla", json=VALID_PAYLOAD)
        assert resp.status_code == 200

        # Her iki storage hattına da yazıldı mı?
        sources = [r[0] for r in captured_records]
        assert "csv" in sources, "CSV hattına kayıt yazılmadı"
        assert "supabase" in sources, "Supabase hattına kayıt yazılmadı"

        # Aynı dict mi? (engine_version kontrolü)
        for source, record in captured_records:
            assert "engine_version" in record, f"{source}: engine_version yok"
            assert record["engine_version"] == "v2_fuzzy27", (
                f"{source}: yanlış engine_version: {record['engine_version']}"
            )

        # İki dict birebir aynı mı?
        csv_record = [r[1] for r in captured_records if r[0] == "csv"][0]
        supabase_record = [r[1] for r in captured_records if r[0] == "supabase"][0]
        assert csv_record == supabase_record, "CSV ve Supabase dict'leri farklı!"


class TestPdfAndMisc:
    """PDF URL ve diğer response alanları."""

    def test_pdf_url_in_response(self, client):
        resp = client.post("/api/risk-hesapla", json=VALID_PAYLOAD)
        data = resp.json()
        assert "pdfDownloadUrl" in data
        assert data["pdfDownloadUrl"] is not None
        assert data["pdfDownloadUrl"].endswith(".pdf")

    def test_health_score_is_integer(self, client):
        resp = client.post("/api/risk-hesapla", json=VALID_PAYLOAD)
        data = resp.json()
        assert isinstance(data["healthScore"], int)

    def test_genel_seviye_valid(self, client):
        resp = client.post("/api/risk-hesapla", json=VALID_PAYLOAD)
        data = resp.json()
        assert data["genelSeviye"] in ("Yüksek", "Orta", "Düşük")


# ---------- Standalone runner ----------
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
