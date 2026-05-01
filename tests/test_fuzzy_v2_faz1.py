"""Faz 1 Doğrulama — Fuzzy Engine v2 staged altyapı testleri."""

import sys
import os

# Proje kökünü path'e ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from skfuzzy import control as ctrl


def test_imports():
    """v2 sembolleri import edilebiliyor mu?"""
    from services.fuzzy_engine import (  # noqa: F401
        fuzzy_control_system_v2,
        get_fuzzy_label,
        clamp,
        RULE_MATRIX,
        get_fired_rules,
        apply_policy_caps,
        compute_health_v2,
        ENGINE_VERSION,
        CAP_SINGLE,
        CAP_DUAL,
        TBDY_THRESHOLD,
        ASTM_THRESHOLD,
    )
    print("[OK] Import basarili -- v2 sembolleri yuklu")



def test_rule_matrix():
    """RULE_MATRIX 27 kural, benzersiz ID, gecerli output."""
    from services.fuzzy_engine import RULE_MATRIX

    assert len(RULE_MATRIX) == 27, f"Beklenen 27, gelen {len(RULE_MATRIX)}"
    ids = [r["id"] for r in RULE_MATRIX]
    assert len(set(ids)) == 27, "Tekrar eden kural ID var"

    valid_outputs = {"very_bad", "bad", "medium", "good", "very_good"}
    valid_strengths = {"low", "medium", "high"}
    valid_corrosions = {"high_risk", "medium_risk", "low_risk"}
    valid_surveys = {"safe", "medium", "high"}

    for r in RULE_MATRIX:
        assert r["output"] in valid_outputs, f"{r['id']}: gecersiz output {r['output']}"
        assert r["inputs"]["strength"] in valid_strengths
        assert r["inputs"]["corrosion"] in valid_corrosions
        assert r["inputs"]["survey_risk"] in valid_surveys

    # 3x3x3 = 27 benzersiz kombinasyon
    combos = set()
    for r in RULE_MATRIX:
        combo = (r["inputs"]["strength"], r["inputs"]["corrosion"], r["inputs"]["survey_risk"])
        combos.add(combo)
    assert len(combos) == 27, f"Eksik kombinasyonlar: {27 - len(combos)}"
    print(f"[OK] RULE_MATRIX: 27 kural, benzersiz ID, tam kapsama (3x3x3)")


def test_v2_fuzzy_computation():
    """v2 fuzzy sistemi hesaplama yapiyor mu?"""
    from services.fuzzy_engine import fuzzy_control_system_v2

    sim = ctrl.ControlSystemSimulation(fuzzy_control_system_v2)
    sim.input["strength"] = 35.0
    sim.input["corrosion"] = -200.0
    sim.input["survey_risk"] = 15.0
    sim.compute()
    score = sim.output["health"]
    assert 0 <= score <= 100, f"v2 skor aralik disi: {score}"
    print(f"[OK] v2 fuzzy hesaplama -- skor: {score:.2f}")


def test_get_fired_rules():
    """get_fired_rules dogru aktivasyon dereceleri donduruyor mu?"""
    from services.fuzzy_engine import get_fired_rules

    # Plan ornegi: strength=22, corrosion=-100, survey_risk=13
    fired = get_fired_rules(22.0, -100.0, 13.0, top_n=3)
    assert len(fired) > 0, "Hicbir kural ateslenmedi"
    assert len(fired) <= 3, f"top_n=3 ama {len(fired)} kural dondu"

    # Aktivasyon sirasina gore azalan mi?
    for i in range(len(fired) - 1):
        assert fired[i]["activation"] >= fired[i + 1]["activation"]

    print(f"[OK] get_fired_rules: {len(fired)} kural atesilendi")
    for r in fired:
        print(f"     {r['id']} ({r['output']}): aktivasyon={r['activation']}")

    # Matematik dogrulama (plan ornegi)
    # strength=22: low=0.30, medium=0.1333
    # corrosion=-100: low_risk=1.0
    # survey_risk=13: safe=0.40, medium=0.0769
    rule_ids = [r["id"] for r in fired]
    assert "R09" in rule_ids, "R09 ateslenmeli (low+low_risk+safe)"
    r09 = [r for r in fired if r["id"] == "R09"][0]
    assert abs(r09["activation"] - 0.30) < 0.01, f"R09 aktivasyon hatasi: {r09['activation']}"
    print(f"[OK] R09 aktivasyon dogrulandi: {r09['activation']}")


