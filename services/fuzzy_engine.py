"""Yapı Sağlığı — Fuzzy Logic Sistemi

v2: 27 kural (RULE_MATRIX), trapmf çıktı, policy layer, explainability
    Aktif karar motoru: compute_health_v2()
"""

import logging
from typing import List, Tuple, Dict

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

logger = logging.getLogger(__name__)


# =============================================================================
#  SHARED UTILITIES
# =============================================================================

def get_fuzzy_label(score: float) -> str:
    if score < 25:
        return "Very Bad (Çok Kötü - Acil)"
    if score < 45:
        return "Bad (Kötü - Güçlendirme Gerekli)"
    if score < 65:
        return "Medium (Orta Risk - İnceleme Gerekli)"
    if score < 85:
        return "Good (İyi - Bakım Önerilir)"
    return "Very Good (Çok İyi - Sağlam)"


def clamp(val: float, low: float, high: float) -> float:
    return max(low, min(high, val))


# =============================================================================
#  V2 — YENİ FUZZY MOTOR (Faz 2'de risk.py'den aktif çağrılacak)
#  27 kural | trapmf çıktı | RULE_MATRIX | policy layer | explainability
# =============================================================================

# -------------------------------------------------------------------------
#  V2 Engine Version
# -------------------------------------------------------------------------
ENGINE_VERSION = "v2_fuzzy27"

