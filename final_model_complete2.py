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
    # Model yükleme simülasyonu
    model = PyTorchANFIS(n_inputs=2, n_rules=8)
    scaler_x = MinMaxScaler(feature_range=(0.1, 0.9)).fit([[2000, 20], [4500, 60]])
    scaler_y = MinMaxScaler(feature_range=(0.1, 0.9)).fit([[10], [80]])
    return model, scaler_x, scaler_y


# =============================================================================
# BÖLÜM 2: ANKET SKORU HESAPLAMA (STAGE 2 - GÖZLEM / TALHA'NIN KISMI)
# =============================================================================
def calculate_survey_risk_score(req: Any) -> float:
    """
    Kullanıcıdan gelen bina özelliklerine göre 0-40+ arası bir risk skoru üretir.
    """
    skor = 0
    # 1) Yapım yılı
    if req.yapimYili <= 1975:
        skor += 5
    elif req.yapimYili <= 1999:
        skor += 4
    elif req.yapimYili <= 2018:
        skor += 2
    else:
        skor += 1

    # 2) Kat sayısı
    if req.katSayisi <= 3:
        pass
    elif req.katSayisi <= 5:
        skor += 1
    elif req.katSayisi <= 8:
        skor += 2
    else:
        skor += 4

    # 3) Zemin dükkan (Risk artırıcı)
    if req.zeminDukkan == "evet": skor += 3

    # 4) Bitişik nizam
    if req.bitisik == "evet": skor += 1

    # 5) Mevcut hasar durumu
    if req.hasar == "hafif":
        skor += 4
    elif req.hasar == "kolon":
        skor += 8

    # 7) Kısa kolon
    if req.kisaKolon == "var":
        skor += 3
    elif req.kisaKolon == "emin_degil":
        skor += 1

    # 9) Plan düzensizliği
    if req.planTipi in ("L", "T", "U"):
        skor += 2
    elif req.planTipi == "kompleks":
        skor += 3

    # 11) Çatlak analizi
    cp = getattr(req, "crackPuan", 0)
    crack_skor_map = {0: 0, 1: 2, 2: 3, 3: 4}
    skor += crack_skor_map.get(min(cp, 3), 0)

    # 12) Zemin sınıfı
    if getattr(req, "zeminSinifi", "Z2") in ("Z3", "Z4"): skor += 2

    return float(skor)


