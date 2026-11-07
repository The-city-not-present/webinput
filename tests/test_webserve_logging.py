"""Tests for the caller-side webserve console logging (src/helper_webserve_logging.py).

webinput keeps no in-memory log — the helper only prints — so these tests assert
on the console output (stdout vs stderr) only.
"""

import logging

import pytest

from src.helper_webserve_logging import WebserveLogger, logger


@pytest.fixture(autouse=True)
def _reset_logger():
    logger.handlers.clear()
    logger.setLevel(logging.NOTSET)
    logger.propagate = True
    yield
    logger.handlers.clear()
    logger.setLevel(logging.NOTSET)
    logger.propagate = True


def test_request_event_logs_to_stdout(capsys):
    wl = WebserveLogger({"script_name": "webinput"})
    wl.handle_event(
        "request",
        {
            "method": "GET",
            "path": "/health",
            "status_code": 200,
            "timestamp": "08/Nov/2026 12:00:00",
            "remote_address": "127.0.0.1",
            "request_line": "GET /health HTTP/1.1",
            "response_size": "-",
        },
    )

    captured = capsys.readouterr()
    assert "127.0.0.1 - - [08/Nov/2026 12:00:00]" in captured.out
    assert "[200]" in captured.out
    assert '"GET /health HTTP/1.1"' in captured.out
    assert captured.err == ""


def test_error_event_logs_to_stderr(capsys):
    wl = WebserveLogger({})
    wl.handle_event(
        "error",
        {"message": "boom", "traceback": "Traceback (most recent call last):\n  boom\n"},
    )

    captured = capsys.readouterr()
    assert "boom" in captured.err
    assert captured.out == ""


def test_start_event_has_script_name_prefix(capsys):
    wl = WebserveLogger({"script_name": "webinput"})
    wl.handle_event("webserver_start", {"host": "localhost", "port": 5279})

    captured = capsys.readouterr()
    assert "webinput: " in captured.out
    assert "starting webserver at localhost:5279" in captured.out
