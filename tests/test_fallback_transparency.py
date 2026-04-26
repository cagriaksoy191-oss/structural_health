"""Fallback Transparency — Şeffaflık doğrulama testleri.

Her kritik fallback senaryosunda API response'un dürüst ve tutarlı olduğunu doğrular.
Dış bağımlılıklar (Ollama, Supabase, AFAD, PDF) monkeypatch ile izole edilmiştir.
"""

import sys
import os

# Proje kökünü path'e ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient


# ---------- Ortak Payload ----------
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


# ---------- Base Mock Fixture ----------
@pytest.fixture(autouse=True)
def mock_externals(monkeypatch):
    """Tüm dış bağımlılıkları izole et."""
    # Supabase — kayıt çağrısını no-op yap
    monkeypatch.setattr("services.data_service.supabase", None)

    # CSV write — gerçek dosya oluşturmasın
    monkeypatch.setattr(
        "services.data_service.DATA_FILE",
        MagicMock(exists=lambda: False, stat=lambda: MagicMock(st_size=0)),
    )

    # Ollama LLM — routes.risk'teki imported referansı patchle
    monkeypatch.setattr(
        "routes.risk.get_llm_comment",
        lambda **kwargs: "Mock AI yorum — test amaçlı.",
    )

    # PDF — routes.risk'teki imported referansı patchle
    monkeypatch.setattr(
        "routes.risk.create_ai_pdf_report",
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

    monkeypatch.setattr("routes.risk.deprem_analizi_async", mock_deprem)


@pytest.fixture
def client():
    """FastAPI test client."""
    from routes.risk import router
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


# ==========================================================
#  F1 — Fuzzy Engine Exception Transparency
# ==========================================================

class TestFuzzyFallback:
    """compute_health_v2 exception alırsa: 200 + uyarı + LLM skip."""

    def test_fuzzy_exception_returns_200_with_warning(self, client, monkeypatch):
        """Fuzzy exception → 200 + detaylarda motor hatası uyarısı."""
        monkeypatch.setattr(
            "routes.risk.compute_health_v2",
            MagicMock(side_effect=RuntimeError("test fuzzy crash")),
        )
        resp = client.post("/api/risk-hesapla", json=VALID_PAYLOAD)
        assert resp.status_code == 200
        data = resp.json()
        uyari_var = any("hesaplama motorunda hata" in d for d in data["detaylar"])
        assert uyari_var, f"Motor hata uyarısı detaylarda yok: {data['detaylar']}"

    def test_fuzzy_exception_health_score_is_50(self, client, monkeypatch):
        """Fuzzy exception → healthScore == 50."""
        monkeypatch.setattr(
            "routes.risk.compute_health_v2",
            MagicMock(side_effect=RuntimeError("test")),
        )
        resp = client.post("/api/risk-hesapla", json=VALID_PAYLOAD)
        data = resp.json()
        assert data["healthScore"] == 50

    def test_fuzzy_fallback_skips_llm(self, client, monkeypatch):
        """Fuzzy fallback → LLM çağrılmamalı, aciklama sabit metin olmalı."""
        mock_llm = MagicMock(return_value="Bu metin görünmemeli.")
        # routes.risk namespace'indeki referansı patchle (imported by name)
        monkeypatch.setattr("routes.risk.get_llm_comment", mock_llm)
        monkeypatch.setattr(
            "routes.risk.compute_health_v2",
            MagicMock(side_effect=RuntimeError("test")),
        )
        resp = client.post("/api/risk-hesapla", json=VALID_PAYLOAD)
        data = resp.json()
        # LLM çağrılmamış olmalı
        mock_llm.assert_not_called()
        # Sabit fallback metni olmalı
        assert "varsayılan modda" in data["aciklama"], (
            f"Fallback metni bekleniyor: {data['aciklama']}"
        )

    def test_fuzzy_fallback_aciklama_not_empty(self, client, monkeypatch):
        """Fuzzy fallback → aciklama boş veya None olmamalı."""
        monkeypatch.setattr(
            "routes.risk.compute_health_v2",
            MagicMock(side_effect=RuntimeError("test")),
        )
        resp = client.post("/api/risk-hesapla", json=VALID_PAYLOAD)
        data = resp.json()
        assert data["aciklama"] is not None
        assert len(data["aciklama"]) > 20, "Fallback metni çok kısa"

    def test_fuzzy_trace_has_sanitized_fallback(self, client, monkeypatch):
        """Fuzzy fallback → fuzzyTrace içinde sanitize fallback alanları."""
        monkeypatch.setattr(
            "routes.risk.compute_health_v2",
            MagicMock(side_effect=RuntimeError("secret internal error")),
        )
        resp = client.post("/api/risk-hesapla", json=VALID_PAYLOAD)
        data = resp.json()
        trace = data["fuzzyTrace"]
        assert trace["fallback"] is True
        assert trace["fallback_code"] == "FUZZY_ENGINE_ERROR"
        assert "varsayilan modda" in trace["fallback_message"]
        # Ham exception stringi response'ta OLMAMALI
        assert "secret internal error" not in str(trace)


# ==========================================================
#  F3 — Beton Predict Fallback Transparency
# ==========================================================

class TestBetonFallback:
    """Beton predict fail → detaylarda uyarı."""

    def test_concrete_predict_fail_shows_warning(self, client, monkeypatch):
        """Beton predict exception → detaylarda beton fallback uyarısı."""
        # Model var ama predict patlar
        mock_model = MagicMock()
        mock_model.predict = MagicMock(side_effect=ValueError("bad input"))
        monkeypatch.setattr("services.ml_models.concrete_model", mock_model)
        resp = client.post("/api/risk-hesapla", json=VALID_PAYLOAD)
        data = resp.json()
        assert resp.status_code == 200
        beton_uyari = any("Beton" in d and "varsayılan" in d for d in data["detaylar"])
        assert beton_uyari, f"Beton fallback uyarısı yok: {data['detaylar']}"


# ==========================================================
#  F8 — PDF Exception → 200 + null URL
# ==========================================================

class TestPdfFallback:
    """PDF üretimi patlarsa: ana response korunmalı, pdfDownloadUrl=null."""

    def test_pdf_fail_returns_200_with_null_url(self, client, monkeypatch):
        """PDF exception → 200 + pdfDownloadUrl is None + detaylarda uyarı."""
        monkeypatch.setattr(
            "routes.risk.create_ai_pdf_report",
            MagicMock(side_effect=Exception("font missing")),
        )
        resp = client.post("/api/risk-hesapla", json=VALID_PAYLOAD)
        assert resp.status_code == 200
        data = resp.json()
        assert data["pdfDownloadUrl"] is None
        pdf_uyari = any("PDF" in d for d in data["detaylar"])
        assert pdf_uyari, f"PDF hata uyarısı detaylarda yok: {data['detaylar']}"

    def test_pdf_fail_analysis_intact(self, client, monkeypatch):
        """PDF fail → healthScore, fuzzyLabel, depremSeviye normal olmalı."""
        monkeypatch.setattr(
            "routes.risk.create_ai_pdf_report",
            MagicMock(side_effect=Exception("disk full")),
        )
        resp = client.post("/api/risk-hesapla", json=VALID_PAYLOAD)
        data = resp.json()
        assert isinstance(data["healthScore"], int)
        assert data["healthScore"] > 0
        assert data["fuzzyLabel"] is not None
        assert data["depremSeviye"] is not None


# ==========================================================
#  F5 — Ollama Fail → Clean Message
# ==========================================================

class TestOllamaFallback:
    """Ollama fail → sanitize Türkçe mesaj, exception leak yok."""

    def test_ollama_fail_returns_clean_message(self, client, monkeypatch):
        """Ollama unavailable → sanitize Türkçe metin."""
        # routes.risk namespace'indeki referansı patchle
        monkeypatch.setattr(
            "routes.risk.get_llm_comment",
            lambda **kwargs: (
                "Yapay zeka yorum servisi su anda erisilemiyor. "
                "Analiz sonuclari gecerlidir; uzman yorumu icin lutfen tekrar deneyin."
            ),
        )
        resp = client.post("/api/risk-hesapla", json=VALID_PAYLOAD)
        data = resp.json()
        assert "Connection" not in data["aciklama"]
        assert "Errno" not in data["aciklama"]
        assert "Exception" not in data["aciklama"]
        assert len(data["aciklama"]) > 10


# ==========================================================
#  F6 — Supabase Fail → No Response Noise
# ==========================================================

class TestSupabaseFallback:
    """Supabase fail → response'a gürültü girmesin."""

    def test_supabase_fail_no_detaylar_noise(self, client, monkeypatch):
        """Supabase exception → detaylarda Supabase ile ilgili uyarı YOK."""
        # Supabase: mock client ile insert exception'ı simüle et
        mock_sb = MagicMock()
        mock_sb.table.return_value.insert.return_value.execute.side_effect = Exception("db error")
        monkeypatch.setattr("services.data_service.supabase", mock_sb)

        # CSV: DATA_FILE.exists() exception ile CSV yazma hatasını simüle et
        mock_file = MagicMock()
        mock_file.exists.side_effect = Exception("disk error")
        monkeypatch.setattr("services.data_service.DATA_FILE", mock_file)

        resp = client.post("/api/risk-hesapla", json=VALID_PAYLOAD)
        assert resp.status_code == 200
        data = resp.json()
        # Detaylarda Supabase veya CSV kelimesi olmamalı
        for d in data["detaylar"]:
            assert "Supabase" not in d, f"Supabase gürültüsü detaylarda: {d}"
            assert "CSV" not in d, f"CSV gürültüsü detaylarda: {d}"


# ==========================================================
#  Fuzzy Fallback → phase2_advice Mixed Signal
# ==========================================================

class TestFuzzyFallbackPhase2:
    """Fuzzy fallback varken PDF/phase2_advice sahte 'Orta risk' taşımamalı."""

    def test_fuzzy_fallback_phase2_advice_honest(self, client, monkeypatch):
        """Fuzzy fallback → PDF'e giden phase2_advice dürüst fallback metni olmalı."""
        captured = {}

        def capture_pdf(**kwargs):
            captured.update(kwargs)
            return "/static/mock_report.pdf"

        monkeypatch.setattr("routes.risk.create_ai_pdf_report", capture_pdf)
        monkeypatch.setattr(
            "routes.risk.compute_health_v2",
            MagicMock(side_effect=RuntimeError("test")),
        )
        resp = client.post("/api/risk-hesapla", json=VALID_PAYLOAD)
        assert resp.status_code == 200
        # PDF fonksiyonuna giden phase2_advice 'Orta risk' İÇERMEMELİ
        advice = captured.get("phase2_advice", "")
        assert "Orta risk" not in advice, f"Sahte Orta risk hâlâ var: {advice}"
        assert "varsayılan modda" in advice, f"Dürüst fallback metni yok: {advice}"
