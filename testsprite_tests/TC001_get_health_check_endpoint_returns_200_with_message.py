import requests

BASE_URL = "http://localhost:8000"


def test_get_health_check_endpoint_returns_200_with_message():
    try:
        response = requests.get(f"{BASE_URL}/", timeout=30)
        response.raise_for_status()
        json_data = response.json()
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        assert "message" in json_data, "Response JSON does not contain 'message' key"
        assert isinstance(json_data["message"], str), "'message' is not a string"
        assert json_data["message"], "'message' is empty"
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"


test_get_health_check_endpoint_returns_200_with_message()