# -------------------------------------------------------------------------
#  V2 RULE_MATRIX — Single Source of Truth
#  Her kural: id, inputs, output, rationale, references
#  Kod, testler ve explainability bu yapıdan türetilir.
# -------------------------------------------------------------------------
RULE_MATRIX: List[Dict] = [
    # ===================== BLOK A: strength = low =====================
    {
        "id": "R01",
        "inputs": {"strength": "low", "corrosion": "high_risk", "survey_risk": "high"},
        "output": "very_bad",
        "rationale": "Üç faktör de kritik. Yapı acil tehlikede.",
        "references": ["TBDY 2018 Md. 7.2.5.3"],
    },
    {
        "id": "R02",
        "inputs": {"strength": "low", "corrosion": "high_risk", "survey_risk": "medium"},
        "output": "very_bad",
        "rationale": "Zayıf beton + yoğun korozyon → survey orta bile olsa gizli tehlike çok yüksek.",
        "references": ["TBDY 2018 Md. 7.2.5.3"],
    },
    {
        "id": "R03",
        "inputs": {"strength": "low", "corrosion": "high_risk", "survey_risk": "safe"},
        "output": "very_bad",
        "rationale": "Korozyon vetosu: dış görünüş aldatıcı, donatılar ağır hasar altında.",
        "references": ["ASTM C876-15", "TBDY 2018"],
    },
    {
        "id": "R04",
        "inputs": {"strength": "low", "corrosion": "medium_risk", "survey_risk": "high"},
        "output": "very_bad",
        "rationale": "C25 altı beton + orta korozyon + yapısal sorunlar — çoklu risk birikmesi.",
        "references": ["TBDY 2018 Md. 7.2.5.3"],
    },
    {
        "id": "R05",
        "inputs": {"strength": "low", "corrosion": "medium_risk", "survey_risk": "medium"},
        "output": "very_bad",
        "rationale": "Üç faktör de standart-altı. Birikimli tehlike.",
        "references": ["TBDY 2018"],
    },
    {
        "id": "R06",
        "inputs": {"strength": "low", "corrosion": "medium_risk", "survey_risk": "safe"},
        "output": "bad",
        "rationale": "Zayıf beton + orta korozyon ama yapısal sorun yok. Güçlendirme şart.",
        "references": ["TBDY 2018 Md. 7.2.5.3"],
    },
    {
        "id": "R07",
        "inputs": {"strength": "low", "corrosion": "low_risk", "survey_risk": "high"},
        "output": "bad",
        "rationale": "Korozyon düşük ama beton zayıf + yapısal sorunlar → güçlendirme gerekli.",
        "references": ["TBDY 2018"],
    },
    {
        "id": "R08",
        "inputs": {"strength": "low", "corrosion": "low_risk", "survey_risk": "medium"},
        "output": "bad",
        "rationale": "C25 altı beton tek başına yeterli risk. Korozyon avantajı betonu telafi etmez.",
        "references": ["TBDY 2018 Md. 7.2.5.3"],
    },
    {
        "id": "R09",
        "inputs": {"strength": "low", "corrosion": "low_risk", "survey_risk": "safe"},
        "output": "bad",
        "rationale": "Kural seviyesinde en iyi senaryo: tüm kurallar Bad veya Very Bad. Nihai garanti policy layer'da.",
        "references": ["TBDY 2018 Md. 7.2.5.3"],
    },
    # ===================== BLOK B: strength = medium =====================
    {
        "id": "R10",
        "inputs": {"strength": "medium", "corrosion": "high_risk", "survey_risk": "high"},
        "output": "very_bad",
        "rationale": "Beton yeterli ama yoğun korozyon + ağır yapısal sorunlar → taşıma kapasitesi tehlikede.",
        "references": ["ASTM C876-15", "TBDY 2018"],
    },
    {
        "id": "R11",
        "inputs": {"strength": "medium", "corrosion": "high_risk", "survey_risk": "medium"},
        "output": "bad",
        "rationale": "Korozyon ciddi tehdit, yapısal risk orta. Korozyon vetosu: high_risk = en fazla Bad.",
        "references": ["ASTM C876-15"],
    },
    {
        "id": "R12",
        "inputs": {"strength": "medium", "corrosion": "high_risk", "survey_risk": "safe"},
        "output": "bad",
        "rationale": "Gizli tehlike: survey iyi ama korozyon donatıyı yiyor. Korozyon vetosu aktif.",
        "references": ["ASTM C876-15"],
    },
    {
        "id": "R13",
        "inputs": {"strength": "medium", "corrosion": "medium_risk", "survey_risk": "high"},
        "output": "bad",
        "rationale": "Orta beton + orta korozyon + yüksek yapısal risk → kötü kombinasyon.",
        "references": ["TBDY 2018"],
    },
    {
        "id": "R14",
        "inputs": {"strength": "medium", "corrosion": "medium_risk", "survey_risk": "medium"},
        "output": "medium",
        "rationale": "Her üç faktör 'orta' → dengeli orta risk, izleme ve inceleme gerekli.",
        "references": [],
    },
    {
        "id": "R15",
        "inputs": {"strength": "medium", "corrosion": "medium_risk", "survey_risk": "safe"},
        "output": "medium",
        "rationale": "Orta beton + orta korozyon, yapısal olarak sağlam → izlenebilir.",
        "references": [],
    },
    {
        "id": "R16",
        "inputs": {"strength": "medium", "corrosion": "low_risk", "survey_risk": "high"},
        "output": "bad",
        "rationale": "Yapısal sorunlar ciddi. Beton yeterli + korozyon düşük ama yapısal zayıflıklar tehlikeli.",
        "references": ["TBDY 2018"],
    },
    {
        "id": "R17",
        "inputs": {"strength": "medium", "corrosion": "low_risk", "survey_risk": "medium"},
        "output": "medium",
        "rationale": "Beton standart, korozyon düşük, yapısal risk orta → izleme.",
        "references": [],
    },
    {
        "id": "R18",
        "inputs": {"strength": "medium", "corrosion": "low_risk", "survey_risk": "safe"},
        "output": "good",
        "rationale": "Tüm faktörler kabul edilebilir. Periyodik bakım yeterli.",
        "references": [],
    },
    # ===================== BLOK C: strength = high =====================
    {
        "id": "R19",
        "inputs": {"strength": "high", "corrosion": "high_risk", "survey_risk": "high"},
        "output": "bad",
        "rationale": "Kritik çelişki: beton mükemmel ama donatılar ağır korozyonda + yapısal sorunlar. Korozyon vetosu aktif.",
        "references": ["ASTM C876-15"],
    },
    {
        "id": "R20",
        "inputs": {"strength": "high", "corrosion": "high_risk", "survey_risk": "medium"},
        "output": "bad",
        "rationale": "Yüksek korozyon uzun vadede betonu da etkileyecek. Korozyon vetosu aktif.",
        "references": ["ASTM C876-15"],
    },
    {
        "id": "R21",
        "inputs": {"strength": "high", "corrosion": "high_risk", "survey_risk": "safe"},
        "output": "bad",
        "rationale": "Beton güçlü + survey iyi ama korozyon ciddi. Semantik tutarlılık: high_risk = en fazla Bad.",
        "references": ["ASTM C876-15"],
    },
    {
        "id": "R22",
        "inputs": {"strength": "high", "corrosion": "medium_risk", "survey_risk": "high"},
        "output": "medium",
        "rationale": "Güçlü beton kısmen telafi ediyor ama yapısal sorunlar + orta korozyon → izleme.",
        "references": [],
    },
    {
        "id": "R23",
        "inputs": {"strength": "high", "corrosion": "medium_risk", "survey_risk": "medium"},
        "output": "medium",
        "rationale": "Orta korozyon + orta yapısal risk, güçlü beton ile dengeleniyor.",
        "references": [],
    },
    {
        "id": "R24",
        "inputs": {"strength": "high", "corrosion": "medium_risk", "survey_risk": "safe"},
        "output": "good",
        "rationale": "Güçlü beton + iyi survey → orta korozyon yönetilebilir. Bakım planı yeterli.",
        "references": [],
    },
    {
        "id": "R25",
        "inputs": {"strength": "high", "corrosion": "low_risk", "survey_risk": "high"},
        "output": "medium",
        "rationale": "Korozyon düşük + beton güçlü ama ciddi yapısal sorunlar → inceleme gerekli.",
        "references": ["TBDY 2018"],
    },
    {
        "id": "R26",
        "inputs": {"strength": "high", "corrosion": "low_risk", "survey_risk": "medium"},
        "output": "good",
        "rationale": "Güçlü beton, düşük korozyon, orta yapısal risk → iyi durumda.",
        "references": [],
    },
    {
        "id": "R27",
        "inputs": {"strength": "high", "corrosion": "low_risk", "survey_risk": "safe"},
        "output": "very_good",
        "rationale": "Tüm faktörler optimal. Sağlam yapı.",
        "references": [],
    },
]


