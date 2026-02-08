# V12 Titanium – Sismik Değerlendirme Modülü Geliştirme Planı

**Tarih:** 07.02.2026  
**Durum:** Onay Bekliyor  
**Referans Belge:** *Seismic Evaluation and Strengthening of Existing Buildings* (IITK-GSDMA Guidelines)

Bu doküman, V12 Titanium projesini standart bir ön tarama aracından, uluslararası mühendislik normlarına (IITK-GSDMA / FEMA) uygun, bilimsel tabanlı bir **"Yapısal Sağlık Analiz Platformu"**na dönüştürmek için yapılacak 4 kritik geliştirmeyi içerir.

---

## 🚀 Geliştirme Özeti (Mahşerin 4 Atlısı)

Aşağıdaki 4 madde, yapısal risk analizinin doğruluğunu %100'e yakın oranda artıracak "Kırmızı Çizgi" kurallarıdır.

| Önem Sırası | Özellik | Mühendislik Tanımı | Etki (Puan/Ceza) |
| :--- | :--- | :--- | :--- |
| **1. (100/100)** | **Bilgi Güvenilirlik Katsayısı (K)** | Knowledge Factor | Beton Dayanımını **%25 Düşürür** |
| **2. (98/100)** | **Yük Yolu Sürekliliği** | Load Path Continuity | Risk Puanına **+15 Ceza** (Kritik) |
| **3. (90/100)** | **Çekiçleme Etkisi** | Pounding Effect | Risk Puanına **+5 Ceza** (Artırıldı) |
| **4. (85/100)** | **Kütle Düzensizliği** | Mass Irregularity | Risk Puanına **+3 Ceza** |

---

## 🛠️ Detaylı Uygulama Planı

### 1. Bilgi Güvenilirlik Katsayısı (Knowledge Factor)
**Kaynak:** *PDF Sayfa 14 / Tablo 1*

**Problem:** Mevcut sistemde kullanıcı "Betonum C30" dediğinde, sistem bunu kesin doğru kabul eder. Ancak projesi ve zemin etüdü olmayan bir binada C30 beton, güvenilirlik belirsizliğinden dolayı C22.5 gibi davranır.
**Çözüm:** Kullanıcının elindeki veri/proje durumuna göre sistem otomatik bir "Güvenlik Çarpanı (K)" uygular.

*   **Frontend (Arayüz):**
    *   Forma eklenecek soru: **"Binanın Statik / Mimari Projesi Mevcut mu?"**
    *   Seçenekler:
        *   `Evet (Tamamına sahibim)` -> K = 1.00
        *   `Kısmen / Emin Değilim` -> K = 0.85
        *   `Hayır / Hiçbir Belge Yok` -> K = 0.75 (**Varsayılan**)

*   **Backend (Mantık):**
    ```python
    # Pseudo-code
    beton_dayanimi = tahmin_beton_dayanimi(upv, schmidt)
    if proje_durumu == "yok":
        beton_dayanimi = beton_dayanimi * 0.75  # Ciddi ceza
    ```

---

### 2. Yük Yolu Sürekliliği (Load Path)
**Kaynak:** *PDF Sayfa 94 / Tablo 1.1 - Madde 1* ve *Sayfa 18*

**Problem:** Bir binanın en hayati özelliği, yükü çatıdan temele kesintisiz aktarmasıdır. Bir katta kolon var, alt katta yoksa (saplama kiriş/kesik kolon), o bina beton kalitesi ne olursa olsun yıkılma riski taşır.
**Çözüm:** Bu durumu tespit edip binayı direkt "Yüksek Risk" kategorisine itmek.

*   **Frontend (Arayüz):**
    *   Forma eklenecek soru: **"Kolonlar temelden çatıya kadar kesintisiz ve aynı hizada devam ediyor mu?"**
    *   *Açıklama:* "Alt katta olup üstte olmayan veya kaydırılmış kolon var mı?"
    *   Seçenekler: `Evet (Düzenli)` / `Hayır (Düzensiz / Kesik)`

*   **Backend (Mantık):**
    ```python
    if yuk_yolu == "duzensiz":
        yapisal_risk_puani += 15  # Bu tek başına binayı "Orta"dan "Yüksek" riske atabilir.
        detaylar.append("KRİTİK: Yük Yolu Düzensizliği (Load Path Failure) tespit edildi.")
    ```

---

### 3. Çekiçleme Etkisi (Pounding Effect)
**Kaynak:** *PDF "Pounding" Uyarıları* (Mevcut özellik güçlendiriliyor)

**Problem:** Bitişik nizam binalarda, kat döşemeleri (tabliyeler) farklı hizadaysa, deprem anında yan binanın döşemesi bizim binanın kolonunun ortasına balyoz gibi vurur ve kolonu keser. Mevcut sistemde buna sadece +2 puan veriyorduk, bu yetersiz.
**Çözüm:** Cezanın caydırıcılığını artırmak.

*   **Frontend (Arayüz):**
    *   Mevcut soru korunacak: *"Bitişik Binayla Kat Hizası"* -> `Farklı` seçilirse.

*   **Backend (Mantık):**
    ```python
    if bitisik_hiza == "farkli":
        yapisal_risk_puani += 5  # Eski değer 2 idi. %150 artırıldı.
        detaylar.append("CİDDİ RİSK: Bitişik bina ile döşeme seviyeleri farklı (Çekiçleme Riski).")
    ```

---

### 4. Kütle Düzensizliği (Mass Irregularity)
**Kaynak:** *PDF Sayfa 29 / Madde 6.4.3*

**Problem:** Binanın belirli bir katında (genelde çatı veya bodrum) normalden çok daha fazla ağırlık olması (Su deposu, dev arşivler, ağır makineler), deprem kuvvetlerinin o kata odaklanmasına neden olur.
**Çözüm:** Ekstra yükü risk puanına yansıtmak.

*   **Frontend (Arayüz):**
    *   Forma eklenecek soru (Checkbox): **"Binada, diğer katlardan belirgin şekilde daha ağır bir kat (Su deposu, ağır makine, arşiv vb.) var mı?"**

*   **Backend (Mantık):**
    ```python
    if kutle_duzensizligi == "var":
        yapisal_risk_puani += 3
        detaylar.append("Kütle Düzensizliği: Ağır yükler tespit edildi.")
    ```

---

## ✅ Sonuç ve Beklenti

Bu plan uygulandığında V12 Titanium:
1.  **Daha "Acımasız" ama Gerçekçi Olacak:** Projesi olmayan eski binalar artık "Orta Risk" yerine hak ettikleri "Yüksek Risk" bandında çıkacak.
2.  **Mühendislik Standartlarına Uyacak:** IITK-GSDMA ve FEMA standartlarındaki en kritik checklist maddelerini kapsayacak.
3.  **Güven Verecek:** Kullanıcıya "Bunu neden sordun?" dediğinde "Uluslararası standartlar gereği" diyebileceğiz.

**Tavsiye:** Ekip onayı sonrası kodlamaya **Madde 1** ve **Madde 2**'den başlanması önerilir.
