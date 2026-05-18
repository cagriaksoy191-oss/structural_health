"""Yapı Sağlığı — Qwen3 LLM Entegrasyonu"""

import logging
import httpx

from services.http_client import http_client

logger = logging.getLogger(__name__)


async def get_llm_comment(skor, risk_durumu, beton, korozyon=None, risk_puani=None, dts=None, bys=None, phase2_advice=None, korozyon_metni=None, ana_risk_kaynagi=None):
    # Geriye dönük uyumluluk (Backward Compat)
    if korozyon_metni is None:
        korozyon_metni = f"{korozyon} mV" if korozyon is not None else "Bilinmiyor"
    
    if ana_risk_kaynagi is None:
        ana_risk_kaynagi = "Belirtilmedi"

    # Kullanıcının talebi üzerine model ismi (stale-label temizlendi)
    MODEL_ADI = "qwen3:8b"

    # Kullanıcı verilerini hazırlayalım
    user_message = f"""
    ANALİZ EDİLECEK BİNA VERİLERİ:
    - Yapı Sağlık Skoru: {skor}/100
    - Risk Durumu: {risk_durumu}
    - Beton Dayanımı: {beton} MPa
    - Korozyon Durumu: {korozyon_metni}
    - Genel Risk Puanı: {risk_puani}
    - Deprem Tasarım Sınıfı (DTS): {dts}
    - Bina Yükseklik Sınıfı (BYS): {bys}
    - 2. Aşama Tavsiyesi: {phase2_advice}
    - Ana Risk Sürücüsü: {ana_risk_kaynagi}

    GÖREVİN:
    Yukarıdaki verileri inceleyen uzman bir Türk inşaat mühendisi olarak, bina sahibine yönelik şu formatta, 3-4 cümlelik, GÜVEN VERİCİ, NET ve KISA bir sonuç raporu yaz:

    Örnek Format:
    "Yapı sağlığı skoru 35 ve risk durumu yüksek seviyede; beton dayanımı 18 MPa ve korozyon potansiyeli -450 mV (%95 - Çok Yüksek) olduğu için acil detaylı inceleme şarttır. 2. aşama karot, röntgen gibi yöntemlerle yapının mevcut durumunu netleştirmeniz, gerekli güçlendirme kararlarını almanız açısından kritik. Bu adımları tamamladığınızda iyileştirme ile güvenli bir şekilde kullanıma devam edilebilir."

    DİKKAT (KATI KURALLAR): 
    - Yanıtında KESİNLİKLE "##", "**", "*" gibi Markdown veya özel karakterler KULLANMA. Düz metin olarak yaz.
    - Metin içine KESİNLİKLE "Faz 2:" veya "2. Aşama Tavsiyesi:" gibi alt başlıklar koyma.
    - Sadece tek bir paragraftan oluşan bir metin ver.
    - Aciliyet ("ACİL") veya detaylı inceleme kararı varsa, BUNUN GEREKÇESİNİ SADECE '{ana_risk_kaynagi}' MADDE İLE İLİŞKİLENDİR. 
    - Orta-düşük korozyon gibi tehlikesiz verileri aciliyet sebebi gibi bağlama.
    - -200 ile -350 mV arasındaki korozyon değerlerini "orta", "belirsiz" veya "düşük-orta" risk olarak değerlendir, felaket senaryosu çizme.
    - Korozyon değeri <= -350 mV olmadığı sürece korozyonu BİRİNCİL felaket sebebi gibi gösterme.
    - Beton dayanımı < 25 MPa ise YAPISAL RİSKİN ANA KAYNAĞI OLARAK BETONU VURGULA.
    """

    # Sistem (Rol) Tanımı
    system_message = "Sen uzman bir Türk inşaat mühendisisin. Net ve çok kısa bir özet verirsin."

    try:
        # ARTIK '/api/chat' KULLANIYORUZ (Daha kararlı)
        client = http_client.get_client()
        response = await client.post(
            "http://localhost:11434/api/chat",
            json={
                    "model": MODEL_ADI,
                    "messages": [
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": user_message},
                    ],
                    "stream": False,
                    "options": {
                        "temperature": 0.7
                    },  # Biraz yaratıcılık verelim ki konuşsun
                },
                timeout=120.0,
            )

        if response.status_code == 200:
            # Chat modunda cevap 'message' -> 'content' içindedir
            return response.json()["message"]["content"].strip()
        else:
            logger.warning("Ollama HTTP hatasi: status=%s", response.status_code)
            return (
                "Yapay zeka yorum servisi su anda yanitlamiyor. "
                "Analiz sonuclari gecerlidir; uzman yorumu icin lutfen tekrar deneyin."
            )

    except httpx.RequestError as e:
        logger.warning("Ollama istek hatasi: %s", type(e).__name__)
        return (
            "Yapay zeka yorum servisi su anda erisilemiyor. "
            "Analiz sonuclari gecerlidir; uzman yorumu icin lutfen tekrar deneyin."
        )
    except Exception as e:
        logger.warning("Ollama beklenmeyen hata: %s", type(e).__name__)
        return (
            "Yapay zeka yorum servisi su anda erisilemiyor. "
            "Analiz sonuclari gecerlidir; uzman yorumu icin lutfen tekrar deneyin."
        )