# =============================================================================
# BÖLÜM 3: HİYERARŞİK FUZZY KARAR SİSTEMİ (STAGE 3 - BEYİN / OPTİMİZE EDİLDİ)
# =============================================================================
def create_final_decision_system():
    # --- GİRDİLER ---
    strength = ctrl.Antecedent(np.arange(0, 81, 1), 'strength')  # MPa (ANFIS'ten)
    corrosion = ctrl.Antecedent(np.arange(-600, 101, 1), 'corrosion')  # mV (Cihazdan)
    survey_risk = ctrl.Antecedent(np.arange(0, 46, 1), 'survey_risk')  # Skor (Anketten)

    # --- ÇIKTI ---
    health = ctrl.Consequent(np.arange(0, 101, 1), 'health')

    # --- ÜYELİK FONKSİYONLARI ---
    # Beton Dayanımı
    strength['low'] = fuzz.trapmf(strength.universe, [0, 0, 15, 25])
    strength['medium'] = fuzz.trimf(strength.universe, [20, 35, 50])
    strength['high'] = fuzz.trapmf(strength.universe, [40, 55, 80, 80])

    # Korozyon (ASTM C876)
    corrosion['high_risk'] = fuzz.trapmf(corrosion.universe, [-600, -600, -400, -300])  # Çok negatif
    corrosion['medium_risk'] = fuzz.trimf(corrosion.universe, [-400, -275, -150])
    corrosion['low_risk'] = fuzz.trapmf(corrosion.universe, [-200, -100, 100, 100])

    # Anket Riski (Talha'nın Skoru)
    survey_risk['safe'] = fuzz.trapmf(survey_risk.universe, [0, 0, 8, 12])
    survey_risk['medium'] = fuzz.trimf(survey_risk.universe, [10, 20, 30])
    survey_risk['high'] = fuzz.trapmf(survey_risk.universe, [25, 35, 45, 45])

    # Global Sağlık İndeksi
    health['critical'] = fuzz.trimf(health.universe, [0, 0, 40])  # Yıkılma Riski
    health['risky'] = fuzz.trimf(health.universe, [30, 50, 70])  # Güçlendirme Gerekli
    health['safe'] = fuzz.trimf(health.universe, [60, 100, 100])  # Sağlam

    # --- OPTİMİZE EDİLMİŞ KURALLAR (RULE BASE) ---
    # Baha'nın isteği üzerine tekrar eden kurallar "OR" (|) operatörü ile birleştirildi.
    # Bu sayede 19 kural yerine 4 ana blok kural ile sistem hızlandı.

    # 1. KURAL: VETO DURUMLARI (KRİTİK)
    # Eğer korozyon çok yüksekse YA DA anket riski tavan yaptıysa YA DA beton çok zayıfsa -> KRİTİK
    # (Eski Rule 1, 7, 9, 10, 13, 15, 16, 17, 18, 19 Birleşimi)
    rule_critical = ctrl.Rule(
        (corrosion['high_risk']) |  # Korozyon Veto
        (strength['low'] & survey_risk['high']) |  # Beton kötü + Bina riskli
        (strength['low'] & survey_risk['medium'] & corrosion['low_risk']) |  # Beton kötü + Bina orta risk
        (corrosion['medium_risk'] & strength['high'] & survey_risk['high']) |
        (corrosion['medium_risk'] & strength['medium'] & survey_risk['medium']) |
        (corrosion['medium_risk'] & strength['medium'] & survey_risk['high']) |
        (corrosion['medium_risk'] & strength['low']),  # Korozyon orta ama beton kötü
        health['critical']
    )

    # 2. KURAL: GÜVENLİ DURUMLAR (SAFE)
    # Beton iyiyse, korozyon düşükse ve bina genel olarak düzgünse -> GÜVENLİ
    # (Eski Rule 2, 4, 5 Birleşimi)
    rule_safe = ctrl.Rule(
        (corrosion['low_risk'] & strength['high'] & survey_risk['safe']) |
        (corrosion['low_risk'] & strength['high'] & survey_risk['medium']) |
        (corrosion['low_risk'] & strength['medium'] & survey_risk['safe']),
        health['safe']
    )

    # 3. KURAL: ARA DURUMLAR (RİSKLİ)
    # Ne çok iyi ne çok kötü, inceleme gereken durumlar
    # (Eski Rule 3, 6, 8, 11, 12, 14 Birleşimi)
    rule_risky = ctrl.Rule(
        (corrosion['low_risk'] & strength['high'] & survey_risk['high']) |
        (corrosion['low_risk'] & strength['medium'] & survey_risk['medium']) |
        (corrosion['low_risk'] & strength['low'] & survey_risk['safe']) |
        (corrosion['medium_risk'] & strength['high'] & survey_risk['safe']) |
        (corrosion['medium_risk'] & strength['high'] & survey_risk['medium']) |
        (corrosion['medium_risk'] & strength['medium'] & survey_risk['safe']),
        health['risky']
    )

    # Sistemi Kur
    system = ctrl.ControlSystem([rule_critical, rule_safe, rule_risky])
    return ctrl.ControlSystemSimulation(system)


# =============================================================================
# BÖLÜM 4: TEST VE KOŞTURMA
# =============================================================================
class BuildingRequest:
    """Veri yapısını simüle eder"""

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def run_evaluation():
    print("--- BİNA SAĞLIK SİSTEMİ BAŞLATILIYOR ---")

    # 1. Bina verilerini al (Örnek: Eski ve hasarlı bir bina)
    req = BuildingRequest(
        yapimYili=1985, katSayisi=7, zeminDukkan="evet", bitisik="evet",
        hasar="kolon", kisaKolon="var", planTipi="L", crackPuan=2, zeminSinifi="Z3"
    )

    # 2. Skorları hesapla
    survey_score = calculate_survey_risk_score(req)

    # 3. Stage 1 Tahmini (GWO-ANFIS Simülasyonu)
    estimated_fc = 75  # MPa (Beton sağlam çıktı diyelim)

    # 4. Fuzzy Karar (Stage 3)
    fuzzy_sim = create_final_decision_system()

    # SENARYO GİRİŞİ:
    # Beton sağlam (75 MPa) ama Korozyon Orta Seviye (-200) ve Bina Anketi Kötü
    fuzzy_sim.input['strength'] = estimated_fc
    fuzzy_sim.input['corrosion'] = -200
    fuzzy_sim.input['survey_risk'] = survey_score

    fuzzy_sim.compute()

    print(f"Anket Risk Skoru: {survey_score}")
    print(f"Tahmini Dayanım: {estimated_fc} MPa")
    print(f"Korozyon Değeri: -200 mV")
    print(f"Global Sağlık Endeksi: {fuzzy_sim.output['health']:.2f}/100")

    # Sonuç Yorumlama
    score = fuzzy_sim.output['health']
    if score < 40:
        print("SONUÇ: 🔴 KRİTİK (Tahliye/Güçlendirme Şart)")
    elif score < 70:
        print("SONUÇ: 🟡 RİSKLİ (Detaylı İnceleme)")
    else:
        print("SONUÇ: 🟢 GÜVENLİ")


if __name__ == "__main__":
    run_evaluation()