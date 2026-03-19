"""Faz 3 — Doğrulama ve Kalibrasyon Test Suite.

Kapsamlı v2 fuzzy + policy layer doğrulama:
  1. 27 kural boundary testleri
  2. Monotonicity sweep
  3. Determinism doğrulaması
  4. Explainability trace consistency
  5. Policy guardrail doğrulaması
  6. Universe resolution / stability
  7. Cap sabitleri değerlendirmesi
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import numpy as np
from skfuzzy import control as ctrl

from services.fuzzy_engine import (
    fuzzy_control_system_v2,
    compute_health_v2,
    get_fired_rules,
    apply_policy_caps,
    get_fuzzy_label,
    clamp,
    ENGINE_VERSION,
    RULE_MATRIX,
    CAP_SINGLE,
    CAP_DUAL,
    TBDY_THRESHOLD,
    ASTM_THRESHOLD,
    _INPUT_MF_DEFS,
    _compute_membership,
)


# ==================================================================
#  1. BOUNDARY TESTLERI
# ==================================================================

class TestBoundaryValues:
    """MF sınır ve yakın-sınır noktalarında v2 sistemin çalışması."""

    # Representative corner/boundary seçimi:
    #   strength: 0 (sol kenar), 15 (low-medium sınırı), 22 (overlap), 35 (medium peak),
    #             50 (medium-high sınırı), 55 (high plato), 80 (sağ kenar)
    #   corrosion: -600 (sol kenar), -400 (high-medium sınırı), -350 (ASTM eşiği),
    #              -275 (medium peak), -200 (medium-low sınırı), -100 (low plato)
    #   survey:    0 (sol kenar), 10 (safe-medium sınırı), 13 (overlap), 25 (medium peak),
    #              38 (medium-high sınırı), 40 (high plato), 50 (sağ kenar)

    BOUNDARY_STRENGTHS = [0, 15, 22, 35, 50, 55, 80]
    BOUNDARY_CORROSIONS = [-600, -400, -350, -275, -200, -100]
    BOUNDARY_SURVEYS = [0, 10, 13, 25, 38, 40, 50]

    def test_all_corners_produce_valid_score(self):
        """Her köşe noktasında v2 sistem 0-100 arası skor üretmeli."""
        corners = [
            (0, -600, 0), (0, -600, 50), (0, 100, 0), (0, 100, 50),
            (80, -600, 0), (80, -600, 50), (80, 100, 0), (80, 100, 50),
        ]
        for s, c, sr in corners:
            sim = ctrl.ControlSystemSimulation(fuzzy_control_system_v2)
            sim.input["strength"] = float(s)
            sim.input["corrosion"] = float(c)
            sim.input["survey_risk"] = float(sr)
            sim.compute()
            score = sim.output["health"]
            assert 0 <= score <= 100, f"Corner ({s},{c},{sr}) → skor aralık dışı: {score}"

    def test_representative_boundary_sweep(self):
        """14 representative boundary noktasında hesaplama başarılı."""
        cases = [
            # (strength, corrosion, survey_risk)
            (15, -300, 15),    # strength low-medium sınırı, corrosion high-medium sınırı
            (22, -275, 13),    # plan örneği civarı
            (25, -350, 25),    # TBDY eşiği, ASTM eşiği, survey medium peak
            (35, -200, 10),    # medium peak, corrosion low-medium sınırı
            (50, -100, 38),    # strength medium-high sınırı, survey medium-high sınırı
            (55, -400, 40),    # high plato, corrosion high-medium sınırı, survey high
            (20, -500, 30),    # low beton, ciddi korozyon, yüksek survey
            (40, -150, 5),     # high beton başlangıcı, düşük korozyon, düşük survey
            (0, -600, 50),     # en kötü köşe
            (80, 100, 0),      # en iyi köşe
            (35, -275, 25),    # tam orta
            (50, -350, 15),    # ASTM sınırı + strength high sınırı
            (15, -100, 40),    # düşük beton + düşük korozyon + yüksek survey
            (55, -200, 13),    # güçlü beton + düşük korozyon + düşük survey
        ]
        for s, c, sr in cases:
            result = compute_health_v2(float(s), float(c), float(sr), float(s))
            assert 0 <= result["raw_score"] <= 100
            assert 0 <= result["capped_score"] <= 100
            assert result["label"] != ""

    def test_worst_case_score_is_low(self):
        """En kötü girdiler → skor çok düşük olmalı."""
        result = compute_health_v2(0.0, -600.0, 50.0, 0.0)
        assert result["raw_score"] < 20, f"En kötü girdi skorunun düşük olması beklenir: {result['raw_score']}"

    def test_best_case_score_is_high(self):
        """En iyi girdiler → skor çok yüksek olmalı."""
        result = compute_health_v2(80.0, 100.0, 0.0, 80.0)
        assert result["raw_score"] > 80, f"En iyi girdi skorunun yüksek olması beklenir: {result['raw_score']}"


# ==================================================================
#  2. MONOTONİCİTY TESTLERİ
# ==================================================================

class TestMonotonicity:
    """Fuzzy raw skorun monotonicity davranışı.

    Beklenti: strength arttıkça veya corrosion iyileştikçe veya survey düştükçe
    skor artmalı veya aynı kalmalı (non-decreasing). Fuzzy overlap nedeniyle
    küçük dalgalanmalar kabul edilir; tolerance = 2.0 birim.
    """

    TOLERANCE = 2.0  # Fuzzy overlap kaynaklı kabul edilir dalgalanma

    def test_monotonicity_strength_axis(self):
        """strength artarken (corrosion/survey sabit) raw skor non-decreasing olmalı."""
        fixed_corrosion = -200.0
        fixed_survey = 15.0
        strengths = list(range(5, 76, 5))
        scores = []
        for s in strengths:
            result = compute_health_v2(float(s), fixed_corrosion, fixed_survey, float(s))
            scores.append(result["raw_score"])

        violations = []
        for i in range(1, len(scores)):
            drop = scores[i - 1] - scores[i]
            if drop > self.TOLERANCE:
                violations.append(
                    f"  strength {strengths[i-1]}→{strengths[i]}: "
                    f"skor {scores[i-1]:.2f}→{scores[i]:.2f} (düşüş={drop:.2f})"
                )
        assert len(violations) == 0, (
            f"Strength aksında monotonicity ihlali:\n" + "\n".join(violations)
        )

    def test_monotonicity_corrosion_axis(self):
        """corrosion iyileşirken (daha pozitif) raw skor non-decreasing olmalı."""
        fixed_strength = 35.0
        fixed_survey = 15.0
        corrosions = list(range(-550, 50, 50))
        scores = []
        for c in corrosions:
            result = compute_health_v2(fixed_strength, float(c), fixed_survey, fixed_strength)
            scores.append(result["raw_score"])

        violations = []
        for i in range(1, len(scores)):
            drop = scores[i - 1] - scores[i]
            if drop > self.TOLERANCE:
                violations.append(
                    f"  corrosion {corrosions[i-1]}→{corrosions[i]}: "
                    f"skor {scores[i-1]:.2f}→{scores[i]:.2f} (düşüş={drop:.2f})"
                )
        assert len(violations) == 0, (
            f"Corrosion aksında monotonicity ihlali:\n" + "\n".join(violations)
        )

    def test_monotonicity_survey_axis(self):
        """survey_risk düşerken raw skor non-decreasing olmalı."""
        fixed_strength = 35.0
        fixed_corrosion = -200.0
        surveys = list(range(45, 0, -5))  # 45→5 (azalan risk)
        scores = []
        for sr in surveys:
            result = compute_health_v2(fixed_strength, fixed_corrosion, float(sr), fixed_strength)
            scores.append(result["raw_score"])

        violations = []
        for i in range(1, len(scores)):
            drop = scores[i - 1] - scores[i]
            if drop > self.TOLERANCE:
                violations.append(
                    f"  survey {surveys[i-1]}→{surveys[i]}: "
                    f"skor {scores[i-1]:.2f}→{scores[i]:.2f} (düşüş={drop:.2f})"
                )
        assert len(violations) == 0, (
            f"Survey aksında monotonicity ihlali:\n" + "\n".join(violations)
        )

    def test_capped_score_monotonicity_with_policy(self):
        """Cap sonrası nihai skor: plateau kabul edilir, düşüş kabul edilmez."""
        # strength artarken (düşük beton bölgesinde cap aktif olabilir)
        fixed_corrosion = -200.0
        fixed_survey = 15.0
        strengths = list(range(10, 60, 5))
        scores = []
        for s in strengths:
            result = compute_health_v2(float(s), fixed_corrosion, fixed_survey, float(s))
            scores.append(result["capped_score"])

        violations = []
        for i in range(1, len(scores)):
            drop = scores[i - 1] - scores[i]
            if drop > self.TOLERANCE:
                violations.append(
                    f"  strength {strengths[i-1]}→{strengths[i]}: "
                    f"capped {scores[i-1]:.2f}→{scores[i]:.2f} (düşüş={drop:.2f})"
                )
        assert len(violations) == 0, (
            f"Capped skor monotonicity ihlali:\n" + "\n".join(violations)
        )


# ==================================================================
#  3. DETERMİNİSM TESTLERİ
# ==================================================================

class TestDeterminism:
    """Aynı girdi → aynı çıktı, her çalıştırmada."""

    FIXED_CASES = [
        (22.0, -100.0, 13.0, 22.0),
        (35.0, -275.0, 25.0, 35.0),
        (55.0, -400.0, 40.0, 55.0),
        (80.0, 100.0, 0.0, 80.0),
        (5.0, -500.0, 48.0, 5.0),
    ]

    @pytest.mark.parametrize("s,c,sr,mpa", FIXED_CASES)
    def test_repeated_runs_same_result(self, s, c, sr, mpa):
        """10 tekrarlı çalıştırmada aynı sonuç."""
        results = [compute_health_v2(s, c, sr, mpa) for _ in range(10)]

        first = results[0]
        for i, r in enumerate(results[1:], 1):
            assert r["raw_score"] == first["raw_score"], f"Run {i}: raw_score farklı"
            assert r["capped_score"] == first["capped_score"], f"Run {i}: capped_score farklı"
            assert r["label"] == first["label"], f"Run {i}: label farklı"
            assert r["engine_version"] == first["engine_version"]
            assert len(r["fired_rules"]) == len(first["fired_rules"])
            for j in range(len(r["fired_rules"])):
                assert r["fired_rules"][j]["id"] == first["fired_rules"][j]["id"]
                assert r["fired_rules"][j]["activation"] == first["fired_rules"][j]["activation"]
            assert len(r["applied_caps"]) == len(first["applied_caps"])
            for j in range(len(r["applied_caps"])):
                assert r["applied_caps"][j]["cap_name"] == first["applied_caps"][j]["cap_name"]
                assert r["applied_caps"][j]["effective"] == first["applied_caps"][j]["effective"]


# ==================================================================
#  4. EXPLAİNABİLİTY TRACE CONSISTENCY
# ==================================================================

class TestExplainabilityTrace:
    """fired_rules ve applied_caps trace'inin tutarlılığı."""

    def test_fired_rules_sorted_by_activation(self):
        """get_fired_rules çıktısı aktivasyona göre azalan sıralı."""
        fired = get_fired_rules(22.0, -100.0, 13.0, top_n=10)
        for i in range(len(fired) - 1):
            assert fired[i]["activation"] >= fired[i + 1]["activation"], (
                f"Sıralama hata: {fired[i]['id']}({fired[i]['activation']}) < "
                f"{fired[i+1]['id']}({fired[i+1]['activation']})"
            )

    def test_fired_rules_match_membership(self):
        """Top rule'un aktivasyonu = min(μ_strength, μ_corrosion, μ_survey)."""
        s, c, sr = 35.0, -275.0, 25.0
        fired = get_fired_rules(s, c, sr, top_n=1)
        assert len(fired) >= 1
        rule = fired[0]
        detail = rule["membership_detail"]
        mu_s = list(detail["strength"].values())[0]
        mu_c = list(detail["corrosion"].values())[0]
        mu_sr = list(detail["survey_risk"].values())[0]
        expected_activation = min(mu_s, mu_c, mu_sr)
        assert abs(rule["activation"] - expected_activation) < 0.001

    def test_fired_rule_ids_are_valid(self):
        """Ateşlenen kural ID'leri RULE_MATRIX'te var."""
        valid_ids = {r["id"] for r in RULE_MATRIX}
        fired = get_fired_rules(35.0, -200.0, 15.0, top_n=10)
        for r in fired:
            assert r["id"] in valid_ids, f"Bilinmeyen kural: {r['id']}"

    def test_applied_caps_consistent_with_scores(self):
        """applied_caps trace'i raw/capped skor ile uyumlu."""
        # TBDY cap senaryosu
        result = compute_health_v2(22.0, -100.0, 13.0, 22.0)
        for cap in result["applied_caps"]:
            if cap["effective"]:
                assert cap["capped_score"] < cap["original_score"], (
                    f"effective=True ama capped >= original: {cap}"
                )
            else:
                assert cap["capped_score"] == cap["original_score"], (
                    f"effective=False ama capped != original: {cap}"
                )

    def test_trace_route_detaylar_consistency(self):
        """compute_health_v2 applied_caps → route'daki detaylar üretimi ile uyumlu.

        Bu test doğrudan route çağırmıyor, ama trace yapısının
        detay üretimi için gerekli alanları taşıdığını doğruluyor.
        """
        result = compute_health_v2(5.0, -500.0, 48.0, 5.0)
        for cap in result["applied_caps"]:
            assert "reason" in cap, f"reason eksik: {cap['cap_name']}"
            assert "recommendation" in cap, f"recommendation eksik: {cap['cap_name']}"
            assert len(cap["reason"]) > 0
            assert len(cap["recommendation"]) > 0
            assert "cap_name" in cap
            assert "effective" in cap


