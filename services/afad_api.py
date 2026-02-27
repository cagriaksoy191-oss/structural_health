"""Yapı Sağlığı — AFAD Deprem Tehlike Haritası API Entegrasyonu

AFAD Event API (deprem.afad.gov.tr) üzerinden gerçek zamanlı deprem verisi çeker.
Bölgesel deprem yoğunluğundan yaklaşık PGA (Peak Ground Acceleration) hesaplar.
In-memory cache ile aynı sorguları önbelleğe alır.
"""

import math
import time
import os
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple, List

import httpx

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
#  KONFİGÜRASYON
# ─────────────────────────────────────────────
AFAD_API_BASE = "https://deprem.afad.gov.tr/apiv2/event/filter"
AFAD_TIMEOUT = 10  # saniye
AFAD_CACHE_TTL = int(os.getenv("AFAD_CACHE_TTL", "3600"))  # varsayılan 1 saat

# ─────────────────────────────────────────────
#  IN-MEMORY CACHE
# ─────────────────────────────────────────────
_cache: Dict[str, dict] = {}


def _cache_key(il: str, ilce: str) -> str:
    return f"{il.lower().strip()}:{ilce.lower().strip()}"


def cache_get(il: str, ilce: str) -> Optional[dict]:
    """Cache'den veri al. TTL geçmişse None döner."""
    key = _cache_key(il, ilce)
    entry = _cache.get(key)
    if entry and (time.time() - entry["timestamp"]) < AFAD_CACHE_TTL:
        logger.info(f"AFAD cache HIT: {key}")
        return entry["data"]
    if entry:
        del _cache[key]  # süresi dolmuş
    return None


def cache_set(il: str, ilce: str, data: dict) -> None:
    """Cache'e veri yaz."""
    key = _cache_key(il, ilce)
    _cache[key] = {"data": data, "timestamp": time.time()}
    logger.info(f"AFAD cache SET: {key}")


# ─────────────────────────────────────────────
#  İL/İLÇE → KOORDİNAT TABLOSU (81 İL MERKEZİ)
# ─────────────────────────────────────────────
CITY_COORDINATES: Dict[str, Tuple[float, float]] = {
    "adana": (37.0000, 35.3213),
    "adiyaman": (37.7648, 38.2786),
    "afyonkarahisar": (38.7507, 30.5567),
    "agri": (39.7191, 43.0503),
    "aksaray": (38.3687, 34.0370),
    "amasya": (40.6499, 35.8353),
    "ankara": (39.9208, 32.8541),
    "antalya": (36.8969, 30.7133),
    "ardahan": (41.1105, 42.7022),
    "artvin": (41.1828, 41.8183),
    "aydin": (37.8560, 27.8416),
    "balikesir": (39.6484, 27.8826),
    "bartin": (41.6344, 32.3375),
    "batman": (37.8812, 41.1351),
    "bayburt": (40.2552, 40.2249),
    "bilecik": (40.0567, 30.0665),
    "bingol": (38.8854, 40.4966),
    "bitlis": (38.4006, 42.1095),
    "bolu": (40.7318, 31.6061),
    "burdur": (37.7208, 30.2908),
    "bursa": (40.1826, 29.0665),
    "canakkale": (40.1553, 26.4142),
    "cankiri": (40.6013, 33.6134),
    "corum": (40.5506, 34.9556),
    "denizli": (37.7765, 29.0864),
    "diyarbakir": (37.9144, 40.2306),
    "duzce": (40.8438, 31.1565),
    "edirne": (41.6818, 26.5623),
    "elazig": (38.6810, 39.2264),
    "erzincan": (39.7500, 39.5000),
    "erzurum": (39.9000, 41.2700),
    "eskisehir": (39.7767, 30.5206),
    "gaziantep": (37.0662, 37.3833),
    "giresun": (40.9128, 38.3895),
    "gumushane": (40.4386, 39.5086),
    "hakkari": (37.5744, 43.7408),
    "hatay": (36.4018, 36.3498),
    "igdir": (39.9167, 44.0500),
    "isparta": (37.7648, 30.5566),
    "istanbul": (41.0082, 28.9784),
    "izmir": (38.4192, 27.1287),
    "kahramanmaras": (37.5858, 36.9371),
    "karabuk": (41.2061, 32.6204),
    "karaman": (37.1759, 33.2287),
    "kars": (40.6167, 43.1000),
    "kastamonu": (41.3887, 33.7827),
    "kayseri": (38.7312, 35.4787),
    "kilis": (36.7184, 37.1212),
    "kirikkale": (39.8468, 33.5153),
    "kirklareli": (41.7333, 27.2167),
    "kirsehir": (39.1425, 34.1709),
    "kocaeli": (40.8533, 29.8815),
    "konya": (37.8667, 32.4833),
    "kutahya": (39.4167, 29.9833),
    "malatya": (38.3552, 38.3095),
    "manisa": (38.6191, 27.4289),
    "mardin": (37.3212, 40.7245),
    "mersin": (36.8000, 34.6333),
    "mugla": (37.2153, 28.3636),
    "mus": (38.9462, 41.7539),
    "nevsehir": (38.6939, 34.6857),
    "nigde": (37.9667, 34.6833),
    "ordu": (40.9839, 37.8764),
    "osmaniye": (37.0742, 36.2464),
    "rize": (41.0201, 40.5234),
    "sakarya": (40.6940, 30.4358),
    "samsun": (41.2928, 36.3313),
    "sanliurfa": (37.1591, 38.7969),
    "siirt": (37.9333, 41.9500),
    "sinop": (42.0231, 35.1531),
    "sirnak": (37.4187, 42.4918),
    "sivas": (39.7477, 37.0179),
    "tekirdag": (40.9833, 27.5167),
    "tokat": (40.3167, 36.5500),
    "trabzon": (41.0015, 39.7178),
    "tunceli": (39.1079, 39.5401),
    "usak": (38.6823, 29.4082),
    "van": (38.4891, 43.3800),
    "yalova": (40.6500, 29.2667),
    "yozgat": (39.8181, 34.8147),
    "zonguldak": (41.4564, 31.7987),
}


