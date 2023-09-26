import functools
import sys
import time
from datetime import timedelta
from itertools import chain
from typing import Union


class Notification:
    __slots__ = ()
    __props__ = None
    __slot_sorter__ = sorted
    __print_none__ = False

    @classmethod
    def get_slots(cls):
        if cls.__props__ is not None:
            return cls.__props__
        return cls.__slot_sorter__(
            chain.from_iterable(getattr(typ, "__slots__", ()) for typ in cls.__mro__)
        )

    def __str__(self):
        values = []
        for name in self.get_slots():
            value = getattr(self, name)
            if self.__print_none__ or value is not None:
                values.append((name, value))
        return "{}({})".format(
            type(self).__name__,
            ", ".join(
                f"{name}={repr(value) if isinstance(value, str) else value}"
                for name, value in values
            ),
        )

    __repr__ = __str__


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


class ProfilingStart(Notification):
    __slots__ = ("name",)

    def __init__(self, title):
        # type: (str) -> None
        self.name = title

    def __str__(self):
        return f"ProfilingStart({self.name})"

    __repr__ = __str__


class ProfilingEnd(Notification):
    __slots__ = "name", "time"

    def __init__(self, name, duration):
        self.name = name
        self.time = str(duration)

    def __str__(self):
        return f"ProfilingEnded({self.name}, {self.time})"


class _Profile(Duration):
    __slots__ = ()

    def __init__(self, difference: timedelta):
        super().__init__(
            (difference.seconds + difference.days * 24 * 3600) * 1_000_000
            + difference.microseconds
        )


class _InlineProfile(Notification):
    __slots__ = "title", "time"

    def __init__(self, title, duration):
        self.title = title
        self.time = duration

    def __str__(self):
        return f"Profiled({self.title}, {self.time})"


class Profiler:
    __slots__ = "__title", "__time_start", "__time_end", "__inline"

    def __init__(self, title, notifier=None, inline=False):
        self.__title = title
        self.__time_start = None
        self.__time_end = None
        self.__inline = inline

    def __enter__(self):
        if not self.__inline:
            print(ProfilingStart(self.__title), file=sys.stderr)
        self.__time_start = time.perf_counter_ns()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__time_end = time.perf_counter_ns()
        profiling = _Profile(
            timedelta(microseconds=(self.__time_end - self.__time_start) / 1000)
        )
        if self.__inline:
            print(_InlineProfile(self.__title, profiling), file=sys.stderr)
        else:
            print(ProfilingEnd(self.__title, profiling), file=sys.stderr)

    @staticmethod
    def profile(title=None):
        """Profile a function."""

        def decorator_profile(fn):
            @functools.wraps(fn)
            def wrapper(*args, **kwargs):
                with Profiler(title or fn.__name__):
                    return fn(*args, **kwargs)

            return wrapper

        return decorator_profile

    @staticmethod
    def profile_method(title=None):
        """Profile a method from an object providing a `notifier` attribute."""

        def decorator_profile(fn):
            @functools.wraps(fn)
            def wrapper(self, *args, **kwargs):
                with Profiler(title or fn.__name__, notifier=self.notifier):
                    return fn(self, *args, **kwargs)

            return wrapper

        return decorator_profile


class InlineProfiler(Profiler):
    __slots__ = ()

    def __init__(self, title, notifier=None):
        super().__init__(title, notifier, True)