def test_policy_caps_no_cap():
    """Normal degerler -- cap uygulanmamali."""
    from services.fuzzy_engine import apply_policy_caps

    score, caps = apply_policy_caps(72.0, 35.0, -100.0)
    assert score == 72.0, f"Cap yok ama skor degisti: {score}"
    assert len(caps) == 0, "Cap listesi bos olmali"
    print(f"[OK] Policy cap (cap yok): skor={score}")


def test_policy_caps_tbdy():
    """Dusuk beton dayanimi -- TBDY cap uygulanmali."""
    from services.fuzzy_engine import apply_policy_caps, CAP_SINGLE

    score, caps = apply_policy_caps(62.0, 22.0, -100.0)
    assert score == float(CAP_SINGLE), f"TBDY cap beklenen {CAP_SINGLE}, gelen {score}"
    assert len(caps) == 1
    assert caps[0]["cap_name"] == "TBDY_ONELEME_CAP"
    assert caps[0]["effective"] is True
    assert "karot" in caps[0]["recommendation"].lower()
    print(f"[OK] Policy cap (TBDY, effective=True): {score}, cap={caps[0]['cap_name']}")


def test_policy_caps_astm():
    """Yuksek korozyon -- ASTM cap uygulanmali."""
    from services.fuzzy_engine import apply_policy_caps, CAP_SINGLE

    score, caps = apply_policy_caps(55.0, 35.0, -400.0)
    assert score == float(CAP_SINGLE), f"ASTM cap beklenen {CAP_SINGLE}, gelen {score}"
    assert len(caps) == 1
    assert caps[0]["cap_name"] == "ASTM_C876_CAP"
    assert caps[0]["effective"] is True
    print(f"[OK] Policy cap (ASTM, effective=True): {score}, cap={caps[0]['cap_name']}")


def test_policy_caps_dual():
    """Cift kritik -- CAP_DUAL uygulanmali."""
    from services.fuzzy_engine import apply_policy_caps, CAP_DUAL

    score, caps = apply_policy_caps(38.0, 20.0, -500.0)
    assert score == float(CAP_DUAL), f"Dual cap beklenen {CAP_DUAL}, gelen {score}"
    assert len(caps) == 1
    assert caps[0]["cap_name"] == "CAP_DUAL"
    assert caps[0]["effective"] is True
    print(f"[OK] Policy cap (DUAL, effective=True): {score}, cap={caps[0]['cap_name']}")


def test_policy_caps_ineffective_dual():
    """Cift kritik kosul saglanmis ama skor zaten dusuk -- trace korunmali, effective=False."""
    from services.fuzzy_engine import apply_policy_caps

    score, caps = apply_policy_caps(18.0, 20.0, -400.0)
    assert score == 18.0, f"Skor degismemeli: {score}"
    assert len(caps) == 1, f"Trace korunmali, gelen={len(caps)}"
    assert caps[0]["cap_name"] == "CAP_DUAL"
    assert caps[0]["effective"] is False
    assert caps[0]["original_score"] == 18.0
    assert caps[0]["capped_score"] == 18.0
    assert "karot" in caps[0]["recommendation"].lower()
    print(f"[OK] Policy cap (DUAL etkisiz, effective=False): skor={score}, trace korundu")


def test_policy_caps_ineffective_tbdy():
    """TBDY kosul saglanmis ama skor zaten cap altinda -- trace korunmali."""
    from services.fuzzy_engine import apply_policy_caps

    score, caps = apply_policy_caps(30.0, 22.0, -100.0)
    assert score == 30.0, f"Skor degismemeli: {score}"
    assert len(caps) == 1
    assert caps[0]["cap_name"] == "TBDY_ONELEME_CAP"
    assert caps[0]["effective"] is False
    assert "karot" in caps[0]["recommendation"].lower()
    print(f"[OK] Policy cap (TBDY etkisiz, effective=False): skor={score}, trace korundu")


