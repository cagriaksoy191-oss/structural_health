import requests


def test_post_risk_hesapla_with_valid_body_returns_200_with_risk_response():
    base_url = "http://localhost:8000"
    url = f"{base_url}/api/risk-hesapla"
    headers = {"Content-Type": "application/json"}
    payload = {
        "il": "Istanbul",
        "ilce": "Kadikoy",
        "yapimYili": 2005,
        "katSayisi": 5,
        "zeminDukkan": "evet",
        "bitisik": "hayir",
        "hasar": "yok",
        "kullanimAmaci": "konut",
        "kisaKolon": "yok",
        "agirCikma": "yok",
        "planTipi": "dikdortgen",
        "bitisikHiza": "yok",
        "ultrasonikSesHizi": 4500.5,
        "geriSicramaSayisi": 12.3,
        "corrosion": 0.1,
        "zeminSinifi": "Z2",
        "crackPuan": 2,
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"

    if response.status_code != 200:
        print(f"DEBUG: Error Response Body: {response.text}")
    assert (
        response.status_code == 200
    ), f"Expected status code 200, got {response.status_code}"

    try:
        data = response.json()
    except ValueError:
        assert False, "Response is not a valid JSON"

    assert isinstance(data, dict), "Response JSON is not an object"
    # Check required fields in response
    assert "healthScore" in data, "Missing 'healthScore' in response"
    assert "basincDayanimi" in data, "Missing 'basincDayanimi' in response"
    assert "detaylar" in data, "Missing 'detaylar' in response"
    # Further type checks
    assert isinstance(
        data["healthScore"], (int, float)
    ), "'healthScore' should be numeric"
    assert isinstance(
        data["basincDayanimi"], (int, float)
    ), "'basincDayanimi' should be numeric"
    assert isinstance(data["detaylar"], list), "'detaylar' should be a list"


test_post_risk_hesapla_with_valid_body_returns_200_with_risk_response()
