import functools
import sys
import time
from datetime import timedelta
from itertools import chain
from typing import Union


class Duration:
    __slots__ = (
        "days",
        "hours",
        "minutes",
        "seconds",
        "microseconds",
        "total_microseconds",
    )

    def __init__(self, microseconds: Union[int, float]):
        assert 0 <= microseconds, microseconds

        if isinstance(microseconds, float):
            microseconds = round(microseconds)

        solid_seconds = microseconds // 1000000
        solid_minutes = solid_seconds // 60
        solid_hours = solid_minutes // 60

        self.days = solid_hours // 24
        self.hours = solid_hours % 24
        self.minutes = solid_minutes % 60
        self.seconds = solid_seconds % 60
        self.microseconds = microseconds % 1000000

        # Comparable duration is video duration round to microseconds.
        self.total_microseconds = microseconds

    def __hash__(self):
        return hash(self.total_microseconds)

    def __eq__(self, other):
        return self.total_microseconds == other.total_microseconds

    def __ne__(self, other):
        return self.total_microseconds != other.total_microseconds

    def __lt__(self, other):
        return self.total_microseconds < other.total_microseconds

    def __gt__(self, other):
        return self.total_microseconds > other.total_microseconds

    def __le__(self, other):
        return self.total_microseconds <= other.total_microseconds

    def __ge__(self, other):
        return self.total_microseconds >= other.total_microseconds

    def __str__(self):
        view = []
        if self.days:
            view.append("%02dd" % self.days)
        if self.hours:
            view.append("%02dh" % self.hours)
        if self.minutes:
            view.append("%02dm" % self.minutes)
        if self.seconds:
            view.append("%02ds" % self.seconds)
        if self.microseconds:
            view.append("%06dµs" % self.microseconds)
        return " ".join(view) if view else "00s"

    def to_json(self):
        return str(self)

    @classmethod
    def from_seconds(cls, seconds):
        return cls(seconds * 1_000_000)

    @classmethod
    def from_minutes(cls, minutes):
        return cls(minutes * 60_000_000)


class _Profile(Duration):
    __slots__ = ()

    def __init__(self, difference: timedelta):
        super().__init__(
            (difference.seconds + difference.days * 24 * 3600) * 1_000_000
            + difference.microseconds
        )


class ProfilingStart:
    __slots__ = ("name",)

    def __init__(self, title):
        # type: (str) -> None
        self.name = title

    def __str__(self):
        return f"ProfilingStart({self.name})"

    __repr__ = __str__


class ProfilingEnd:
    __slots__ = "name", "time"

    def __init__(self, name, duration):
        self.name = name
        self.time = str(duration)

    def __str__(self):
        return f"ProfilingEnded({self.name}, {self.time})"


class Profiler:
    __slots__ = "__title", "__time_start", "__time_end"

    def __init__(self, title):
        self.__title = title
        self.__time_start = None
        self.__time_end = None

    def __enter__(self):
        print(ProfilingStart(self.__title), file=sys.stderr)
        self.__time_start = time.perf_counter_ns()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__time_end = time.perf_counter_ns()
        profiling = _Profile(
            timedelta(microseconds=(self.__time_end - self.__time_start) / 1000)
        )
        print(ProfilingEnd(self.__title, profiling), file=sys.stderr)