# -------------------------------------------------------------------------
#  V2 Policy Layer Constants (provisional — Faz 3'te kalibre edilecek)
# -------------------------------------------------------------------------
TBDY_THRESHOLD = 25.0    # MPa — TBDY 2018 minimum C25
ASTM_THRESHOLD = -350.0  # mV  — ASTM C876 aktif korozyon sınırı
CAP_SINGLE = 40          # Tek kritik faktör cap değeri (Bad bant üst çeyreği)
CAP_DUAL = 25            # Çift kritik faktör cap değeri (Very Bad / Bad sınırı)


# -------------------------------------------------------------------------
#  V2 Fuzzy System Builder
# -------------------------------------------------------------------------

def _build_antecedents_v2():
    """Girdi değişkenlerini oluşturur. Girdi MF'leri v1 ile aynıdır."""
    strength = ctrl.Antecedent(np.arange(0, 81, 1), "strength")
    corrosion = ctrl.Antecedent(np.arange(-600, 101, 1), "corrosion")
    survey_risk = ctrl.Antecedent(np.arange(0, 51, 1), "survey_risk")

    strength["low"] = fuzz.trapmf(strength.universe, [0, 0, 15, 25])
    strength["medium"] = fuzz.trimf(strength.universe, [20, 35, 50])
    strength["high"] = fuzz.trapmf(strength.universe, [40, 55, 80, 80])

    corrosion["high_risk"] = fuzz.trapmf(corrosion.universe, [-600, -600, -400, -300])
    corrosion["medium_risk"] = fuzz.trimf(corrosion.universe, [-400, -275, -150])
    corrosion["low_risk"] = fuzz.trapmf(corrosion.universe, [-200, -100, 100, 100])

    survey_risk["safe"] = fuzz.trapmf(survey_risk.universe, [0, 0, 10, 15])
    survey_risk["medium"] = fuzz.trimf(survey_risk.universe, [12, 25, 38])
    survey_risk["high"] = fuzz.trapmf(survey_risk.universe, [30, 40, 50, 50])

    return strength, corrosion, survey_risk


