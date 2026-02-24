"""Yapı Sağlığı — Fuzzy Logic Sistemi"""

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


def create_fuzzy_system():
    strength = ctrl.Antecedent(np.arange(0, 81, 1), "strength")
    corrosion = ctrl.Antecedent(np.arange(-600, 101, 1), "corrosion")
    survey_risk = ctrl.Antecedent(np.arange(0, 51, 1), "survey_risk")
    health = ctrl.Consequent(np.arange(0, 101, 1), "health")

    strength["low"] = fuzz.trapmf(strength.universe, [0, 0, 15, 25])
    strength["medium"] = fuzz.trimf(strength.universe, [20, 35, 50])
    strength["high"] = fuzz.trapmf(strength.universe, [40, 55, 80, 80])

    corrosion["high_risk"] = fuzz.trapmf(corrosion.universe, [-600, -600, -400, -300])
    corrosion["medium_risk"] = fuzz.trimf(corrosion.universe, [-400, -275, -150])
    corrosion["low_risk"] = fuzz.trapmf(corrosion.universe, [-200, -100, 100, 100])

    survey_risk["safe"] = fuzz.trapmf(survey_risk.universe, [0, 0, 10, 15])
    survey_risk["medium"] = fuzz.trimf(survey_risk.universe, [12, 25, 38])
    survey_risk["high"] = fuzz.trapmf(survey_risk.universe, [30, 40, 50, 50])

    health["very_bad"] = fuzz.trimf(health.universe, [0, 0, 25])
    health["bad"] = fuzz.trimf(health.universe, [20, 35, 50])
    health["medium"] = fuzz.trimf(health.universe, [45, 55, 65])
    health["good"] = fuzz.trimf(health.universe, [60, 75, 90])
    health["very_good"] = fuzz.trimf(health.universe, [80, 100, 100])

    # Kurallar
    rule_very_bad = ctrl.Rule(
        (corrosion["high_risk"])
        | (strength["low"] & survey_risk["high"])
        | (strength["low"] & corrosion["medium_risk"]),
        health["very_bad"],
    )
    rule_bad = ctrl.Rule(
        (strength["low"] & survey_risk["medium"] & corrosion["low_risk"])
        | (strength["medium"] & survey_risk["high"] & corrosion["low_risk"])
        | (corrosion["medium_risk"] & strength["medium"]),
        health["bad"],
    )
    rule_medium = ctrl.Rule(
        (strength["medium"] & survey_risk["medium"] & corrosion["low_risk"])
        | (strength["high"] & survey_risk["high"] & corrosion["low_risk"])
        | (corrosion["medium_risk"] & strength["high"]),
        health["medium"],
    )
    rule_good = ctrl.Rule(
        (strength["high"] & survey_risk["medium"] & corrosion["low_risk"])
        | (strength["medium"] & survey_risk["safe"] & corrosion["low_risk"]),
        health["good"],
    )
    rule_very_good = ctrl.Rule(
        (strength["high"] & survey_risk["safe"] & corrosion["low_risk"]),
        health["very_good"],
    )

    return ctrl.ControlSystem(
        [rule_very_bad, rule_bad, rule_medium, rule_good, rule_very_good]
    )


fuzzy_control_system = create_fuzzy_system()


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
