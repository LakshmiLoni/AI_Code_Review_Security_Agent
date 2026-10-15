"""Headless smoke test of the Streamlit UI (no browser, code is never executed)."""
from pathlib import Path

import pytest

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest  # noqa: E402

APP_PATH = Path(__file__).resolve().parent.parent / "app.py"


def _app():
    at = AppTest.from_file(str(APP_PATH), default_timeout=60)
    at.run()
    return at


def _button(at, key):
    return next(b for b in at.button if b.key == key)


def test_app_loads_without_exception():
    at = _app()
    assert not at.exception
    assert at.title[0].value.startswith("AI Code Review")


def test_no_language_dropdown():
    at = _app()
    assert len(at.selectbox) == 0


def test_paste_python_and_validate():
    at = _app()
    at.text_area(key="paste_area").input("def add(a, b):\n    return a + b\n")
    _button(at, "validate_paste").click()
    at.run()
    assert not at.exception
    page = " ".join(m.value for m in at.markdown)
    assert "Python" in page and "Valid syntax" in page


def test_paste_invalid_python_shows_line():
    at = _app()
    at.text_area(key="paste_area").input("def broken(:\n    pass\n")
    _button(at, "validate_paste").click()
    at.run()
    assert not at.exception
    assert any("Line 1" in m.value for m in at.markdown)


def test_ambiguous_paste_asks_for_clearer_sample():
    at = _app()
    at.text_area(key="paste_area").input("hello")
    _button(at, "validate_paste").click()
    at.run()
    assert any("clearer" in e.value for e in at.error)


def test_empty_paste_shows_error():
    at = _app()
    _button(at, "validate_paste").click()
    at.run()
    assert any("empty" in e.value.lower() for e in at.error)