def get_city_coordinates(il: str, ilce: str = "") -> Optional[Tuple[float, float]]:
    """İl adından merkez koordinatını döndürür."""
    from services.normalize import normalize_key
    il_key = normalize_key(il)
    return CITY_COORDINATES.get(il_key)


# ─────────────────────────────────────────────
#  AFAD EVENT API SORGUSU
# ─────────────────────────────────────────────
async def get_afad_earthquakes(
    lat: float,
    lon: float,
    radius_km: float = 250.0,
    days: int = 365,
    min_mag: float = 3.0,
) -> List[dict]:
    """
    AFAD Event API'den belirli bir nokta çevresindeki son depremleri çeker.

    Args:
        lat, lon: Merkez koordinatı
        radius_km: Arama yarıçapı (km)
        days: Kaç günlük veri çekilecek
        min_mag: Minimum büyüklük filtresi

    Returns:
        Deprem listesi (dict). Boş liste: hata veya veri bulunamadı.
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    # Yarıçapı derece cinsine çevir (yaklaşık)
    delta_deg = radius_km / 111.0

    params = {
        "start": start_date.strftime("%Y-%m-%d 00:00:00"),
        "end": end_date.strftime("%Y-%m-%d 23:59:59"),
        "minlat": lat - delta_deg,
        "maxlat": lat + delta_deg,
        "minlon": lon - delta_deg,
        "maxlon": lon + delta_deg,
        "minmag": min_mag,
        "format": "json",
    }

    try:
        async with httpx.AsyncClient(timeout=AFAD_TIMEOUT) as client:
            response = await client.get(AFAD_API_BASE, params=params)
            response.raise_for_status()
            data = response.json()

            if isinstance(data, list):
                logger.info(f"AFAD API: {len(data)} deprem bulundu ({lat:.2f}, {lon:.2f})")
                return data
            else:
                logger.warning(f"AFAD API beklenmeyen format: {type(data)}")
                return []

    except httpx.TimeoutException:
        logger.warning(f"AFAD API timeout ({AFAD_TIMEOUT}s)")
        return []
    except httpx.HTTPStatusError as e:
        logger.warning(f"AFAD API HTTP hatası: {e.response.status_code}")
        return []
    except Exception as e:
        logger.warning(f"AFAD API bağlantı hatası: {e}")
        return []


# ─────────────────────────────────────────────
#  PGA HESAPLAMA (Yaklaşık GMPE)
# ─────────────────────────────────────────────
def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """İki nokta arasındaki mesafeyi km cinsinden hesaplar."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _estimate_pga_from_earthquake(magnitude: float, distance_km: float) -> float:
    """
    Basitleştirilmiş Ground Motion Prediction Equation (GMPE).
    Boore-Atkinson (2008) yaklaşımından esinlenilmiş basitleştirme.

    PGA (g) = 10^(0.35 * M - 1.4 - 1.2 * log10(R + 10))

    NOT: Bu resmi bir GMPE değildir, yaklaşık bir tahmindir.
    Gerçek PGA için TDTH verisi gereklidir.
    """
    if distance_km < 1:
        distance_km = 1.0

    log_pga = 0.35 * magnitude - 1.4 - 1.2 * math.log10(distance_km + 10)
    pga = 10 ** log_pga

    # Fiziksel sınırlar
    return max(0.0, min(pga, 2.0))


