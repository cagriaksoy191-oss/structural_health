"""Yapı Sağlığı — Risk Hesaplama API Rotası (v2_fuzzy27)"""

import asyncio
import logging
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks

logger = logging.getLogger(__name__)

from models.schemas import RiskRequest, RiskResponse
from services.fuzzy_engine import (
    compute_health_v2,
    get_fuzzy_label,
    clamp,
    ENGINE_VERSION,
)
from services.corrosion import korozyon_olasiligi
from services.ml_models import tahmin_beton_dayanimi
from services.earthquake import (
    deprem_seviyesi_bul,
    deprem_seviyesi_puan,
    tahmini_zemin_sinifi,
    deprem_analizi_async,
)
from services.structural import yapisal_skor_hesapla, yapisal_seviye_etiketi
from services.ai_comment import get_llm_comment
from services.data_service import kayit_ekle_supabase, kayit_ekle_csv
from services.pdf_report import create_ai_pdf_report


router = APIRouter()


@router.post("/api/risk-hesapla", response_model=RiskResponse)
async def risk_hesapla(req: RiskRequest, background_tasks: BackgroundTasks):
    # 1. Deprem ve Zemin Analizi (Hybrid: AFAD API + Statik Harita Fallback)
    deprem_result = await deprem_analizi_async(
        il=req.il,
        ilce=req.ilce,
        lat=req.latitude,
        lon=req.longitude,
    )
    deprem_seviye = deprem_result["seviye"]
    deprem_puan = deprem_result["puan"]
    pga_value = deprem_result.get("pga")  # None ise API çalışmadı veya statik fallback uygulandı
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
    basinc_dayanimi, beton_fallback = tahmin_beton_dayanimi(
        req.ultrasonikSesHizi, req.geriSicramaSayisi
    )
    if beton_fallback:
        detaylar.append("⚠️ UYARI: Beton dayanımı tahmin edilemedi; varsayılan (C25 = 25.0 MPa) kullanıldı.")

    # --- Korozyon Olasılığı (ASTM C876 standardı, sürekli interpolasyon) ---
    kor_yuzde, kor_seviye, kor_ikon = korozyon_olasiligi(req.corrosion)
    detaylar.append(
        f"{kor_ikon} Korozyon Olasılığı: %{kor_yuzde} ({kor_seviye}) "
        f"[{req.corrosion:.0f} mV — ASTM C876]"
    )

    # ==================================================================
    #  4. v2 FUZZY + POLICY LAYER (compute_health_v2)
    #  Ensemble kaldırıldı. Karar motoru: %100 Fuzzy + Policy Layer.
    # ==================================================================
    _fuzzy_fallback = False
    try:
        v2_result = compute_health_v2(
            strength_val=float(basinc_dayanimi),
            corrosion_val=float(req.corrosion),
            survey_val=float(toplam_yapisal_risk),
            basinc_dayanimi=float(basinc_dayanimi),
        )

        health_score = v2_result["capped_score"]
        fuzzy_label = v2_result["label"]
        fired_rules = v2_result["fired_rules"]
        applied_caps = v2_result["applied_caps"]
        raw_score = v2_result["raw_score"]

    except Exception as e:
        logger.error("Fuzzy v2 hesaplama hatasi: %s", type(e).__name__)
        health_score = 50.0
        fuzzy_label = get_fuzzy_label(50.0)
        fired_rules = []
        applied_caps = []
        raw_score = 50.0
        _fuzzy_fallback = True
        detaylar.append(
            "⚠️ UYARI: Yapı sağlığı hesaplama motorunda hata oluştu; "
            "gösterilen skor tahminidir. Lütfen sonuçları uzman ile doğrulayın."
        )

    # --- Policy Cap Detayları → kullanıcıya dönük uyarılar ---
    for cap in applied_caps:
        # Guardrail eşleşti → kullanıcı bilgilendirilmeli (effective olsa da olmasa da)
        if cap["cap_name"] == "CAP_DUAL":
            detaylar.append(
                f"🚨 KRİTİK ÖN TARAMA UYARISI: {cap['reason']}"
            )
            detaylar.append(f"📋 Öneri: {cap['recommendation']}")
        elif cap["cap_name"] == "TBDY_ONELEME_CAP":
            detaylar.append(
                f"🚨 KRİTİK ÖN TARAMA UYARISI: {cap['reason']}"
            )
            detaylar.append(f"📋 Öneri: {cap['recommendation']}")
        elif cap["cap_name"] == "ASTM_C876_CAP":
            detaylar.append(
                f"🚨 {cap['reason']}"
            )
            detaylar.append(f"📋 Öneri: {cap['recommendation']}")

        if cap.get("effective"):
            detaylar.append(
                f"⚠️ Skor sınırlandırıldı: {cap['original_score']:.0f} → {cap['capped_score']:.0f}"
            )

    # --- Explainability: Top-N Kurallar (teknik detay) ---
    if fired_rules:
        top_rule = fired_rules[0]
        detaylar.append(
            f"🔍 Ana kural: {top_rule['id']} ({top_rule['output']}) "
            f"— {top_rule['rationale']}"
        )

    # genel seviye belirleme
    if health_score < 45:
        genel_seviye = "Yüksek"
    elif health_score < 65:
        genel_seviye = "Orta"
    else:
        genel_seviye = "Düşük"

    # AI YORUM Oncesi BKS, H_N, DTS, BYS, Deprem Siniflari hesaplamalari
    amaci_lower = req.kullanimAmaci.lower()
    if "hastane" in amaci_lower or "okul" in amaci_lower:
        bks = 1
        i_kats = 1.5
    elif "isyeri" in amaci_lower or "sanayi" in amaci_lower:
        bks = 2
        i_kats = 1.2
    else:
        bks = 3
        i_kats = 1.0

    bina_turu = "Yeni Yapilacak Bina" if req.yapimYili >= 2019 else "Mevcut Bina"

    h_n = 0
    if req.zeminDukkan == "evet":
        h_n += 4.5 + (req.katSayisi - 1) * 3.5
    elif bks == 2:
        h_n += req.katSayisi * 3.8
    else:
        h_n += req.katSayisi * 3.5

    if pga_value is not None:
        if pga_value >= 0.40: dts = "1a" if bks == 1 else "1"
        elif pga_value >= 0.30: dts = "2a" if bks == 1 else "2"
        elif pga_value >= 0.20: dts = "3a" if bks == 1 else "3"
        else: dts = "4a" if bks == 1 else "4"
    else:
        dts = "Bilinmiyor"

    if h_n > 70: bys = "BYS 1"
    elif h_n > 56: bys = "BYS 2"
    elif h_n > 42: bys = "BYS 3"
    elif h_n > 28: bys = "BYS 4"
    elif h_n > 17.5: bys = "BYS 5"
    elif h_n > 10.5: bys = "BYS 6"
    else: bys = "BYS 7" 

    counts = {"DD-1": 0, "DD-2": 0, "DD-3": 0, "DD-4": 0}
    events = deprem_result.get("events", [])
    for d in events:
        try:
            mag = float(d.get('magnitude', d.get('mag', 0)))
            if mag >= 7.5: counts["DD-1"] += 1
            elif 6.5 <= mag < 7.5: counts["DD-2"] += 1
            elif 5.0 <= mag < 6.5: counts["DD-3"] += 1
            elif mag >= 3.0: counts["DD-4"] += 1
        except: pass

    if health_score < 50:
        phase2_advice = "ACİL: Yapı risk puanı eşiğin altında. 2. Aşama Detaylı İnceleme (Karot, röntgen vb.) ŞARTTIR."
    elif health_score < 70:
        phase2_advice = "UYARI: Orta risk. 2. Aşama İnceleme Önerilir."
    else:
        phase2_advice = "Bilgi: Risk görece düşük. Ancak standart mühendis incelemesi tavsiye edilir."

    # Fuzzy fallback → phase2_advice de dürüst fallback çizgisinde olmalı
    if _fuzzy_fallback:
        phase2_advice = (
            "Hesaplama motoru geçici olarak varsayılan modda çalıştı. "
            "Gösterilen skor tahminidir. Lütfen analizi tekrar çalıştırın "
            "veya sonuçları bir uzmanla doğrulayın."
        )

    # --- Ana Risk Sürücüsü Belirleme (Sadece LLM için) ---
    if basinc_dayanimi < 25.0:
        ana_risk_kaynagi = "Düşük Beton Dayanımı (< 25 MPa)"
    elif req.corrosion <= -350.0:
        ana_risk_kaynagi = "Kritik Korozyon Seviyesi"
    elif health_score < 70:
        ana_risk_kaynagi = "Yapısal Risk Faktörleri (Genel skor düşüklüğü)"
    else:
        ana_risk_kaynagi = "Belirgin tekil bir risk tespit edilmedi"

    # --- Korozyon Metni Hazırlığı (LLM için) ---
    korozyon_metni = f"{req.corrosion:.0f} mV (%{kor_yuzde} - {kor_seviye})"

    # --- AI YORUM (Async: senkron requests.post thread'e atılıyor) ---
    if _fuzzy_fallback:
        # Fuzzy motor fallback — LLM'e fabricated 50.0 skoru göndermek yanlış güven yaratır.
        # Sabit, dürüst metin kullanılıyor.
        aciklama = (
            "Yapı sağlığı karar motoru geçici olarak varsayılan modda çalıştı. "
            "Gösterilen skor (50) tahmini bir değerdir ve güvenilir kabul edilmemelidir. "
            "Lütfen analizi tekrar çalıştırın veya sonuçları bir uzmanla doğrulayın."
        )
    else:
        aciklama = await asyncio.to_thread(
            get_llm_comment,
            skor=int(health_score),
            risk_durumu=fuzzy_label,
            beton=round(basinc_dayanimi, 1),
            korozyon_metni=korozyon_metni,
            risk_puani=int(toplam_yapisal_risk),
            dts=dts,
            bys=bys,
            phase2_advice=phase2_advice,
            ana_risk_kaynagi=ana_risk_kaynagi
        )

    pdf_params = {
        "kullanim_amaci": req.kullanimAmaci, "bks": bks, "i_katsayisi": i_kats,
        "yapim_yili": req.yapimYili, "bina_turu": bina_turu, "bys": bys, "dts": dts,
        "kat_sayisi": req.katSayisi, "h_n": round(h_n, 1), "zemin_kat_dukkan": req.zeminDukkan == "evet"
    }

    evaluations = []
    
    # 1. Yapi Yili
    if req.yapimYili < 2000:
        evaluations.append(("Eski Yapı (2000 Öncesi)", "Beton teknolojisi ve kalite kontrol standartları 1990'larda günümüzden daha düşüktür.", "+15 Puan"))
    else:
        evaluations.append(("Yeni/Yakın Zamanlı Yapı", "Güncel yönetmeliklere daha uygun malzeme ve işçiliği gösterir.", "0 Puan"))
        
    # 2. Kat Sayisi
    if req.katSayisi >= 5:
        evaluations.append((f"Orta-Yüksek Bina ({req.katSayisi} Kat)", "Yükseklik arttıkça sismik yanıt ve deformasyon riski yükselir.", "+6 Puan"))
        
    # 3. Zemin Dukkan
    if req.zeminDukkan == "evet":
        evaluations.append(("Zayıf Kat Riski (Zemin Dükkan)", "Dükkan katı, taşıyıcı sistemden izole edilmemiş; çökme, kayma ve aşırı deformasyona yol açabilir.", "+18 Puan"))

    # 4. Cikma Durumu
    if req.agirCikma == "buyuk":
        evaluations.append(("Ağır Çıkma", "Üst kısımlarda ek yük oluşturur ve kesme kuvvetlerini artırır.", "+10 Puan"))
    elif req.agirCikma == "hafif":
        evaluations.append(("Hafif Çıkma", "Çatı ve dış cephe elemanları hafif; ancak bu faktör tek başına kritik değildir.", "+3 Puan"))

    # 5. Kisa Kolon
    if req.kisaKolon == "var":
        evaluations.append(("Kısa Kolon Etkisi", "Deprem anında kesme kuvvetlerini kolonların kısa bölümüne yığarak ani kırılmalara neden olabilir.", "+20 Puan"))

    # 6. Plan / Bitisik
    if req.bitisik == "evet":
        if req.bitisikHiza == "farkli":
            evaluations.append(("Plan Düzensizliği (Kat Hizası Yok)", "Kat hizası bitişik nizamda yok; katlar arası deformasyon dağılımını eşit tutmaz ve çarpışma (çekiçleme) etkisini artırır.", "+10 Puan"))
        else:
            evaluations.append(("Bitişik Nizam (Kat Hizalı)", "Aynı hizada bitişik durum nispeten uyumlu salınıma olanak tanır.", "+5 Puan"))

    # 7. Catlak
    if req.hasar != "yok":
        evaluations.append((f"Fiziksel Hasar Gözlemi ({req.hasar.capitalize()})", "Görsel olarak saptanan çatlaklar, betonun iç yapısal bütünlüğünün bozulmuş olabileceğinin göstergesidir.", f"+{req.crackPuan or 8} Puan"))

    # 8. Beton Dayanimi
    if basinc_dayanimi < 25.0:
        evaluations.append((f"Çok Düşük Beton Dayanımı ({basinc_dayanimi:.1f} Mpa)", "Tasarım dayanımı (genellikle >= 25 MPa) çok altında; taşıma kapasitesi ciddi şekilde azalır.", "+20 Puan"))
    else:
        evaluations.append((f"Yeterli Beton Dayanımı ({basinc_dayanimi:.1f} MPa)", "Tasarım dayanımı sınırlarında veya kabul edilebilir durumda.", "0 Puan"))

    # 9. Korozyon
    evaluations.append((f"Korozyon Potansiyeli ({req.corrosion} mV)", f"{kor_seviye} korozyon riski. Donatıların paslanma hızı taşıyıcı kesit kayıplarına yol açabilir.", "-"))

    # --- TBDY 2018 UYUM TABLOSU ---
    tbdy_uyum = []
    # BKS
    bks_desc = "Konut, genel risk." if bks == 3 else ("Ticari/Sanayi" if bks == 2 else "Okul/Hastane, kritik bina.")
    tbdy_uyum.append(("Bina Kullanım Sınıfı (BKS)", f"BKS-{bks}", "Uygun", 'U', bks_desc))
    
    # DTS
    tbdy_uyum.append(("Deprem Tasarım Sınıfı (DTS)", f"DTS-{dts}", "Uygun", 'U', "Bölgesel deprem ivmesine göre belirlenmiştir."))
    
    # Yapısal Skor
    if health_score >= 80:
        tbdy_uyum.append(("Yapısal Skor ≥ 80", f"{health_score:.0f}", "Uygun", 'U', "Skor yüksek; yapı güvenli görünüyor."))
    elif health_score >= 50:
        tbdy_uyum.append(("Yapısal Skor ≥ 50", f"{health_score:.0f}", "Uyarı", 'D', "Orta risk; detaylı inceleme önerilir."))
    else:
        tbdy_uyum.append(("Yapısal Skor ≥ 50", f"{health_score:.0f}", "Uygun Değil", 'R', "Skor düşük; güçlendirme/önlem şart."))

    # Beton Dayanımı
    if basinc_dayanimi >= 25.0:
        tbdy_uyum.append(("Beton Dayanımı ≥ 25 MPa", f"{basinc_dayanimi:.1f} MPa", "Uygun", 'U', "TBDY 2018 minimum tasarım standardını karşılıyor."))
    else:
        tbdy_uyum.append(("Beton Dayanımı ≥ 25 MPa", f"{basinc_dayanimi:.1f} MPa", "Uygun Değil", 'R', "Kritik eksik; ciddi deprem hasarı riski taşır."))
        
    # Korozyon
    if req.corrosion >= -200:
        tbdy_uyum.append(("Korozyon Potansiyeli ≥ -200 mV", f"{req.corrosion:.0f} mV", "Uygun", 'U', "Korozyon riski düşük (%10)."))
    elif req.corrosion >= -350:
        tbdy_uyum.append(("Korozyon Potansiyeli > -350 mV", f"{req.corrosion:.0f} mV", "Uyarı", 'D', "Orta risk; koruyucu önlemler alınmalı."))
    else:
        tbdy_uyum.append(("Korozyon Potansiyeli > -350 mV", f"{req.corrosion:.0f} mV", "Uygun Değil", 'R', "Yüksek korozyon; donatı kesit kaybı muhtemel."))
        
    # Zayıf Kat
    tbdy_uyum.append(("Zayıf Kat (B2) Varlığı", "Var" if req.zeminDukkan == "evet" else "Yok", "Uyarı" if req.zeminDukkan == "evet" else "Uygun", 'D' if req.zeminDukkan == "evet" else 'U', "Zemin kat dükkan." if req.zeminDukkan == "evet" else "Yumuşak kat etkisi gözlenmedi."))


    try:
        pdf_url = await asyncio.to_thread(
            create_ai_pdf_report,
            params=pdf_params, counts=counts, risk_skoru=health_score,
            anfis_mpa=basinc_dayanimi, ai_text=aciklama, phase2_advice=phase2_advice,
            evaluations=evaluations, tbdy_uyum=tbdy_uyum,
            engine_version=ENGINE_VERSION,
        )
    except Exception as e:
        logger.error("PDF rapor uretim hatasi: %s", type(e).__name__)
        pdf_url = None
        detaylar.append("⚠️ PDF raporu olusturulamadı.")

    # --- Kayıt: Supabase + CSV (aynı dict) ---
    record_dict = {
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
        "engine_version": ENGINE_VERSION,
    }
    background_tasks.add_task(kayit_ekle_supabase, record_dict)
    background_tasks.add_task(kayit_ekle_csv, record_dict)

    # --- Explainability Trace (teknik JSON) ---
    fuzzy_trace = {
        "raw_score": raw_score,
        "capped_score": round(health_score, 2),
        "fired_rules": [
            {
                "id": r["id"],
                "output": r["output"],
                "activation": r["activation"],
                "rationale": r["rationale"],
            }
            for r in fired_rules
        ],
        "applied_caps": [
            {
                "cap_name": c["cap_name"],
                "effective": c.get("effective", True),
                "original_score": c["original_score"],
                "capped_score": c["capped_score"],
            }
            for c in applied_caps
        ],
    }

    if _fuzzy_fallback:
        fuzzy_trace["fallback"] = True
        fuzzy_trace["fallback_code"] = "FUZZY_ENGINE_ERROR"
        fuzzy_trace["fallback_message"] = "Karar motoru gecici olarak varsayilan modda calisti"

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
        bks=bks,
        binaYukseklik=round(h_n, 2),
        dts=dts,
        earthquakeClasses=counts,
        pdfDownloadUrl=pdf_url,
        engineVersion=ENGINE_VERSION,
        fuzzyTrace=fuzzy_trace,
    )
