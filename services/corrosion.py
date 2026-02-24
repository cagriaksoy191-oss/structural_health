"""Yapı Sağlığı — ASTM C876 Korozyon Hesaplama"""


def korozyon_olasiligi(mv: float) -> tuple:
    """
    ASTM C876 standardına göre korozyon olasılığını yüzde olarak hesaplar.
    Sürekli (continuous) interpolasyon ile hassas sonuç verir.

    Referans eşikler:
      > -200 mV  → %90+ korozyon YOK
      -200 ~ -350 mV → Belirsiz bölge (lineer interpolasyon)
      < -350 mV  → %90+ korozyon VAR

    Returns: (yuzde: int, seviye: str, renk_kodu: str)
    """
    if mv >= -100:
        yuzde = 5
    elif mv >= -200:
        # -100 → %5,  -200 → %10  (güvenli bölge)
        yuzde = int(5 + ((-100 - mv) / 100) * 5)
    elif mv >= -350:
        # -200 → %10,  -350 → %90  (belirsiz bölge, lineer artış)
        yuzde = int(10 + ((-200 - mv) / 150) * 80)
    elif mv >= -500:
        # -350 → %90,  -500 → %97  (yüksek risk bölgesi)
        yuzde = int(90 + ((-350 - mv) / 150) * 7)
    else:
        yuzde = 98

    yuzde = max(2, min(98, yuzde))  # %2-%98 aralığında tut

    if yuzde <= 15:
        return yuzde, "Düşük", "🟢"
    elif yuzde <= 40:
        return yuzde, "Orta-Düşük", "🟡"
    elif yuzde <= 65:
        return yuzde, "Orta", "🟠"
    elif yuzde <= 85:
        return yuzde, "Yüksek", "🔴"
    else:
        return yuzde, "Çok Yüksek", "🔴"
