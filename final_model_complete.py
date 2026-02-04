import torch
import torch.nn as nn
import numpy as np
import pandas as pd
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from sklearn.preprocessing import MinMaxScaler
from typing import List, Dict, Any


# =============================================================================
# BÖLÜM 1: GWO İLE EĞİTİLMİŞ ANFIS MODELİ (STAGE 1 - MOTOR)
# =============================================================================
class PyTorchANFIS(nn.Module):
    def __init__(self, n_inputs, n_rules):
        super(PyTorchANFIS, self).__init__()
        self.n_inputs = n_inputs
        self.n_rules = n_rules
        self.c = nn.Parameter(torch.randn(n_rules, n_inputs))
        self.sigma = nn.Parameter(torch.abs(torch.randn(n_rules, n_inputs)) + 0.1)
        self.consequent_weights = nn.Parameter(torch.randn(n_rules, n_inputs))
        self.consequent_bias = nn.Parameter(torch.randn(n_rules, 1))

    def forward(self, x):
        x_expanded = x.unsqueeze(1)
        membership = torch.exp(-0.5 * ((x_expanded - self.c) / self.sigma) ** 2)
        w = torch.prod(membership, dim=2, keepdim=True)
        w_sum = torch.sum(w, dim=1, keepdim=True)
        w_norm = w / (w_sum + 1e-8)
        rule_output = (x_expanded * self.consequent_weights.unsqueeze(0)).sum(dim=2,
                                                                              keepdim=True) + self.consequent_bias.unsqueeze(
            0)
        weighted_output = w_norm * rule_output
        final_output = torch.sum(weighted_output, dim=1)
        return final_output


def load_trained_model():
    # Simülasyon amaçlı model yükleme
    model = PyTorchANFIS(n_inputs=2, n_rules=8)
    scaler_x = MinMaxScaler(feature_range=(0.1, 0.9)).fit([[2000, 20], [4500, 60]])
    scaler_y = MinMaxScaler(feature_range=(0.1, 0.9)).fit([[10], [80]])
    return model, scaler_x, scaler_y


# =============================================================================
# BÖLÜM 2: ANKET SKORU HESAPLAMA (STAGE 2 - TALHA'NIN KISMI)
# =============================================================================
def calculate_survey_risk_score(req: Any) -> float:
    skor = 0
    if req.yapimYili <= 1975:
        skor += 5
    elif req.yapimYili <= 1999:
        skor += 4
    elif req.yapimYili <= 2018:
        skor += 2
    else:
        skor += 1

    if req.katSayisi <= 3:
        pass
    elif req.katSayisi <= 5:
        skor += 1
    elif req.katSayisi <= 8:
        skor += 2
    else:
        skor += 4

    if req.zeminDukkan == "evet": skor += 3
    if req.bitisik == "evet": skor += 1

    if req.hasar == "hafif":
        skor += 4
    elif req.hasar == "kolon":
        skor += 8

    if req.kisaKolon == "var":
        skor += 3
    elif req.kisaKolon == "emin_degil":
        skor += 1

    if req.planTipi in ("L", "T", "U"):
        skor += 2
    elif req.planTipi == "kompleks":
        skor += 3

    cp = getattr(req, "crackPuan", 0)
    crack_skor_map = {0: 0, 1: 2, 2: 3, 3: 4}
    skor += crack_skor_map.get(min(cp, 3), 0)

    if getattr(req, "zeminSinifi", "Z2") in ("Z3", "Z4"): skor += 2

    return float(skor)