# ==================================================================
#  5. POLİCY GUARDRAİL DOĞRULAMASI
# ==================================================================

class TestPolicyGuardrails:
    """Her guardrail senaryosu ayrı ayrı ve birlikte."""

    def test_no_cap_normal_values(self):
        score, caps = apply_policy_caps(72.0, 35.0, -100.0)
        assert score == 72.0
        assert len(caps) == 0

    def test_tbdy_cap_effective(self):
        score, caps = apply_policy_caps(62.0, 22.0, -100.0)
        assert score == float(CAP_SINGLE)
        assert caps[0]["cap_name"] == "TBDY_ONELEME_CAP"
        assert caps[0]["effective"] is True

    def test_astm_cap_effective(self):
        score, caps = apply_policy_caps(55.0, 35.0, -400.0)
        assert score == float(CAP_SINGLE)
        assert caps[0]["cap_name"] == "ASTM_C876_CAP"
        assert caps[0]["effective"] is True

    def test_dual_cap_effective(self):
        score, caps = apply_policy_caps(48.0, 20.0, -500.0)
        assert score == float(CAP_DUAL)
        assert caps[0]["cap_name"] == "CAP_DUAL"
        assert caps[0]["effective"] is True

    def test_tbdy_cap_ineffective(self):
        score, caps = apply_policy_caps(30.0, 22.0, -100.0)
        assert score == 30.0
        assert caps[0]["effective"] is False
        assert caps[0]["cap_name"] == "TBDY_ONELEME_CAP"
        assert "karot" in caps[0]["recommendation"].lower()

    def test_astm_cap_ineffective(self):
        score, caps = apply_policy_caps(35.0, 40.0, -500.0)
        assert score == 35.0
        assert caps[0]["effective"] is False
        assert caps[0]["cap_name"] == "ASTM_C876_CAP"

    def test_dual_cap_ineffective(self):
        score, caps = apply_policy_caps(15.0, 18.0, -450.0)
        assert score == 15.0
        assert caps[0]["effective"] is False
        assert caps[0]["cap_name"] == "CAP_DUAL"
        assert "karot" in caps[0]["recommendation"].lower()
        assert "donatı" in caps[0]["recommendation"].lower()

    def test_tbdy_threshold_boundary_exact(self):
        """Tam eşik: 25.0 MPa → TBDY tetiklenmemeli (strict <)."""
        score, caps = apply_policy_caps(60.0, 25.0, -100.0)
        assert len(caps) == 0, "25.0 MPa = eşik, strict < olmalı → cap yok"

    def test_astm_threshold_boundary_exact(self):
        """Tam eşik: -350.0 mV → ASTM tetiklenmeli (<=)."""
        score, caps = apply_policy_caps(60.0, 35.0, -350.0)
        assert len(caps) == 1, "-350 mV = eşik, <= olmalı → cap var"
        assert caps[0]["cap_name"] == "ASTM_C876_CAP"

    def test_dual_requires_both_thresholds(self):
        """Çift kritik için HER İKİ eşik de geçmeli."""
        # Sadece TBDY
        _, caps1 = apply_policy_caps(60.0, 22.0, -100.0)
        assert caps1[0]["cap_name"] == "TBDY_ONELEME_CAP"

        # Sadece ASTM
        _, caps2 = apply_policy_caps(60.0, 35.0, -400.0)
        assert caps2[0]["cap_name"] == "ASTM_C876_CAP"

        # İkisi birden
        _, caps3 = apply_policy_caps(60.0, 22.0, -400.0)
        assert caps3[0]["cap_name"] == "CAP_DUAL"

    def test_recommendation_never_empty(self):
        """Her cap trace'inin recommendation alanı boş olmamalı."""
        scenarios = [
            (60.0, 22.0, -100.0),  # TBDY
            (60.0, 35.0, -400.0),  # ASTM
            (60.0, 22.0, -400.0),  # DUAL
            (15.0, 22.0, -400.0),  # DUAL ineffective
        ]
        for s, mpa, mv in scenarios:
            _, caps = apply_policy_caps(s, mpa, mv)
            for cap in caps:
                assert len(cap["recommendation"]) > 10, (
                    f"Recommendation çok kısa: {cap['cap_name']}: {cap['recommendation']}"
                )