def calculate_pga_from_events(
    events: List[dict], target_lat: float, target_lon: float
) -> float:
    """
    Deprem listesinden hedef noktadaki en büyük tahmini PGA'yı hesaplar.
    Her depremin mesafesi ve büyüklüğüne göre PGA tahmin edilir, en yüksek alınır.
    """
    max_pga = 0.0

    for event in events:
        try:
            mag = float(event.get("magnitude", event.get("mag", 0)))
            eq_lat = float(event.get("latitude", event.get("lat", 0)))
            eq_lon = float(event.get("longitude", event.get("lng", 0)))

            if mag < 3.0 or eq_lat == 0 or eq_lon == 0:
                continue

            dist = _haversine_km(target_lat, target_lon, eq_lat, eq_lon)
            pga = _estimate_pga_from_earthquake(mag, dist)

            if pga > max_pga:
                max_pga = pga

        except (ValueError, TypeError):
            continue

    return round(max_pga, 4)


def pga_to_risk_seviyesi(pga: float) -> str:
    """
    PGA değerinden risk seviyesi döndürür.
    TBDY 2018 deprem bölgesi sınırlarından esinlenilmiştir:
      PGA >= 0.40g → "yüksek"
      0.20g <= PGA < 0.40g → "orta"
      PGA < 0.20g → "düşük"
    """
    if pga >= 0.40:
        return "yüksek"
    elif pga >= 0.20:
        return "orta"
    else:
        return "düşük"


# ─────────────────────────────────────────────
#  ANA FONKSİYON: Sismik Tehlike Analizi
# ─────────────────────────────────────────────
async def calculate_seismic_hazard(
    il: str,
    ilce: str = "",
    lat: Optional[float] = None,
    lon: Optional[float] = None,
) -> Optional[dict]:
    """
    AFAD verilerinden sismik tehlike analizi yapar.

    1. Koordinat belirle (verildiyse kullan, yoksa il merkezinden al)
    2. Cache kontrol et
    3. AFAD API'den son depremleri çek
    4. PGA hesapla
    5. Risk seviyesi döndür

    Başarısız olursa None döner (fallback için sinyal).
    """
    # Cache kontrol
    cached = cache_get(il, ilce)
    if cached:
        return cached

    # Koordinat belirle
    if lat is None or lon is None:
        coords = get_city_coordinates(il, ilce)
        if coords is None:
            logger.warning(f"'{il}' için koordinat bulunamadı")
            return None
        lat, lon = coords

    # AFAD API'den depremleri çek
    events = await get_afad_earthquakes(lat, lon)

    if not events:
        logger.info(f"AFAD API: {il}/{ilce} için deprem verisi bulunamadı veya API erişilemedi")
        return None

    # PGA hesapla
    pga = calculate_pga_from_events(events, lat, lon)
    risk_seviyesi = pga_to_risk_seviyesi(pga)

    result = {
        "pga": pga,
        "risk_seviyesi": risk_seviyesi,
        "deprem_sayisi": len(events),
        "kaynak": "AFAD",
        "koordinat": {"lat": lat, "lon": lon},
    }

    # Cache'e yaz
    cache_set(il, ilce, result)

    return result