# =============================================================================
# BÖLÜM 3: 5 SEVİYELİ FUZZY KARAR SİSTEMİ (STAGE 3 - YENİ 5'Lİ MOTOR)
# =============================================================================
def create_final_decision_system():
    # --- GİRDİLER ---
    strength = ctrl.Antecedent(np.arange(0, 81, 1), 'strength')  # MPa
    corrosion = ctrl.Antecedent(np.arange(-600, 101, 1), 'corrosion')  # mV
    survey_risk = ctrl.Antecedent(np.arange(0, 46, 1), 'survey_risk')  # Skor

    # --- ÇIKTI (5 SEVİYE - YENİ!) ---
    health = ctrl.Consequent(np.arange(0, 101, 1), 'health')

    # --- INPUT ÜYELİK FONKSİYONLARI ---
    strength['low'] = fuzz.trapmf(strength.universe, [0, 0, 15, 25])
    strength['medium'] = fuzz.trimf(strength.universe, [20, 35, 50])
    strength['high'] = fuzz.trapmf(strength.universe, [40, 55, 80, 80])

    corrosion['high_risk'] = fuzz.trapmf(corrosion.universe, [-600, -600, -400, -300])  # Veto Bölgesi
    corrosion['medium_risk'] = fuzz.trimf(corrosion.universe, [-400, -275, -150])
    corrosion['low_risk'] = fuzz.trapmf(corrosion.universe, [-200, -100, 100, 100])

    survey_risk['safe'] = fuzz.trapmf(survey_risk.universe, [0, 0, 8, 12])
    survey_risk['medium'] = fuzz.trimf(survey_risk.universe, [10, 20, 30])
    survey_risk['high'] = fuzz.trapmf(survey_risk.universe, [25, 35, 45, 45])

    # --- OUTPUT ÜYELİK FONKSİYONLARI (5 SEVİYE) ---
    # 1. VERY BAD (Çok Kötü): 0-25
    health['very_bad'] = fuzz.trimf(health.universe, [0, 0, 25])
    # 2. BAD (Kötü): 20-45
    health['bad'] = fuzz.trimf(health.universe, [20, 35, 50])
    # 3. MEDIUM (Orta): 45-65
    health['medium'] = fuzz.trimf(health.universe, [45, 55, 65])
    # 4. GOOD (İyi): 60-85
    health['good'] = fuzz.trimf(health.universe, [60, 75, 90])
    # 5. VERY GOOD (Çok İyi): 80-100
    health['very_good'] = fuzz.trimf(health.universe, [80, 100, 100])

    # --- KURALLAR (5 SEVİYELİ MANTIK) ---

    # 1. VERY BAD (Acil Durumlar - Veto)
    # Korozyon Çok Yüksekse YA DA (Beton Kötü VE Bina Riskli)
    rule_very_bad = ctrl.Rule(
        (corrosion['high_risk']) |
        (strength['low'] & survey_risk['high']) |
        (strength['low'] & corrosion['medium_risk']),
        health['very_bad']
    )

    # 2. BAD (Kötü - Ağır Hasarlı)
    # Korozyon Orta ama Beton Kötü, veya Beton Orta ama Bina Riskli
    rule_bad = ctrl.Rule(
        (strength['low'] & survey_risk['medium'] & corrosion['low_risk']) |
        (strength['medium'] & survey_risk['high'] & corrosion['low_risk']) |
        (corrosion['medium_risk'] & strength['medium']),
        health['bad']
    )

    # 3. MEDIUM (Orta - Riskli)
    # Her şeyin ortalama olduğu veya birinin iyi diğerinin kötü olduğu durumlar
    rule_medium = ctrl.Rule(
        (strength['medium'] & survey_risk['medium'] & corrosion['low_risk']) |
        (strength['high'] & survey_risk['high'] & corrosion['low_risk']) |
        (corrosion['medium_risk'] & strength['high']),
        health['medium']
    )

    # 4. GOOD (İyi - Hafif Kusurlu)
    # Beton İyi, Korozyon Yok ama Anket Orta
    rule_good = ctrl.Rule(
        (strength['high'] & survey_risk['medium'] & corrosion['low_risk']) |
        (strength['medium'] & survey_risk['safe'] & corrosion['low_risk']),
        health['good']
    )

    # 5. VERY GOOD (Çok İyi - Sağlam)
    # Her şey mükemmel
    rule_very_good = ctrl.Rule(
        (strength['high'] & survey_risk['safe'] & corrosion['low_risk']),
        health['very_good']
    )

    system = ctrl.ControlSystem([rule_very_bad, rule_bad, rule_medium, rule_good, rule_very_good])
    return ctrl.ControlSystemSimulation(system)


# =============================================================================
# BÖLÜM 4: TEST VE KOŞTURMA
# =============================================================================
class BuildingRequest:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def run_evaluation():
    print("--- 5 SEVİYELİ BİNA SAĞLIK SİSTEMİ TESTİ ---")

    # SENARYO: Beton C50 (İyi), Korozyon -150 (Orta-İyi arası), Anket 15 (Orta)
    req = BuildingRequest(
        yapimYili=1995, katSayisi=5, zeminDukkan="hayir", bitisik="hayir",
        hasar="hafif", kisaKolon="yok", planTipi="duzenli", crackPuan=1, zeminSinifi="Z2"
    )

    survey_score = calculate_survey_risk_score(req)
    estimated_fc = 50.0  # Örnek C50 Beton

    fuzzy_sim = create_final_decision_system()

    fuzzy_sim.input['strength'] = estimated_fc
    fuzzy_sim.input['corrosion'] = -150
    fuzzy_sim.input['survey_risk'] = survey_score

    fuzzy_sim.compute()
    score = fuzzy_sim.output['health']

    print(f"Anket Risk Skoru: {survey_score}")
    print(f"Tahmini Dayanım: {estimated_fc} MPa")
    print(f"Korozyon Değeri: -150 mV")
    print(f"Global Sağlık Endeksi: {score:.2f}/100")
    print("-" * 30)

    # 5'Lİ ÇIKTIYA GÖRE YORUMLAMA
    if score < 25:
        print("SONUÇ: ⚫ VERY BAD (Çok Kötü - Acil)")
    elif score < 45:
        print("SONUÇ: 🔴 BAD (Kötü - Güçlendirme)")
    elif score < 65:
        print("SONUÇ: 🟡 MEDIUM (Orta - İnceleme)")
    elif score < 85:
        print("SONUÇ: 🔵 GOOD (İyi - Bakım)")
    else:
        print("SONUÇ: 🟢 VERY GOOD (Çok İyi - Sağlam)")


if __name__ == "__main__":
    run_evaluation()