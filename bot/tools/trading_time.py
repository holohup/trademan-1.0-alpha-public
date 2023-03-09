import zoneinfo
from datetime import datetime, time, timedelta
from typing import NamedTuple

from bot.tools.classes import Asset


class TradingSession(NamedTuple):
    open: time
    close: time


TRADE_DAYS = (0, 4)
MORNING_TRADE_HOURS = {'morning': TradingSession(time(9, 00), time(9, 50))}
EVENING_TRADE_HOURS = {'evening': TradingSession(time(19, 5), time(23, 50))}
STOCKS_TRADE_HOURS = {'base': TradingSession(time(10, 00), time(18, 39, 59))}
FUTURES_TRADE_HOURS = {
    'before_clearing': TradingSession(time(9, 00), time(14, 00)),
    'after_clearing': TradingSession(time(14, 5), time(18, 45)),
}
TIME_OFFSET = timedelta(seconds=15)
MOSCOW_ZONE = zoneinfo.ZoneInfo('Europe/Moscow')


class TradingTime:
    def __init__(self, asset: Asset) -> None:
        self._asset = asset
        if asset.asset_type == 'F':
            self._trading_sessions = dict(FUTURES_TRADE_HOURS)
        else:
            self._trading_sessions = dict(STOCKS_TRADE_HOURS)
        if asset.morning_trading and asset.asset_type != 'F':
            self._trading_sessions.update(MORNING_TRADE_HOURS)
        if asset.evening_trading:
            self._trading_sessions.update(EVENING_TRADE_HOURS)
        self._update_trading_schedule_with_time_offset()
        self._sorted_sess_cache = None

    @property
    def is_trading_now(self) -> bool:
        if not self._today_is_a_trading_day:
            return False
        for open_time, close_time in self._trading_sessions.values():
            if open_time <= self._current_datetime.time() <= close_time:
                return True
        return False

    @property
    def _current_datetime(self) -> datetime:
        return datetime.now(MOSCOW_ZONE)

    @property
    def _today_is_a_trading_day(self) -> bool:
        return (
            TRADE_DAYS[0] <= self._current_datetime.weekday() <= TRADE_DAYS[1]
        )

    @property
    def seconds_till_trading_starts(self) -> int:
        if self.is_trading_now:
            return 0
        if self._will_trade_today:
            return self._seconds_until_next_session_today
        return self._seconds_count_till_trading_after_session_close

    @property
    def _seconds_until_next_session_today(self) -> int:
        return self._seconds_till_nearest_session(
            self._current_datetime.time()
        )

    @property
    def _seconds_count_till_trading_after_session_close(self) -> int:
        midnights = self._midnights_count_till_trading_starts
        secs_midn_to_session = self._seconds_till_nearest_session(time(0, 0))
        if midnights > 0:
            return (
                self._seconds_till_midnight
                + 24 * 60 * 60 * (midnights - 1)
                + secs_midn_to_session
            )
        return self._seconds_till_midnight + secs_midn_to_session

    @property
    def _seconds_till_midnight(self) -> int:
        return (
            self._time_difference_in_seconds(
                time(23, 59, 59), self._current_datetime.time()
            )
            + 1
        )

    def _seconds_till_nearest_session(self, tyme: time) -> int:
        for session in self.sorted_sessions:
            if session.open > tyme:
                return self._time_difference_in_seconds(session.open, tyme)
        return 0

    def _time_difference_in_seconds(self, t1: time, t2: time):
        delta = datetime.combine(
            self._current_datetime.date(), t1
        ) - datetime.combine(self._current_datetime.date(), t2)
        return delta.seconds

    @property
    def sorted_sessions(self) -> list:
        if not self._sorted_sess_cache:
            self._sorted_sess_cache = sorted(self._trading_sessions.values())
        return self._sorted_sess_cache

    @property
    def _midnights_count_till_trading_starts(self) -> int:
        if self._will_trade_today:
            return 0
        midnights = 1
        while (
            self._weekday_ahead_number(midnights) > TRADE_DAYS[1]
            or self._weekday_ahead_number(midnights) < TRADE_DAYS[0]
        ):
            midnights += 1
        return midnights

    @property
    def _is_later_then_last_session_close(self) -> bool:
        return self._current_datetime.time() >= self.sorted_sessions[-1].close

    @property
    def _will_trade_today(self) -> bool:
        return (
            not self._is_later_then_last_session_close
            and self._today_is_a_trading_day
        )

    def _weekday_ahead_number(self, days_amount: int) -> int:
        return (days_amount + self._current_datetime.weekday()) % 7

    def _update_trading_schedule_with_time_offset(self) -> None:
        self._trading_sessions = {
            title: TradingSession(
                open=(
                    datetime.combine(
                        self._current_datetime.date(), period.open
                    )
                    + TIME_OFFSET
                ).time(),
                close=(
                    datetime.combine(
                        self._current_datetime.date(), period.close
                    )
                    - TIME_OFFSET
                ).time(),
            )
            for title, period in self._trading_sessions.items()
        }
