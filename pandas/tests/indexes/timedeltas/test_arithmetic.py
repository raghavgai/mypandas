from datetime import timedelta

import numpy as np
import pytest

from pandas.errors import NullFrequencyError

import pandas as pd
from pandas import Timedelta, TimedeltaIndex, timedelta_range
import pandas.util.testing as tm


@pytest.fixture(
    params=[
        pd.offsets.Hour(2),
        timedelta(hours=2),
        np.timedelta64(2, "h"),
        Timedelta(hours=2),
    ],
    ids=str,
)
def delta(request):
    # Several ways of representing two hours
    return request.param


@pytest.fixture(params=["B", "D"])
def freq(request):
    return request.param


class TestTimedeltaIndexArithmetic:
    # Addition and Subtraction Operations

    # -------------------------------------------------------------
    # TimedeltaIndex.shift is used by __add__/__sub__

    def test_tdi_shift_empty(self):
        # GH#9903
        idx = pd.TimedeltaIndex([], name="xxx")
        tm.assert_index_equal(idx.shift(0, freq="H"), idx)
        tm.assert_index_equal(idx.shift(3, freq="H"), idx)

    def test_tdi_shift_hours(self):
        # GH#9903
        idx = pd.TimedeltaIndex(["5 hours", "6 hours", "9 hours"], name="xxx")
        tm.assert_index_equal(idx.shift(0, freq="H"), idx)
        exp = pd.TimedeltaIndex(["8 hours", "9 hours", "12 hours"], name="xxx")
        tm.assert_index_equal(idx.shift(3, freq="H"), exp)
        exp = pd.TimedeltaIndex(["2 hours", "3 hours", "6 hours"], name="xxx")
        tm.assert_index_equal(idx.shift(-3, freq="H"), exp)

    def test_tdi_shift_minutes(self):
        # GH#9903
        idx = pd.TimedeltaIndex(["5 hours", "6 hours", "9 hours"], name="xxx")
        tm.assert_index_equal(idx.shift(0, freq="T"), idx)
        exp = pd.TimedeltaIndex(["05:03:00", "06:03:00", "9:03:00"], name="xxx")
        tm.assert_index_equal(idx.shift(3, freq="T"), exp)
        exp = pd.TimedeltaIndex(["04:57:00", "05:57:00", "8:57:00"], name="xxx")
        tm.assert_index_equal(idx.shift(-3, freq="T"), exp)

    def test_tdi_shift_int(self):
        # GH#8083
        trange = pd.to_timedelta(range(5), unit="d") + pd.offsets.Hour(1)
        result = trange.shift(1)
        expected = TimedeltaIndex(
            [
                "1 days 01:00:00",
                "2 days 01:00:00",
                "3 days 01:00:00",
                "4 days 01:00:00",
                "5 days 01:00:00",
            ],
            freq="D",
        )
        tm.assert_index_equal(result, expected)

    def test_tdi_shift_nonstandard_freq(self):
        # GH#8083
        trange = pd.to_timedelta(range(5), unit="d") + pd.offsets.Hour(1)
        result = trange.shift(3, freq="2D 1s")
        expected = TimedeltaIndex(
            [
                "6 days 01:00:03",
                "7 days 01:00:03",
                "8 days 01:00:03",
                "9 days 01:00:03",
                "10 days 01:00:03",
            ],
            freq="D",
        )
        tm.assert_index_equal(result, expected)

    def test_shift_no_freq(self):
        # GH#19147
        tdi = TimedeltaIndex(["1 days 01:00:00", "2 days 01:00:00"], freq=None)
        with pytest.raises(NullFrequencyError):
            tdi.shift(2)

    # -------------------------------------------------------------
    # Binary operations TimedeltaIndex and timedelta-like
    # Note: add and sub are tested in tests.test_arithmetic, in-place
    #  tests are kept here because their behavior is Index-specific

    def test_tdi_iadd_timedeltalike(self, delta):
        # only test adding/sub offsets as + is now numeric
        rng = timedelta_range("1 days", "10 days")
        expected = timedelta_range("1 days 02:00:00", "10 days 02:00:00", freq="D")
        rng += delta
        tm.assert_index_equal(rng, expected)

    def test_tdi_isub_timedeltalike(self, delta):
        # only test adding/sub offsets as - is now numeric
        rng = timedelta_range("1 days", "10 days")
        expected = timedelta_range("0 days 22:00:00", "9 days 22:00:00")
        rng -= delta
        tm.assert_index_equal(rng, expected)

    # -------------------------------------------------------------

    def test_tdi_ops_attributes(self):
        rng = timedelta_range("2 days", periods=5, freq="2D", name="x")

        result = rng + 1 * rng.freq
        exp = timedelta_range("4 days", periods=5, freq="2D", name="x")
        tm.assert_index_equal(result, exp)
        assert result.freq == "2D"

        result = rng - 2 * rng.freq
        exp = timedelta_range("-2 days", periods=5, freq="2D", name="x")
        tm.assert_index_equal(result, exp)
        assert result.freq == "2D"

        result = rng * 2
        exp = timedelta_range("4 days", periods=5, freq="4D", name="x")
        tm.assert_index_equal(result, exp)
        assert result.freq == "4D"

        result = rng / 2
        exp = timedelta_range("1 days", periods=5, freq="D", name="x")
        tm.assert_index_equal(result, exp)
        assert result.freq == "D"

        result = -rng
        exp = timedelta_range("-2 days", periods=5, freq="-2D", name="x")
        tm.assert_index_equal(result, exp)
        assert result.freq == "-2D"

        rng = pd.timedelta_range("-2 days", periods=5, freq="D", name="x")

        result = abs(rng)
        exp = TimedeltaIndex(
            ["2 days", "1 days", "0 days", "1 days", "2 days"], name="x"
        )
        tm.assert_index_equal(result, exp)
        assert result.freq is None
