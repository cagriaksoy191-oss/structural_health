"""Yapı Sağlığı — Deprem ve Zemin Harita Verileri (Hybrid: AFAD API + Statik Harita)"""

from typing import Dict, Optional
import logging

from services.normalize import normalize_key


# -------------------------------------------------
#  HARİTA VERİLERİ (RAW)
# -------------------------------------------------
DEPREM_RISK_MAP_RAW = {
    "istanbul": {
        "_default": "yüksek",
        "arnavutköy": "düşük",
        "sarıyer": "orta",
        "eyüpsultan": "orta",
        "beykoz": "düşük",
        "şile": "düşük",
        "çatalca": "orta",
        "başakşehir": "orta",
        "avcılar": "yüksek",
        "bakırköy": "yüksek",
        "küçükçekmece": "yüksek",
        "zeytinburnu": "yüksek",
        "fatih": "yüksek",
        "kadıköy": "yüksek",
        "maltepe": "yüksek",
        "kartal": "yüksek",
        "tuzla": "yüksek",
        "pendik": "yüksek",
        "adalar": "yüksek",
        "büyükçekmece": "yüksek",
        "silivri": "yüksek",
        "esenler": "orta",
        "sultangazi": "orta",
    },
    "ankara": {
        "_default": "düşük",
        "elmadağ": "orta",
        "nallıhan": "yüksek",
        "beypazarı": "orta",
        "kazan": "orta",
        "kızılcahamam": "yüksek",
        "çamlıdere": "yüksek",
        "evren": "orta",
        "bala": "orta",
    },
    "izmir": {
        "_default": "yüksek",
        "kiraz": "orta",
        "beydağ": "orta",
        "karaburun": "orta",
    },
    "manisa": {"_default": "yüksek", "demirci": "orta", "gördes": "orta"},
    "aydın": {"_default": "yüksek"},
    "muğla": {"_default": "yüksek", "datça": "orta"},
    "antalya": {
        "_default": "orta",
        "demre": "yüksek",
        "finike": "yüksek",
        "kumluca": "yüksek",
        "kemer": "yüksek",
        "kaş": "yüksek",
        "alanya": "düşük",
        "gündoğmuş": "düşük",
        "gazipaşa": "düşük",
    },
    "adana": {
        "_default": "yüksek",
        "tufanbeyli": "orta",
        "saimbeyli": "orta",
        "pozantı": "orta",
    },
    "hatay": {"_default": "yüksek"},
    "kahramanmaraş": {"_default": "yüksek", "ekinözü": "orta"},
    "erzincan": {"_default": "yüksek"},
    "bingöl": {"_default": "yüksek"},
    "van": {"_default": "yüksek"},
    "diyarbakır": {
        "_default": "orta",
        "lice": "yüksek",
        "hani": "yüksek",
        "çermik": "yüksek",
    },
    "trabzon": {"_default": "düşük", "of": "orta", "hayrat": "orta"},
    "samsun": {
        "_default": "orta",
        "ladik": "yüksek",
        "havza": "yüksek",
        "vezirköprü": "yüksek",
        "kavak": "yüksek",
        "bafra": "düşük",
        "alaçam": "düşük",
    },
    "kocaeli": {"_default": "yüksek", "kandıra": "orta"},
    "sakarya": {"_default": "yüksek"},
    "yalova": {"_default": "yüksek"},
    "bursa": {
        "_default": "yüksek",
        "büyükorhan": "orta",
        "harmancık": "orta",
        "keles": "orta",
    },
    "tekirdağ": {"_default": "yüksek", "saray": "düşük", "kapaklı": "orta"},
    "balıkesir": {"_default": "yüksek", "kepsut": "orta", "dursunbey": "orta"},
    "çanakkale": {"_default": "yüksek", "bozcaada": "orta"},
    "edirne": {"_default": "düşük", "enez": "orta", "ipsala": "orta"},
    "kırklareli": {"_default": "düşük"},
    "denizli": {"_default": "yüksek"},
    "uşak": {"_default": "orta"},
    "kütahya": {"_default": "yüksek"},
    "afyonkarahisar": {
        "_default": "orta",
        "dinar": "yüksek",
        "çay": "yüksek",
        "sultandağı": "yüksek",
    },
    "eskişehir": {"_default": "orta", "inönü": "yüksek"},
    "konya": {
        "_default": "düşük",
        "akşehir": "yüksek",
        "tuzlukçu": "yüksek",
        "ılgın": "orta",
        "doğanhisar": "orta",
    },
    "kayseri": {"_default": "orta", "yahyalı": "orta", "sarız": "orta"},
    "sivas": {
        "_default": "orta",
        "suşehri": "yüksek",
        "koyulhisar": "yüksek",
        "gölova": "yüksek",
        "akıncılar": "yüksek",
        "divriği": "düşük",
    },
    "aksaray": {"_default": "düşük"},
    "karaman": {"_default": "düşük"},
    "niğde": {"_default": "orta", "bor": "orta"},
    "çankırı": {"_default": "yüksek", "yapraklı": "orta"},
    "kırşehir": {"_default": "orta"},
    "yozgat": {"_default": "orta", "akdağmadeni": "düşük"},
    "mersin": {"_default": "düşük", "tarsus": "orta", "çamlıyayla": "orta"},
    "osmaniye": {"_default": "yüksek"},
    "burdur": {"_default": "yüksek"},
    "isparta": {"_default": "yüksek"},
    "bolu": {"_default": "yüksek", "seben": "orta", "kıbrıscık": "orta"},
    "düzce": {"_default": "yüksek"},
    "zonguldak": {"_default": "düşük", "devrek": "yüksek", "gökçebey": "yüksek"},
    "bartın": {"_default": "düşük", "ulus": "orta"},
    "kastamonu": {"_default": "orta", "tosya": "yüksek", "cide": "düşük"},
    "sinop": {"_default": "düşük", "boyabat": "yüksek", "durağan": "yüksek"},
    "ordu": {"_default": "düşük", "mesudiye": "yüksek", "akkuş": "yüksek"},
    "giresun": {
        "_default": "düşük",
        "alucra": "yüksek",
        "şebinkarahisar": "yüksek",
        "çamoluk": "yüksek",
    },
    "rize": {"_default": "düşük"},
    "artvin": {"_default": "düşük", "yusufeli": "orta"},
    "tokat": {"_default": "yüksek", "artova": "orta"},
    "amasya": {"_default": "yüksek"},
    "çorum": {
        "_default": "orta",
        "osmancık": "yüksek",
        "kargı": "yüksek",
        "mecitözü": "yüksek",
    },
    "tunceli": {"_default": "yüksek", "pülümür": "yüksek"},
    "elazığ": {"_default": "yüksek"},
    "malatya": {"_default": "yüksek"},
    "adıyaman": {"_default": "yüksek"},
    "şanlıurfa": {"_default": "düşük", "bozova": "orta"},
    "mardin": {"_default": "düşük"},
    "batman": {"_default": "orta", "sason": "yüksek"},
    "siirt": {"_default": "yüksek"},
    "hakkari": {"_default": "yüksek"},
    "muş": {"_default": "yüksek"},
    "bitlis": {"_default": "yüksek"},
    "ağrı": {"_default": "orta", "patnos": "yüksek", "doğubayazıt": "yüksek"},
    "erzurum": {"_default": "yüksek", "ispir": "orta"},
    "kars": {"_default": "orta", "kağızman": "yüksek"},
    "ığdır": {"_default": "yüksek"},
    "ardahan": {"_default": "orta", "göle": "yüksek"},
}

