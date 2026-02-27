"""Yapı Sağlığı — Risk Hesaplama API Rotası"""

from datetime import datetime

from fastapi import APIRouter
from skfuzzy import control as ctrl

from models.schemas import RiskRequest, RiskResponse
from services.fuzzy_engine import fuzzy_control_system, get_fuzzy_label, clamp
from services.corrosion import korozyon_olasiligi
from services.ml_models import concrete_model, rf_health_score, tahmin_beton_dayanimi
from services.earthquake import (
    deprem_seviyesi_bul,
    deprem_seviyesi_puan,
    tahmini_zemin_sinifi,
    deprem_analizi_async,
)
from services.structural import yapisal_skor_hesapla, yapisal_seviye_etiketi
from services.ai_comment import get_llm_comment
from services.data_service import kayit_ekle_supabase


router = APIRouter()


@router.post("/api/risk-hesapla", response_model=RiskResponse)
async def risk_hesapla(req: RiskRequest):
    # 1. Deprem ve Zemin Analizi (Hybrid: AFAD API + Statik Harita Fallback)
    deprem_result = await deprem_analizi_async(
        il=req.il,
        ilce=req.ilce,
        lat=req.latitude,
        lon=req.longitude,
    )
    deprem_seviye = deprem_result["seviye"]
    deprem_puan = deprem_result["puan"]
    pga_value = deprem_result.get("pga")  # None ise API çalışmadı
    deprem_kaynak = deprem_result.get("kaynak", "Statik Harita")

    zemin_sinifi = (
        req.zeminSinifi if req.zeminSinifi else tahmini_zemin_sinifi(req.il, req.ilce)
    )

    # Detaylara kaynak bilgisi ekle
    detay_prefix = []
    if pga_value is not None:
        detay_prefix.append(
            f"📡 AFAD Veri: PGA={pga_value:.4f}g, "
            f"{deprem_result.get('deprem_sayisi', '?')} deprem tespit edildi"
        )
    else:
        detay_prefix.append(f"📋 Veri Kaynağı: Statik Deprem Haritası")

    # 2. Yapısal Skor
    yapisal_puan, detaylar_raw = yapisal_skor_hesapla(req, zemin_sinifi)
    detaylar = detay_prefix + detaylar_raw  # AFAD bilgisini başa ekle
    toplam_yapisal_risk = yapisal_puan + deprem_puan
    yapisal_seviye = yapisal_seviye_etiketi(toplam_yapisal_risk)

    # 3. Beton Dayanımı
    basinc_dayanimi = tahmin_beton_dayanimi(
        req.ultrasonikSesHizi, req.geriSicramaSayisi
    )
    if concrete_model is None:
        detaylar.append("UYARI: Beton modeli yok, varsayılan (C25) kullanıldı.")

    # --- YÖNETMELİK: Minimum Beton Sınıfı Kontrolü (TBDY 2018 Madde 7.2.5.3) ---
    # Deprem etkisi alacak elemanlarda en düşük beton sınıfı C25 (25 MPa) olmalıdır.
    if basinc_dayanimi < 25.0:
        detaylar.append(
            f"🚨 YÖNETMELİK UYARISI: Tahmini beton dayanımı ({basinc_dayanimi:.1f} MPa) "
            f"TBDY 2018 minimum sınırının (C25 = 25 MPa) altında! "
            f"Bu bina mevcut yönetmelik şartlarını karşılamıyor."
        )
        # Yapısal risk skoruna ciddi ceza ekle
        toplam_yapisal_risk += 5
        detaylar.append("Yönetmelik altı beton nedeniyle ek risk (+5)")

    # --- Korozyon Olasılığı (ASTM C876 standardı, sürekli interpolasyon) ---
    kor_yuzde, kor_seviye, kor_ikon = korozyon_olasiligi(req.corrosion)
    detaylar.append(
        f"{kor_ikon} Korozyon Olasılığı: %{kor_yuzde} ({kor_seviye}) "
        f"[{req.corrosion:.0f} mV — ASTM C876]"
    )

    # 4. Fuzzy Logic (Şeffaf Sınırlandırma ile)
    try:
        sim = ctrl.ControlSystemSimulation(fuzzy_control_system)

        # Clamp ve Uyarı Mekanizması
        f_strength = clamp(float(basinc_dayanimi), 0.0, 80.0)
        if f_strength != float(basinc_dayanimi):
            detaylar.append(
                f"NOT: Beton dayanımı fuzzy limitine sınırlandı ({basinc_dayanimi:.1f} -> {f_strength:.1f})"
            )

        f_corrosion = clamp(float(req.corrosion), -600.0, 100.0)
        if f_corrosion != float(req.corrosion):
            detaylar.append(
                f"NOT: Korozyon fuzzy limitine sınırlandı ({req.corrosion:.0f} -> {f_corrosion:.0f})"
            )

        f_survey = clamp(float(toplam_yapisal_risk), 0.0, 50.0)
        if f_survey != float(toplam_yapisal_risk):
            detaylar.append(
                f"NOT: Yapısal risk fuzzy limitine sınırlandı ({toplam_yapisal_risk} -> {f_survey})"
            )

        sim.input["strength"] = f_strength
        sim.input["corrosion"] = f_corrosion
        sim.input["survey_risk"] = f_survey

        sim.compute()
        health_score = sim.output["health"]
    except Exception as e:
        print(f"Fuzzy hesaplama hatası: {e}")
        health_score = 50.0

    # 5. Ensemble: Fuzzy + RF (predict_proba tabanlı)
    fuzzy_raw = clamp(health_score, 0.0, 100.0)
    rf_score = rf_health_score(req, zemin_sinifi, basinc_dayanimi)
    if rf_score is not None:
        health_score = 0.6 * fuzzy_raw + 0.4 * rf_score
        detaylar.append(
            f"🤖 Ensemble: Fuzzy({fuzzy_raw:.0f}) + RF({rf_score:.0f}) → {health_score:.0f}"
        )
    else:
        health_score = fuzzy_raw
    health_score = clamp(health_score, 0.0, 100.0)
    fuzzy_label = get_fuzzy_label(health_score)

    if health_score < 45:
        genel_seviye = "Yüksek"
    elif health_score < 65:
        genel_seviye = "Orta"
    else:
        genel_seviye = "Düşük"

    # --- AI YORUM ---
    aciklama = get_llm_comment(
        skor=int(health_score),
        risk_durumu=fuzzy_label,
        beton=round(basinc_dayanimi, 1),
        korozyon=req.corrosion,
        risk_puani=int(toplam_yapisal_risk),
    )

    # Kayıt (Supabase)
    kayit_ekle_supabase(
        {
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "il": req.il,
            "ilce": req.ilce,
            "yapim_yili": req.yapimYili,
            "kat_sayisi": req.katSayisi,
            "zemin_dukkan": req.zeminDukkan,
            "bitisik_nizam": req.bitisik,
            "hasar_durumu": req.hasar,
            "kullanim_amaci": req.kullanimAmaci,
            "kisa_kolon": req.kisaKolon,
            "agir_cikma": req.agirCikma,
            "plan_tipi": req.planTipi,
            "bitisik_hiza": req.bitisikHiza,
            "zemin_sinifi": zemin_sinifi,
            "crack_puan": req.crackPuan if req.crackPuan is not None else 0,
            "deprem_seviye": deprem_seviye,
            "deprem_puan": deprem_puan,
            "yapisal_puan": yapisal_puan,
            "toplam_risk_puani": toplam_yapisal_risk,
            "yapisal_seviye": yapisal_seviye,
            "genel_seviye": genel_seviye,
            "ai_etiket": fuzzy_label,
            "ai_yorum": aciklama,
        }
    )

    return RiskResponse(
        # İnsani Yuvarlama (Round)
        healthScore=int(round(health_score)),
        genelSeviye=genel_seviye,
        aciklama=aciklama,
        depremSeviye=deprem_seviye,
        depremPuan=deprem_puan,
        yapisalSeviye=yapisal_seviye,
        yapisalPuan=yapisal_puan,
        toplamYapisalRisk=toplam_yapisal_risk,
        zeminSinifi=zemin_sinifi,
        detaylar=detaylar,
        fuzzyLabel=fuzzy_label,
        corrosion=req.corrosion,
        basincDayanimi=basinc_dayanimi,
        pga=pga_value,
        depremKaynak=deprem_kaynak,
        aiEtiket=fuzzy_label,
        aiYorum=aciklama,
    )