def _build_consequent_v2():
    """Çıktı değişkenini trapmf ile oluşturur (v1'den farklı — daha stabil)."""
    health = ctrl.Consequent(np.arange(0, 101, 1), "health")

    health["very_bad"] = fuzz.trapmf(health.universe, [0, 0, 15, 30])
    health["bad"] = fuzz.trapmf(health.universe, [20, 30, 40, 50])
    health["medium"] = fuzz.trapmf(health.universe, [42, 50, 60, 68])
    health["good"] = fuzz.trapmf(health.universe, [62, 70, 80, 88])
    health["very_good"] = fuzz.trapmf(health.universe, [82, 90, 100, 100])

    return health


def create_fuzzy_system_v2() -> ctrl.ControlSystem:
    """
    RULE_MATRIX'ten 27 kuralı otomatik üretir.
    Her kural: strength[set] & corrosion[set] & survey_risk[set] → health[output]
    """
    strength, corrosion, survey_risk = _build_antecedents_v2()
    health = _build_consequent_v2()

    antecedent_map = {
        "strength": strength,
        "corrosion": corrosion,
        "survey_risk": survey_risk,
    }

    rules = []
    for entry in RULE_MATRIX:
        inp = entry["inputs"]
        antecedent_expr = (
            antecedent_map["strength"][inp["strength"]]
            & antecedent_map["corrosion"][inp["corrosion"]]
            & antecedent_map["survey_risk"][inp["survey_risk"]]
        )
        rule = ctrl.Rule(antecedent_expr, health[entry["output"]])
        rules.append(rule)

    return ctrl.ControlSystem(rules)


# Staged v2 instance — Faz 2'de risk.py burayı import edecek
fuzzy_control_system_v2 = create_fuzzy_system_v2()


# -------------------------------------------------------------------------
#  V2 Explainability — get_fired_rules()
# -------------------------------------------------------------------------

def _compute_membership(value: float, mf_params: list, mf_type: str) -> float:
    """Tek bir üyelik fonksiyonu için üyelik derecesini hesaplar."""
    arr = np.array([value])
    if mf_type == "trapmf":
        return float(fuzz.trapmf(arr, mf_params)[0])
    elif mf_type == "trimf":
        return float(fuzz.trimf(arr, mf_params)[0])
    return 0.0


# Girdi MF tanımları — _build_antecedents_v2() ile senkron tutulmalı
_INPUT_MF_DEFS = {
    "strength": {
        "low":    {"params": [0, 0, 15, 25],       "type": "trapmf"},
        "medium": {"params": [20, 35, 50],          "type": "trimf"},
        "high":   {"params": [40, 55, 80, 80],      "type": "trapmf"},
    },
    "corrosion": {
        "high_risk":   {"params": [-600, -600, -400, -300], "type": "trapmf"},
        "medium_risk": {"params": [-400, -275, -150],       "type": "trimf"},
        "low_risk":    {"params": [-200, -100, 100, 100],   "type": "trapmf"},
    },
    "survey_risk": {
        "safe":   {"params": [0, 0, 10, 15],    "type": "trapmf"},
        "medium": {"params": [12, 25, 38],       "type": "trimf"},
        "high":   {"params": [30, 40, 50, 50],   "type": "trapmf"},
    },
}