ZEMIN_SINIF_MAP_RAW = {
    "istanbul": {
        "_default": "Z3",
        "arnavutköy": "Z2",
        "sarıyer": "Z1",
        "avcılar": "Z4",
        "bakırköy": "Z4",
    },
    "ankara": {"_default": "Z2", "etimesgut": "Z4", "gölbaşı": "Z4"},
    "izmir": {"_default": "Z3", "bayraklı": "Z4", "karşıyaka": "Z4"},
}


# -------------------------------------------------
#  HARİTA NORMALİZASYONU (Startup)
# -------------------------------------------------
def normalize_map_keys(raw_map: Dict) -> Dict:
    normalized = {}
    for il, il_data in raw_map.items():
        norm_il = normalize_key(il)
        normalized[norm_il] = {}
        for ilce, val in il_data.items():
            normalized[norm_il][normalize_key(ilce)] = val
    return normalized


DEPREM_RISK_MAP = normalize_map_keys(DEPREM_RISK_MAP_RAW)
ZEMIN_SINIF_MAP = normalize_map_keys(ZEMIN_SINIF_MAP_RAW)


def deprem_seviyesi_bul(il: str, ilce: str) -> str:
    il_key = normalize_key(il)
    ilce_key = normalize_key(ilce)

    il_data = DEPREM_RISK_MAP.get(il_key)
    if not il_data:
        return "orta"
    return il_data.get(ilce_key, il_data.get("_default", "orta"))