# ==================================================================
#  6. UNİVERSE RESOLUTION / STABILITY SWEEP
# ==================================================================

class TestStabilityAndResolution:
    """Kritik sınırlar civarında stability sweep."""

    def test_score_stability_near_tbdy_boundary(self):
        """TBDY sınırı (25 MPa) civarında raw skor kararlı mı?

        NOT: MF transition gap bölgesinde (strength 20-25 arası, low→medium geçişi)
        raw skor doğal olarak hızlı değişir. Bu trapmf/trimf tasarımının sonucudur.
        Tolerance 8.0: gap bölgesini kapsar, gerçek anomalileri yakalar.
        """
        fixed_c = -200.0
        fixed_sr = 15.0
        strengths = [24.0, 24.5, 24.9, 25.0, 25.1, 25.5, 26.0]
        scores = []
        for s in strengths:
            result = compute_health_v2(s, fixed_c, fixed_sr, s)
            scores.append((s, result["raw_score"], result["capped_score"]))

        # Raw skor'lar MF geçişinde hızlı değişebilir; büyük sıçrama (>8) olmamalı
        MF_TRANSITION_TOLERANCE = 8.0
        for i in range(1, len(scores)):
            raw_diff = abs(scores[i][1] - scores[i - 1][1])
            assert raw_diff < MF_TRANSITION_TOLERANCE, (
                f"TBDY sınırında aşırı raw skor sıçraması: "
                f"{scores[i-1][0]}→{scores[i][0]}: {scores[i-1][1]:.2f}→{scores[i][1]:.2f}"
            )

    def test_score_stability_near_astm_boundary(self):
        """ASTM sınırı (-350 mV) civarında skor kararlı mı?"""
        fixed_s = 35.0
        fixed_sr = 15.0
        corrosions = [-360, -355, -352, -350, -348, -345, -340]
        scores = []
        for c in corrosions:
            result = compute_health_v2(fixed_s, float(c), fixed_sr, fixed_s)
            scores.append((c, result["raw_score"], result["capped_score"]))

        for i in range(1, len(scores)):
            raw_diff = abs(scores[i][1] - scores[i - 1][1])
            assert raw_diff < 5.0, (
                f"ASTM sınırında büyük raw skor sıçraması: "
                f"{scores[i-1][0]}→{scores[i][0]}: {scores[i-1][1]:.2f}→{scores[i][1]:.2f}"
            )

    def test_mf_overlap_coverage(self):
        """Her noktada en az bir MF aktif olmalı.

        NOT: trapmf/trimf gap bölgelerinde (ör: strength 16-19) MF toplamı
        1.0'ın altına düşebilir — bu fuzzy tasarımın doğal sonucudur,
        hesaplama hatasına neden olmaz. Asıl kontrol: hiçbir noktada
        toplam 0'a düşmemeli (yani her zaman en az bir kural ateşlenebilmeli).
        """
        # Strength axis — gap bölgeleri (15-20, 40-50 arası) sum < 1.0
        for val in range(0, 81, 1):
            total = sum(
                _compute_membership(float(val), mf["params"], mf["type"])
                for mf in _INPUT_MF_DEFS["strength"].values()
            )
            assert total > 0.0, f"Strength={val}: hiçbir MF aktif değil!"
            # Core bölgelerde (MF tepelerinde) sum yaklaşık 1.0
            if val in [0, 10, 35, 55, 70, 80]:
                assert 0.8 <= total <= 1.2, (
                    f"Strength={val} (core): MF toplamı={total:.3f}"
                )

        # Corrosion axis
        for val in range(-600, 101, 10):
            total = sum(
                _compute_membership(float(val), mf["params"], mf["type"])
                for mf in _INPUT_MF_DEFS["corrosion"].values()
            )
            assert total > 0.0, f"Corrosion={val}: hiçbir MF aktif değil!"

        # Survey axis
        for val in range(0, 51, 1):
            total = sum(
                _compute_membership(float(val), mf["params"], mf["type"])
                for mf in _INPUT_MF_DEFS["survey_risk"].values()
            )
            assert total > 0.0, f"Survey={val}: hiçbir MF aktif değil!"