def test_policy_caps_ineffective_astm():
    """ASTM kosul saglanmis ama skor zaten cap altinda -- trace korunmali."""
    from services.fuzzy_engine import apply_policy_caps

    score, caps = apply_policy_caps(35.0, 40.0, -500.0)
    assert score == 35.0, f"Skor degismemeli: {score}"
    assert len(caps) == 1
    assert caps[0]["cap_name"] == "ASTM_C876_CAP"
    assert caps[0]["effective"] is False
    assert "korozyon" in caps[0]["reason"].lower()
    print(f"[OK] Policy cap (ASTM etkisiz, effective=False): skor={score}, trace korundu")


def test_compute_health_v2_dual_low_score():
    """compute_health_v2: cift kritik + dusuk skor -- trace KAYBOLMAMALI."""
    from services.fuzzy_engine import compute_health_v2

    # strength=5, corrosion=-500, survey=48, MPa=20 --> cift kritik, skor dusuk olacak
    result = compute_health_v2(5.0, -500.0, 48.0, 20.0)
    assert len(result["applied_caps"]) == 1, "Cift kritik trace korunmali"
    cap = result["applied_caps"][0]
    assert cap["cap_name"] == "CAP_DUAL"
    assert "recommendation" in cap
    assert len(cap["recommendation"]) > 0
    print(f"[OK] compute_health_v2 (cift kritik dusuk skor):")
    print(f"     raw={result['raw_score']}, capped={result['capped_score']}")
    print(f"     cap={cap['cap_name']}, effective={cap['effective']}")
    print(f"     recommendation korundu: {cap['recommendation'][:50]}...")


def test_compute_health_v2():
    """Tam v2 pipeline: fuzzy + policy + explainability."""
    from services.fuzzy_engine import compute_health_v2, ENGINE_VERSION

    result = compute_health_v2(22.0, -100.0, 13.0, 22.0)

    assert "raw_score" in result
    assert "capped_score" in result
    assert "label" in result
    assert "applied_caps" in result
    assert "fired_rules" in result
    assert result["engine_version"] == ENGINE_VERSION

    # 22 MPa < 25 --> TBDY cap bekleniyor
    assert len(result["applied_caps"]) > 0, "22 MPa icin TBDY cap bekleniyor"
    assert result["capped_score"] <= 40.0, f"Cap sonrasi skor 40 ustu: {result['capped_score']}"

    print(f"[OK] compute_health_v2 tam pipeline:")
    print(f"     raw={result['raw_score']}, capped={result['capped_score']}")
    print(f"     label={result['label']}")
    print(f"     caps={[c['cap_name'] for c in result['applied_caps']]}")
    print(f"     engine={result['engine_version']}")
    print(f"     top_rules={[(r['id'], r['output'], r['activation']) for r in result['fired_rules']]}")


def test_engine_version():
    """ENGINE_VERSION dogru mu?"""
    from services.fuzzy_engine import ENGINE_VERSION
    assert ENGINE_VERSION == "v2_fuzzy27"
    print(f"[OK] ENGINE_VERSION: {ENGINE_VERSION}")


if __name__ == "__main__":
    tests = [
        test_imports,
        test_rule_matrix,
        test_v2_fuzzy_computation,
        test_get_fired_rules,
        test_policy_caps_no_cap,
        test_policy_caps_tbdy,
        test_policy_caps_astm,
        test_policy_caps_dual,
        test_policy_caps_ineffective_dual,
        test_policy_caps_ineffective_tbdy,
        test_policy_caps_ineffective_astm,
        test_compute_health_v2,
        test_compute_health_v2_dual_low_score,
        test_engine_version,
    ]

    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"[HATA] {t.__name__}: {e}")
            failed += 1

    print()
    print("=" * 50)
    print(f"SONUC: {passed} PASSED, {failed} FAILED")
    print("=" * 50)

    if failed > 0:
        sys.exit(1)