def deprem_seviyesi_puan(seviye: str) -> int:
    if seviye == "yüksek":
        return 3
    if seviye == "orta":
        return 1
    return 0


def tahmini_zemin_sinifi(il: str, ilce: str) -> str:
    il_key = normalize_key(il)
    ilce_key = normalize_key(ilce)
    il_data = ZEMIN_SINIF_MAP.get(il_key)
    if not il_data:
        return "Z3"
    return il_data.get(ilce_key, il_data.get("_default", "Z3"))


# -------------------------------------------------
#  HYBRID FONKSİYON (AFAD API + Statik Harita Fallback)
# -------------------------------------------------
logger = logging.getLogger(__name__)


async def deprem_analizi_async(
    il: str,
    ilce: str,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
) -> dict:
    """
    Hybrid deprem analizi: Önce AFAD API'den gerçek veri dener,
    başarısız olursa statik haritaya düşer.

    Returns:
        {
            "seviye": str,     # "yüksek" / "orta" / "düşük"
            "puan": int,       # 0, 1 veya 3
            "pga": float|None, # PGA değeri (g), None ise API çalışmadı veya dürüst fallback yapıldı
            "kaynak": str,     # "AFAD" veya "Statik Harita"
            "events": list,    # AFAD API olay verileri (İç sözleşme taşıması, dış API'ye sızmaz)
            "deprem_sayisi": int
        }
    """
    # Önce baz statik seviyeyi bul
    statik_seviye = deprem_seviyesi_bul(il, ilce)
    statik_puan = deprem_seviyesi_puan(statik_seviye)

    # --- Önce AFAD API'yi dene ---
    try:
        from services.afad_api import calculate_seismic_hazard

        afad_result = await calculate_seismic_hazard(il, ilce, lat, lon)

        if afad_result is not None:
            afad_seviye = afad_result["risk_seviyesi"]
            afad_puan = deprem_seviyesi_puan(afad_seviye)
            afad_events = afad_result.get("events", [])
            deprem_sayisi = afad_result.get("deprem_sayisi", 0)

            # --- Senaryo 3: Honest Fallback (Kalkan) ---
            # AFAD aktivitesi statik haritadan daha düşük bir puan üretiyorsa, statik harita korunur.
            # İç kontrat ile events taşınır ki external HTTP schema earthquakeClasses üretebilsin.
            if statik_puan > afad_puan:
                logger.info(
                    f"Senaryo 3: AFAD düşük aktivite buldu ({afad_seviye}), "
                    f"ancak statik risk daha yüksek ({statik_seviye}). Statik seviyeye çıkılıyor."
                )
                return {
                    "seviye": statik_seviye,
                    "puan": statik_puan,
                    "pga": None,
                    "kaynak": "Statik Harita",
                    "events": afad_events,
                    "deprem_sayisi": deprem_sayisi,
                }

            logger.info(
                f"AFAD veri başarılı: {il}/{ilce} → "
                f"PGA={afad_result['pga']:.4f}g, Seviye={afad_seviye}, "
                f"Kaynak: AFAD ({deprem_sayisi} deprem)"
            )
            return {
                "seviye": afad_seviye,
                "puan": afad_puan,
                "pga": afad_result["pga"],
                "kaynak": "AFAD",
                "events": afad_events,
                "deprem_sayisi": deprem_sayisi,
            }
    except Exception as e:
        logger.warning(f"AFAD API hatası, statik haritaya düşülüyor: {type(e).__name__}")

    # --- Fallback: Statik harita ---
    logger.info(f"Statik harita kullanıldı: {il}/{ilce} → Seviye={statik_seviye}")

    return {
        "seviye": statik_seviye,
        "puan": statik_puan,
        "pga": None,
        "kaynak": "Statik Harita",
        "events": [],
        "deprem_sayisi": 0,
    }

