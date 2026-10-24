import logging

import pytest

from grid_toolkit.utils import retry, timed


@pytest.fixture
def no_sleep(monkeypatch):
    sleeps = []
    monkeypatch.setattr("time.sleep", lambda s: sleeps.append(s))
    return sleeps


def test_retry_succeeds_after_two_failures(no_sleep):
    calls = 0

    @retry(times=3, delay=5)
    def flaky():
        nonlocal calls
        calls += 1
        if calls < 3:
            raise ConnectionError("down")
        return "ok"

    assert flaky() == "ok"
    assert calls == 3
    assert no_sleep == [5, 5]


def test_retry_gives_up_and_reraises(no_sleep):
    @retry(times=2, delay=1)
    def always_fails():
        raise ConnectionError("down")

    with pytest.raises(ConnectionError):
        always_fails()
    assert no_sleep == [1]


def test_retry_does_not_catch_other_exceptions(no_sleep):
    @retry(times=3, exceptions=(ConnectionError,))
    def bad():
        raise ValueError("bug")

    with pytest.raises(ValueError):
        bad()
    assert no_sleep == []


def test_timed_logs_elapsed(caplog):
    with caplog.at_level(logging.INFO, logger="grid_toolkit.utils"), timed("load"):
        pass
    assert "load took" in caplog.text
