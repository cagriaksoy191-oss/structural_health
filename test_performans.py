import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import os

# --- 1. DOSYA AYARLARI ---
# CSV dosyanın tam adı
CSV_DOSYA_YOLU = "beton_dataset_final.csv"

# Senin CSV dosyanın içindeki Sütun İsimleri (Dosyana göre güncelledim)
COL_UPV = "UPV"       # Ultrasonik Ses Hızı
COL_RN = "RN"         # Schmidt Çekici
COL_GERCEK = "Fc"     # Gerçek Laboratuvar Sonucu (Dosyanda Fc yazıyor)

# Model Dosyasının Adı 
# DİKKAT: Klasöründeki .pkl dosyasının adı neyse buraya aynısını yaz!
# Genelde concrete_model.pkl, rf_model.pkl veya model.pkl olur.
MODEL_DOSYASI = "concrete_model.joblib" 

# --- 2. MODELİ YÜKLE ---
print("🧠 Yapay Zeka Modeli Yükleniyor...")
# Bu kısım senin "Asıl Formülünü" otomatik çeker.
try:
    if os.path.exists(MODEL_DOSYASI):
        model = joblib.load(MODEL_DOSYASI)
        print(f"✅ Model başarıyla yüklendi: {MODEL_DOSYASI}")
    else:
        print(f"❌ HATA: '{MODEL_DOSYASI}' dosyası bulunamadı!")
        print("Lütfen klasöründeki .pkl uzantılı dosyanın adını koddaki MODEL_DOSYASI kısmına yaz.")
        exit()
except Exception as e:
    print(f"❌ Model yükleme hatası: {e}")
    exit()

# --- 3. TAHMİN FONKSİYONU ---
def yapay_zeka_tahmin(upv, rn):
    # Model senden verileri [UPV, RN] sırasında ister
    veri = [[upv, rn]]  
    sonuc = model.predict(veri)[0] # Yapay zekaya sor
    return max(0, sonuc) # Negatif çıkarsa 0 yap

# --- 4. TEST MOTORU ---
def testi_baslat():
    print(f"📂 Veri seti okunuyor: {CSV_DOSYA_YOLU}")
    
    if not os.path.exists(CSV_DOSYA_YOLU):
        print("❌ HATA: CSV dosyası bulunamadı!")
        return

    try:
        df = pd.read_csv(CSV_DOSYA_YOLU)
        print(f"✅ Toplam {len(df)} bina verisi bulundu.")
    except Exception as e:
        print(f"❌ CSV okuma hatası: {e}")
        return

    gercek_degerler = []
    tahmin_degerler = []

    print("🤖 Analiz başlıyor...")
    
    for index, row in df.iterrows():
        try:
            # CSV'den verileri çek
            upv_val = float(row[COL_UPV])
            rn_val = float(row[COL_RN])
            gercek_val = float(row[COL_GERCEK])

            # Yapay Zekaya Sor
            tahmin = yapay_zeka_tahmin(upv_val, rn_val)

            gercek_degerler.append(gercek_val)
            tahmin_degerler.append(tahmin)
            
        except Exception as e:
            print(f"Satır {index} hatası: {e}")
            continue

    # --- 5. SONUÇLAR VE YATIRIMCI RAPORU ---
    mps = mean_absolute_error(gercek_degerler, tahmin_degerler)
    rms = np.sqrt(mean_squared_error(gercek_degerler, tahmin_degerler))
    r2 = r2_score(gercek_degerler, tahmin_degerler)

    print("\n" + "="*50)
    print("   🏆 YATIRIMCI PERFORMANS RAPORU (V12 TITANIUM) 🏆")
    print("="*50)
    print(f"📊 Test Edilen Bina Sayısı : {len(df)}")
    print(f"📉 MPS (Ortalama Sapma)    : {mps:.2f} MPa  (Düşük olması iyidir)")
    print(f"📈 RMS (Hata Kararlılığı)  : {rms:.2f}      (Düşük olması iyidir)")
    print(f"⭐ R² (Başarı Oranı)       : %{r2*100:.1f}  (Yüksek olması iyidir)")
    print("="*50)

    # Grafik Çiz
    plt.figure(figsize=(10, 6))
    plt.scatter(gercek_degerler, tahmin_degerler, alpha=0.6, color='#2563eb', label='AI Tahminleri')
    plt.plot([min(gercek_degerler), max(gercek_degerler)], [min(gercek_degerler), max(gercek_degerler)], 
             color='red', linestyle='--', linewidth=3, label='Mükemmel Hedef')
    
    plt.title(f'V12 Titanium - Yapay Zeka Doğruluk Testi (R² = %{r2*100:.1f})')
    plt.xlabel('Gerçek Laboratuvar Sonuçları (MPa)')
    plt.ylabel('Yapay Zeka Tahminleri (MPa)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()

if __name__ == "__main__":
    testi_baslat()