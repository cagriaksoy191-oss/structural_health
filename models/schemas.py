"""Yapı Sağlığı — Pydantic Veri Modelleri"""

from typing import List, Optional, Literal
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class RiskRequest(BaseModel):
    il: str
    ilce: Optional[str] = ""

    # Dinamik yıl kontrolü
    yapimYili: int = Field(..., ge=1800)

    @field_validator("yapimYili")
    @classmethod
    def check_year_not_future(cls, v: int):
        current_year = datetime.now().year
        if v > current_year:
            raise ValueError(f"Yapım yılı gelecekte olamaz (En fazla {current_year}).")
        return v

    katSayisi: int = Field(..., ge=1, le=100)

    zeminDukkan: Literal["evet", "hayir"]
    bitisik: Literal["evet", "hayir"]
    hasar: Literal["yok", "hafif", "kolon"]

    kullanimAmaci: Literal["konut", "isyeri", "okul", "hastane", "sanayi", "diger"]

    kisaKolon: Literal["yok", "var", "emin_degil"]
    agirCikma: Literal["yok", "hafif", "buyuk"]
    planTipi: Literal["dikdortgen", "L", "T", "U", "kompleks"]
    bitisikHiza: Optional[Literal["uyumlu", "farkli", "yok"]] = "yok"

    # Beton Girdileri (Pozitif olmalı)
    ultrasonikSesHizi: float = Field(..., gt=0)
    geriSicramaSayisi: float = Field(..., gt=0)

    # Korozyon Girdisi
    # Sınırı Fuzzy'den biraz geniş tuttuk ki aşırı değerlerde hata vermesin, clamp yapıp uyaralım.
    corrosion: float = Field(..., description="Korozyon potansiyeli (mV)")

    # "Otomatik" seçilirse boş gelebilir.
    zeminSinifi: Optional[str] = None

    # Frontend verileri
    crackPuan: Optional[int] = Field(default=None, ge=0, le=3)


class RiskResponse(BaseModel):
    healthScore: int
    genelSeviye: str
    aciklama: str
    depremSeviye: str
    depremPuan: int
    yapisalSeviye: str
    yapisalPuan: int
    toplamYapisalRisk: int
    zeminSinifi: Optional[str]
    basincDayanimi: Optional[float] = None
    detaylar: List[str]

    fuzzyLabel: str
    corrosion: float

    aiEtiket: Optional[str] = None
    aiYorum: Optional[str] = None
