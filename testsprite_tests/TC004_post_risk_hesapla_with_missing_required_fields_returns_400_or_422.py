import requests

def test_post_risk_hesapla_with_missing_required_fields_returns_400_or_422():
    base_url = "http://localhost:8000"
    url = f"{base_url}/api/risk-hesapla"
    headers = {
        "Content-Type": "application/json"
    }
    # Prepare request body missing the required field 'ultrasonikSesHizi'
    payload = {
        "il": "Istanbul",
        "ilce": "Besiktas",
        "yapimYili": 2000,
        "katSayisi": 5,
        "zeminDukkan": "Yes",
        "bitisik": "No",
        "hasar": "None",
        "kullanimAmaci": "Residential",
        "kisaKolon": "No",
        "agirCikma": "No",
        "planTipi": "Regular",
        "bitisikHiza": "Close",
        # "ultrasonikSesHizi" is omitted intentionally
        "geriSicramaSayisi": 3.5,
        "corrosion": 1.0,
        "zeminSinifi": "Class A",
        "crackPuan": 2
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"

    assert response.status_code in (400, 422), f"Expected status 400 or 422 but got {response.status_code}"
    try:
        json_resp = response.json()
    except ValueError:
        assert False, "Response is not valid JSON"

    # Expected that the response contains validation error messages listing missing/invalid fields
    # We check at least it mentions the missing 'ultrasonikSesHizi' field somewhere
    error_str = str(json_resp).lower()
    assert ("ultrasonikseshizi" in error_str or "ultrasonikSesHizi".lower() in error_str), "Validation error does not mention missing 'ultrasonikSesHizi' field"

test_post_risk_hesapla_with_missing_required_fields_returns_400_or_422()