def get_fired_rules(
    strength_val: float,
    corrosion_val: float,
    survey_val: float,
    top_n: int = 3,
) -> List[Dict]:
    """
    Verilen girdiler için RULE_MATRIX üzerinden ateşlenen kuralları hesaplar.
    Her kural için aktivasyon derecesi = min(μ_strength, μ_corrosion, μ_survey).

    Returns:
        Aktivasyon derecesine göre sıralanmış top_n kural listesi.
        Her eleman: {id, output, activation, rationale, references, membership_detail}
    """
    # Tüm girdiler için üyelik derecelerini hesapla
    memberships = {}
    input_values = {
        "strength": strength_val,
        "corrosion": corrosion_val,
        "survey_risk": survey_val,
    }

    for var_name, value in input_values.items():
        memberships[var_name] = {}
        for set_name, mf_def in _INPUT_MF_DEFS[var_name].items():
            mu = _compute_membership(value, mf_def["params"], mf_def["type"])
            memberships[var_name][set_name] = round(mu, 4)

    # Her kural için aktivasyon derecesi hesapla
    fired = []
    for entry in RULE_MATRIX:
        inp = entry["inputs"]
        mu_strength = memberships["strength"][inp["strength"]]
        mu_corrosion = memberships["corrosion"][inp["corrosion"]]
        mu_survey = memberships["survey_risk"][inp["survey_risk"]]

        activation = min(mu_strength, mu_corrosion, mu_survey)

        if activation > 0.0:
            fired.append({
                "id": entry["id"],
                "output": entry["output"],
                "activation": round(activation, 4),
                "rationale": entry["rationale"],
                "references": entry["references"],
                "membership_detail": {
                    "strength": {inp["strength"]: mu_strength},
                    "corrosion": {inp["corrosion"]: mu_corrosion},
                    "survey_risk": {inp["survey_risk"]: mu_survey},
                },
            })

    # Aktivasyon derecesine göre azalan sıralama, top_n kadar döndür
    fired.sort(key=lambda x: x["activation"], reverse=True)
    return fired[:top_n]


# -------------------------------------------------------------------------
#  V2 Policy Layer — apply_policy_caps()
# -------------------------------------------------------------------------

def apply_policy_caps(
    score: float,
    basinc_dayanimi: float,
    corrosion_mv: float,
) -> Tuple[float, List[Dict]]:
    """
    Fuzzy skor üzerine yönetmelik/standart guardrail'lerini uygular.

    Guardrail koşulu sağlandığında trace HER ZAMAN üretilir — skor numerik
    olarak değişse de değişmese de. ``effective`` alanı bu ayrımı belirtir:
      - True  → skor cap ile düşürüldü
      - False → koşul eşleşti ama skor zaten cap altındaydı (numerik etki yok)

    Policy sırası:
      1. Çift kritik (MPa < 25 VE mV ≤ -350) → CAP_DUAL
      2. Tek kritik TBDY (MPa < 25) → CAP_SINGLE
      3. Tek kritik ASTM (mV ≤ -350) → CAP_SINGLE

    Args:
        score: Ham fuzzy skor (0-100)
        basinc_dayanimi: Tahmini beton dayanımı (MPa, RF regresyondan)
        corrosion_mv: Korozyon potansiyeli (mV)

    Returns:
        (capped_score, applied_caps) tuple'ı.
        applied_caps: Eşleşen guardrail'lerin listesi. Her eleman:
            cap_name, original_score, capped_score, effective, reason, recommendation
        Boş liste = hiçbir guardrail koşulu sağlanmadı.
    """
    applied_caps: List[Dict] = []
    capped_score = score

    is_low_strength = basinc_dayanimi < TBDY_THRESHOLD
    is_high_corrosion = corrosion_mv <= ASTM_THRESHOLD

    if is_low_strength and is_high_corrosion:
        # Çift kritik durum — en sıkı cap
        effective = score > CAP_DUAL
        if effective:
            capped_score = float(CAP_DUAL)
        applied_caps.append({
            "cap_name": "CAP_DUAL",
            "effective": effective,
            "threshold_strength": f"< {TBDY_THRESHOLD} MPa",
            "threshold_corrosion": f"<= {ASTM_THRESHOLD} mV",
            "original_score": round(score, 2),
            "capped_score": round(capped_score, 2),
            "reason": (
                f"Kritik ön tarama uyarısı: Tahmini beton dayanımı "
                f"({basinc_dayanimi:.1f} MPa) TBDY 2018 C25 risk eşiği altında "
                f"VE korozyon potansiyeli ({corrosion_mv:.0f} mV) ASTM C876 "
                f"aktif korozyon eşiğinde. Hem beton hem donatı tehlikede."
            ),
            "recommendation": (
                "Acil karot deneyi ve donatı kesit ölçümü gereklidir. "
                "Yapının taşıma kapasitesi ciddi risk altında olabilir."
            ),
        })

    elif is_low_strength:
        # Tek kritik: düşük beton
        effective = score > CAP_SINGLE
        if effective:
            capped_score = float(CAP_SINGLE)
        applied_caps.append({
            "cap_name": "TBDY_ONELEME_CAP",
            "effective": effective,
            "threshold": f"< {TBDY_THRESHOLD} MPa",
            "original_score": round(score, 2),
            "capped_score": round(capped_score, 2),
            "reason": (
                f"Kritik ön tarama uyarısı: Tahribatsız test sonuçlarına göre "
                f"tahmini beton dayanımı ({basinc_dayanimi:.1f} MPa) "
                f"TBDY 2018 C25 risk eşiği ({TBDY_THRESHOLD} MPa) altındadır."
            ),
            "recommendation": (
                "Kesin değerlendirme için karot deneyi ile beton dayanımının "
                "doğrulanması gereklidir."
            ),
        })

    elif is_high_corrosion:
        # Tek kritik: yüksek korozyon
        effective = score > CAP_SINGLE
        if effective:
            capped_score = float(CAP_SINGLE)
        applied_caps.append({
            "cap_name": "ASTM_C876_CAP",
            "effective": effective,
            "threshold": f"<= {ASTM_THRESHOLD} mV",
            "original_score": round(score, 2),
            "capped_score": round(capped_score, 2),
            "reason": (
                f"Korozyon uyarısı: Korozyon potansiyeli ({corrosion_mv:.0f} mV) "
                f"ASTM C876 aktif korozyon eşiğinin ({ASTM_THRESHOLD:.0f} mV) "
                f"altında. Donatılarda %90+ aktif korozyon olasılığı."
            ),
            "recommendation": (
                "Donatı kesit kaybı ölçümü ve koruyucu önlemler "
                "(katodik koruma, onarım) değerlendirilmelidir."
            ),
        })

    return capped_score, applied_caps


