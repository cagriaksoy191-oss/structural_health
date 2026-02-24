"""Yapı Sağlığı — Qwen3 LLM Entegrasyonu"""

import requests


def get_llm_comment(skor, risk_durumu, beton, korozyon, risk_puani):
    # Bilgisayarındaki model adı (Listede gördüğün ismin aynısı olmalı)
    MODEL_ADI = "qwen3:8b"

    # Kullanıcı verilerini hazırlayalım
    user_message = f"""
    ANALİZ EDİLECEK BİNA VERİLERİ:
    - Yapı Sağlık Skoru: {skor}/100
    - Risk Durumu: {risk_durumu}
    - Beton Dayanımı: {beton} MPa
    - Korozyon Durumu: {korozyon} mV
    - Genel Risk Puanı: {risk_puani}

    GÖREVİN:
    Bu verileri inceleyen uzman bir inşaat mühendisi gibi davran. 
    Bina sahibi için GÜVEN VEREN, AKICI, PROFESYONEL ve TÜRKÇE bir değerlendirme paragrafı yaz.
    Madde madde yazma, tek bir bütün metin olsun.
    """

    # Sistem (Rol) Tanımı
    system_message = "Sen uzman bir Türk inşaat mühendisisin. Teknik terimleri halkın anlayacağı dilde, akıcı bir paragraf olarak yorumlarsın."

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
