"""Yapı Sağlığı — Qwen3 LLM Entegrasyonu"""

import requests


def get_llm_comment(skor, risk_durumu, beton, korozyon, risk_puani, dts, bys, phase2_advice):
    # Kullanıcının talebi üzerine model ismi
    MODEL_ADI = "gpt-oss:120b-cloud"

    # Kullanıcı verilerini hazırlayalım
    user_message = f"""
    ANALİZ EDİLECEK BİNA VERİLERİ:
    - Yapı Sağlık Skoru: {skor}/100
    - Risk Durumu: {risk_durumu}
    - Beton Dayanımı (ANFIS): {beton} MPa
    - Korozyon Durumu: {korozyon} mV
    - Genel Risk Puanı: {risk_puani}
    - Deprem Tasarım Sınıfı (DTS): {dts}
    - Bina Yükseklik Sınıfı (BYS): {bys}
    - 2. Aşama Tavsiyesi: {phase2_advice}

    GÖREVİN:
    Yukarıdaki verileri inceleyen uzman bir Türk inşaat mühendisi olarak, bina sahibine yönelik şu formatta, 3-4 cümlelik, GÜVEN VERİCİ, NET ve KISA bir sonuç raporu yaz:

    Örnek Format:
    "Yapı sağlığı skoru 45 ve risk durumu orta seviyede; beton dayanımı 41 MPa ve korozyon potansiyeli -200 mV olduğu için acil detaylı inceleme şarttır. 2. aşama karot, röntgen gibi yöntemlerle yapının mevcut durumunu netleştirmeniz, gerekli güçlendirme ve bakım kararlarını almanız açısından kritik. Bu adımları tamamladığınızda güvenli bir şekilde kullanıma devam edilebilir."

    DİKKAT: 
    - Yanıtında KESİNLİKLE "##", "**", "*" gibi Markdown veya özel karakterler KULLANMA. Düz metin olarak yaz.
    - Metin içine KESİNLİKLE "Faz 2:" veya "2. Aşama Tavsiyesi:" gibi alt başlıklar koyma.
    - Sadece tek bir paragraftan oluşan bir metin ver.
    """

    # Sistem (Rol) Tanımı
    system_message = "Sen uzman bir Türk inşaat mühendisisin. Net ve çok kısa bir özet verirsin."

    try:
        # ARTIK '/api/chat' KULLANIYORUZ (Daha kararlı)
        response = requests.post(
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
            timeout=120,
        )

        if response.status_code == 200:
            # Chat modunda cevap 'message' -> 'content' içindedir
            return response.json()["message"]["content"].strip()
        else:
            return f"⚠️ Bağlantı Hatası (Kod: {response.status_code}). Ollama açık mı?"

    except Exception as e:
        return f"⚠️ Yapay Zeka Cevap Vermedi: {str(e)}"