# -------------------------------------------------------------------------
#  V2 Convenience — compute_health_v2() (Faz 2'de risk.py bunu çağıracak)
# -------------------------------------------------------------------------

def compute_health_v2(
    strength_val: float,
    corrosion_val: float,
    survey_val: float,
    basinc_dayanimi: float,
) -> Dict:
    """
    Tam v2 pipeline: fuzzy hesaplama → policy cap → explainability.

    Returns:
        {
            "raw_score": float,
            "capped_score": float,
            "label": str,
            "applied_caps": list,
            "fired_rules": list,
            "engine_version": str,
        }
    """
    # 1. Girdileri clamp et
    f_strength = clamp(float(strength_val), 0.0, 80.0)
    f_corrosion = clamp(float(corrosion_val), -600.0, 100.0)
    f_survey = clamp(float(survey_val), 0.0, 50.0)

    # Clamp uyarıları
    if f_strength != float(strength_val):
        logger.warning(
            "Strength clamped: %.2f -> %.2f", strength_val, f_strength
        )
    if f_corrosion != float(corrosion_val):
        logger.warning(
            "Corrosion clamped: %.2f -> %.2f", corrosion_val, f_corrosion
        )
    if f_survey != float(survey_val):
        logger.warning(
            "Survey risk clamped: %.2f -> %.2f", survey_val, f_survey
        )

    # 2. Fuzzy inference
    sim = ctrl.ControlSystemSimulation(fuzzy_control_system_v2)
    sim.input["strength"] = f_strength
    sim.input["corrosion"] = f_corrosion
    sim.input["survey_risk"] = f_survey
    sim.compute()

    raw_score = clamp(float(sim.output["health"]), 0.0, 100.0)

    # 3. Policy caps
    capped_score, applied_caps = apply_policy_caps(
        raw_score, basinc_dayanimi, f_corrosion
    )

    # 4. Label (cap sonrası skordan)
    label = get_fuzzy_label(capped_score)

    # 5. Explainability
    fired_rules = get_fired_rules(f_strength, f_corrosion, f_survey, top_n=3)

    return {
        "raw_score": round(raw_score, 2),
        "capped_score": round(capped_score, 2),
        "label": label,
        "applied_caps": applied_caps,
        "fired_rules": fired_rules,
        "engine_version": ENGINE_VERSION,
    }
