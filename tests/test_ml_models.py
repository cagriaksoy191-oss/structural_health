import sys
from unittest.mock import MagicMock

# Mock dependencies before importing services.ml_models
sys.modules["pandas"] = MagicMock()
sys.modules["joblib"] = MagicMock()

import pytest
from services.ml_models import tahmin_beton_dayanimi
import services.ml_models

def test_tahmin_beton_dayanimi_success(monkeypatch):
    """Test successful prediction."""
    mock_model = MagicMock()
    # Mock predict to return a list/array with one value
    mock_model.predict.return_value = [30.5]
    monkeypatch.setattr(services.ml_models, "concrete_model", mock_model)

    val, fallback = tahmin_beton_dayanimi(3200.0, 28.0)

    assert val == 30.5
    assert fallback is False
    # Verify predict was called
    mock_model.predict.assert_called_once()

def test_tahmin_beton_dayanimi_none(monkeypatch):
    """Test behavior when concrete_model is None."""
    monkeypatch.setattr(services.ml_models, "concrete_model", None)

    val, fallback = tahmin_beton_dayanimi(3200.0, 28.0)

    assert val == 25.0
    assert fallback is True

def test_tahmin_beton_dayanimi_exception(monkeypatch):
    """Test error handling path when predict raises an exception."""
    mock_model = MagicMock()
    mock_model.predict.side_effect = RuntimeError("Mock prediction failure")
    monkeypatch.setattr(services.ml_models, "concrete_model", mock_model)

    # This should hit the except Exception block in ml_models.py
    val, fallback = tahmin_beton_dayanimi(3200.0, 28.0)

    assert val == 25.0
    assert fallback is True