# ==================================================================
#  7. CAP KALİBRASYON DEĞERLENDİRMESİ
# ==================================================================

class TestCapCalibration:
    """CAP_SINGLE ve CAP_DUAL provisional değerlerinin makul olduğunu doğrula."""

    def test_cap_single_within_bad_band(self):
        """CAP_SINGLE, Bad bandı içinde olmalı (20-50 arası)."""
        assert 20 <= CAP_SINGLE <= 50, (
            f"CAP_SINGLE={CAP_SINGLE} Bad bandı dışında"
        )

    def test_cap_dual_within_very_bad_band(self):
        """CAP_DUAL, Very Bad / Bad sınırında olmalı (10-30 arası)."""
        assert 10 <= CAP_DUAL <= 30, (
            f"CAP_DUAL={CAP_DUAL} Very Bad/Bad sınırı dışında"
        )

    def test_cap_dual_less_than_cap_single(self):
        """CAP_DUAL < CAP_SINGLE olmalı."""
        assert CAP_DUAL < CAP_SINGLE

    def test_cap_single_matches_label_expectation(self):
        """CAP_SINGLE → get_fuzzy_label Bad bandında olmalı."""
        label = get_fuzzy_label(float(CAP_SINGLE))
        assert "Bad" in label or "Kötü" in label, (
            f"CAP_SINGLE={CAP_SINGLE} label={label}, Bad bekleniyor"
        )

    def test_cap_dual_matches_label_expectation(self):
        """CAP_DUAL → get_fuzzy_label Very Bad veya Bad sınırında olmalı.

        NOT: CAP_DUAL=25, label sınırı tam eşikte (<25 = Very Bad, >=25 = Bad).
        Bu tasarım gereği — "en kötü Bad" seviyesinde kilitliyor.
        Saha verisiyle kalibre edilene kadar bu pozisyon korunuyor.
        """
        label = get_fuzzy_label(float(CAP_DUAL))
        assert "Bad" in label or "Kötü" in label, (
            f"CAP_DUAL={CAP_DUAL} label={label}, Bad/Very Bad bekleniyor"
        )

    def test_raw_score_range_for_low_strength_low_corrosion(self):
        """Düşük beton + yüksek korozyon senaryosunda raw skor cap'ten düşük mü?"""
        result = compute_health_v2(5.0, -500.0, 48.0, 5.0)
        # En kötü senaryoda raw skor zaten CAP_DUAL civarında veya altında olmalı
        assert result["raw_score"] <= CAP_DUAL + 15, (
            f"En kötü senaryo raw_score={result['raw_score']}, "
            f"CAP_DUAL={CAP_DUAL} ile çok fazla fark"
        )


# ==================================================================
#  STANDALONE RUNNER
# ==================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
