
# TestSprite AI Testing Report(MCP)

---

## 1️⃣ Document Metadata
- **Project Name:** Final_Proje_Paketi - Kopya
- **Date:** 2026-02-18
- **Prepared by:** TestSprite AI Team

---

## 2️⃣ Requirement Validation Summary

#### Test TC001 get_health_check_endpoint_returns_200_with_message
- **Test Code:** [TC001_get_health_check_endpoint_returns_200_with_message.py](./TC001_get_health_check_endpoint_returns_200_with_message.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/5cfc3e0d-6a8b-4c68-af87-9b5c89a0bc08/6e87576f-0d4b-44eb-b8c9-981f8eb1193a
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC002 get_health_check_endpoint_returns_500_when_service_unavailable
- **Test Code:** [TC002_get_health_check_endpoint_returns_500_when_service_unavailable.py](./TC002_get_health_check_endpoint_returns_500_when_service_unavailable.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 26, in <module>
  File "<string>", line 13, in test_get_health_check_endpoint_returns_500_when_service_unavailable
AssertionError: Expected status code 500, got 200

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/5cfc3e0d-6a8b-4c68-af87-9b5c89a0bc08/63ceb387-6559-485c-a1de-51d088a45276
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC003 post_risk_hesapla_with_valid_body_returns_200_with_risk_response
- **Test Code:** [TC003_post_risk_hesapla_with_valid_body_returns_200_with_risk_response.py](./TC003_post_risk_hesapla_with_valid_body_returns_200_with_risk_response.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 51, in <module>
  File "<string>", line 34, in test_post_risk_hesapla_with_valid_body_returns_200_with_risk_response
AssertionError: Expected status code 200, got 422

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/5cfc3e0d-6a8b-4c68-af87-9b5c89a0bc08/2221cbd7-7b65-4a33-96f7-8d77451c6c2f
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC004 post_risk_hesapla_with_missing_required_fields_returns_400_or_422
- **Test Code:** [TC004_post_risk_hesapla_with_missing_required_fields_returns_400_or_422.py](./TC004_post_risk_hesapla_with_missing_required_fields_returns_400_or_422.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/5cfc3e0d-6a8b-4c68-af87-9b5c89a0bc08/16073c77-f501-40ec-b0d6-f7b19667b0f8
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC005 post_risk_hesapla_with_missing_concrete_model_file_returns_200_with_fallback_note
- **Test Code:** [TC005_post_risk_hesapla_with_missing_concrete_model_file_returns_200_with_fallback_note.py](./TC005_post_risk_hesapla_with_missing_concrete_model_file_returns_200_with_fallback_note.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 52, in <module>
  File "<string>", line 30, in test_post_risk_hesapla_with_missing_concrete_model_file_returns_200_with_fallback_note
AssertionError: Expected status code 200, got 422

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/5cfc3e0d-6a8b-4c68-af87-9b5c89a0bc08/623ed680-716a-4439-ae18-e026e3d8e949
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---


## 3️⃣ Coverage & Matching Metrics

- **40.00** of tests passed

| Requirement        | Total Tests | ✅ Passed | ❌ Failed  |
|--------------------|-------------|-----------|------------|
| ...                | ...         | ...       | ...        |
---


## 4️⃣ Key Gaps / Risks
{AI_GNERATED_KET_GAPS_AND_RISKS}
---