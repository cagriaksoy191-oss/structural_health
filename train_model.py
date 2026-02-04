from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
import joblib

# 1) Kullanacağımız CSV
# 1) Kullanacağımız CSV
DATA_FILE = Path("ana_veri.csv")

def main():
    # --- Dosya var mı? ---
    if not DATA_FILE.exists():
        print(f"HATA: {DATA_FILE} dosyası bulunamadı.")
        print("Lütfen önce 'integrate_anfis_and_train.py' dosyasını çalıştırın.")
        return

    # --- CSV'yi oku ---
    df = pd.read_csv(DATA_FILE)

    if "gercekEtiket" not in df.columns:
        print("HATA: CSV dosyasında 'gercekEtiket' sütunu yok.")
        return

    # --- Hedef ve özellikleri ayır ---
    y = df["gercekEtiket"].astype(str).str.strip()
    X = df.drop(columns=["gercekEtiket"])

    # Sayısal ve kategorik kolonları ayır
    # basincDayanimi, ultrasonikSesHizi, geriSicramaSayisi EKLENDİ
    numeric_features = ["yapimYili", "katSayisi", "basincDayanimi", "ultrasonikSesHizi", "geriSicramaSayisi"]
    categorical_features = [c for c in X.columns if c not in numeric_features]

    print("Sayısal özellikler:", numeric_features)
    print("Kategorik özellikler:", categorical_features)

    # --- Ön işleme + model pipeline ---
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

    # --- Train / test ayır ---
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,   # sınıflar dengeli kalsın
    )

    # --- Modeli eğit ---
    print("Model eğitiliyor (RandomForest)...")
    clf.fit(X_train, y_train)

    # --- Test doğruluğu ---
    acc = clf.score(X_test, y_test)
    print(f"Test doğruluğu (accuracy): {acc:.3f}")

    # --- Modeli kaydet ---
    joblib.dump(clf, "risk_model.joblib")
    print("Model 'risk_model.joblib' olarak kaydedildi.")

if __name__ == "__main__":
    main()
