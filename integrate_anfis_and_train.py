import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

# Dosya yolları
DATA_FILE = Path("sentetik_bina_verisi.csv")
BETON_FILE = Path("beton_dataset_final.csv")
OUTPUT_FILE = Path("ana_veri.csv")

RISK_MODEL_PATH = "risk_model.joblib"
CONCRETE_MODEL_PATH = "concrete_model.joblib"

def main():
    print("--- Veri Entegrasyonu ve Model Eğitimi Başlıyor ---")

    # 1. Verileri Oku
    if not DATA_FILE.exists():
        print(f"HATA: {DATA_FILE} bulunamadı.")
        return
    if not BETON_FILE.exists():
        print(f"HATA: {BETON_FILE} bulunamadı.")
        return
    
    df_bina = pd.read_csv(DATA_FILE)
    df_beton = pd.read_csv(BETON_FILE)

    print(f"Bina verisi: {len(df_bina)} satır.")
    print(f"Beton verisi: {len(df_beton)} satır.")

    # 2. Beton Verisini Rastgele Örnekle ve Birleştir
    # Her bina için beton veri setinden rastgele bir (UPV, RN, Fc) üçlüsü seçiyoruz.
    # Böylece fiziksel olarak tutarlı veriler kullanmış oluruz.
    
    indices = np.random.choice(df_beton.index, size=len(df_bina), replace=True)
    sampled_beton = df_beton.iloc[indices].reset_index(drop=True)

    # Kolon eşleştirme
    # Beton Dataset: UPV (km/s), RN (Schmidt), Fc (MPa)
    # Hedef: ultrasonikSesHizi, geriSicramaSayisi, basincDayanimi
    
    df_bina["ultrasonikSesHizi"] = sampled_beton["UPV"]
    df_bina["geriSicramaSayisi"] = sampled_beton["RN"]
    df_bina["basincDayanimi"] = sampled_beton["Fc"]

    # 3. Yeni Veriyi Kaydet (ana_veri.csv)
    df_bina.to_csv(OUTPUT_FILE, index=False)
    print(f"Yeni veri seti kaydedildi: {OUTPUT_FILE}")

    # ---------------------------------------------------------
    # 4. Beton Dayanımı Modelini Eğit (UPV, RN -> Fc)
    # ---------------------------------------------------------
    print("Beton dayanımı modeli (ConcreteModel) eğitiliyor...")
    X_conc = df_beton[["UPV", "RN"]]
    y_conc = df_beton["Fc"]

    concrete_model = RandomForestRegressor(n_estimators=100, random_state=42)
    concrete_model.fit(X_conc, y_conc)
    
    joblib.dump(concrete_model, CONCRETE_MODEL_PATH)
    print(f"Beton modeli kaydedildi: {CONCRETE_MODEL_PATH}")

    # ---------------------------------------------------------
    # 5. Risk Modelini Yeniden Eğit (Basınç Dayanımı dahil)
    # ---------------------------------------------------------
    print("Risk modeli yeniden eğitiliyor...")
    
    target_col = "gercekEtiket"
    if target_col not in df_bina.columns:
        print(f"HATA: '{target_col}' sütunu bulunamadı.")
        return

    y = df_bina[target_col].astype(str).str.strip()
    X = df_bina.drop(columns=[target_col])

    # Sayısal ve Kategorik Değişkenler
    numeric_features = ["yapimYili", "katSayisi", "basincDayanimi", "ultrasonikSesHizi", "geriSicramaSayisi"]
    categorical_features = [c for c in X.columns if c not in numeric_features]

    print("Kullanılan Sayısal Özellikler:", numeric_features)
    print("Kullanılan Kategorik Özellikler:", categorical_features)

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", "passthrough", numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ]
    )

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced"
    )

    clf = Pipeline(
        steps=[
            ("preprocess", preprocessor),
            ("model", model),
        ]
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    clf.fit(X_train, y_train)
    acc = clf.score(X_test, y_test)
    print(f"Yeni Risk Modeli Test Doğruluğu: {acc:.3f}")

    joblib.dump(clf, RISK_MODEL_PATH)
    print(f"Risk modeli kaydedildi: {RISK_MODEL_PATH}")

if __name__ == "__main__":
    main()
