"""Yapı Sağlığı — Yapısal Skor Hesaplama"""

from typing import List, Tuple

from models.schemas import RiskRequest


def yapisal_skor_hesapla(req: RiskRequest, zemin_sinifi: str) -> Tuple[int, List[str]]:
    skor = 0
    detaylar: List[str] = []

    if req.yapimYili <= 1975:
        skor += 5
        detaylar.append(f"{req.yapimYili} ve öncesi (+5)")
    elif req.yapimYili <= 1999:
        skor += 4
        detaylar.append(f"{req.yapimYili} – 1999 öncesi (+4)")
    elif req.yapimYili <= 2018:
        skor += 2
        detaylar.append(f"{req.yapimYili} – 2018 öncesi (+2)")
    else:
        skor += 1
        detaylar.append(f"{req.yapimYili} sonrası (+1)")

    if req.katSayisi <= 3:
        detaylar.append(f"{req.katSayisi} kat (+0)")
    elif req.katSayisi <= 5:
        skor += 1
        detaylar.append(f"{req.katSayisi} kat (+1)")
    elif req.katSayisi <= 8:
        skor += 2
        detaylar.append(f"{req.katSayisi} kat (+2)")
    else:
        skor += 4
        detaylar.append(f"{req.katSayisi} kat (+4)")

    # --- YÖNETMELİK: Yüksek Yapı Kontrolü (TBDY 2018) ---
    # 21.50m üzeri (yaklaşık 7+ kat) = Yüksek Yapı → özel kurallar gerektirir
    if req.katSayisi >= 8:
        skor += 2
        detaylar.append(
            f"⚠️ Yüksek Yapı Kategorisi ({req.katSayisi} kat ≥ 8) - TBDY 2018 ek kurallar (+2)"
        )

    if req.zeminDukkan == "evet":
        skor += 3
        detaylar.append("Zemin katta dükkân (+3)")
    if req.bitisik == "evet":
        skor += 1
        detaylar.append("Bitişik nizam (+1)")

    if req.hasar == "hafif":
        skor += 4
        detaylar.append("Hafif hasar (+4)")
    elif req.hasar == "kolon":
        skor += 8
        detaylar.append("Kolon hasarı (+8)")

    if req.kullanimAmaci in ["okul", "hastane"]:
        skor += 2
        detaylar.append(f"Kritik kullanım ({req.kullanimAmaci}) (+2)")

    if req.kisaKolon == "var":
        skor += 3
        detaylar.append("Kısa kolon (+3)")
    elif req.kisaKolon == "emin_degil":
        skor += 1
        detaylar.append("Kısa kolon şüphesi (+1)")

    if req.agirCikma == "buyuk":
        skor += 2
        detaylar.append("Büyük çıkma (+2)")
    elif req.agirCikma == "hafif":
        skor += 1
        detaylar.append("Hafif çıkma (+1)")

    if req.planTipi in ["L", "T", "U"]:
        skor += 2
        detaylar.append(f"Düzensiz plan {req.planTipi} (+2)")
    elif req.planTipi == "kompleks":
        skor += 3
        detaylar.append("Kompleks plan (+3)")

    if req.bitisikHiza == "farkli":
        skor += 2
        detaylar.append("Kat hizası farklı (+2)")

    cp = req.crackPuan
    if cp is not None and cp > 0:
        crack_skor_map = {0: 0, 1: 2, 2: 3, 3: 4}
        crack_skor = crack_skor_map.get(cp, 0)
        skor += crack_skor
        detaylar.append(f"Görsel çatlak analizi: Seviye {cp} (+{crack_skor})")

    if zemin_sinifi in ["Z3", "Z4"]:
        skor += 2
        detaylar.append(f"Zayıf zemin {zemin_sinifi} (+2)")
    elif zemin_sinifi == "Z2":
        skor += 1
        detaylar.append("Orta zemin Z2 (+1)")

    return skor, detaylar


def yapisal_seviye_etiketi(skor: int) -> str:
    if skor <= 5:
        return "Düşük"
    if skor <= 12:
        return "Orta"
    return "Yüksek"
