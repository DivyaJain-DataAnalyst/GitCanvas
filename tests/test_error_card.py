# tests/test_error_card.py
from utils.error_card import draw_error_card


def test_error_card_rate_limit():
    result = draw_error_card("rate_limit", username="testuser")
    assert isinstance(result, str)
    assert "</svg>" in result
    assert "Rate Limit" in result


def test_error_card_invalid_user():
    result = draw_error_card("invalid_user", username="fakeuser")
    assert isinstance(result, str)
    assert "</svg>" in result
    assert "fakeuser" in result


def test_error_card_unknown():
    result = draw_error_card("unknown", username="testuser", message="Something broke")
    assert isinstance(result, str)
    assert "</svg>" in result


def test_error_card_default_fallback():
    # passing unknown error_type should fall back gracefully
    result = draw_error_card("nonexistent_type", username="testuser")
    assert isinstance(result, str)
    assert "</svg>" in result