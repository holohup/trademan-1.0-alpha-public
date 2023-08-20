import zoneinfo
from datetime import datetime, time, timedelta
from typing import Union

from tools.trading_hours import (FutureTradingHours, StockTradingHours,
                                 TradingSession)

TRADING_SCHEDULES = {'S': StockTradingHours, 'F': FutureTradingHours}
TRADE_DAYS = (0, 4)
DAYS_IN_WEEK = 7

TIME_OFFSET = timedelta(seconds=15)
MOSCOW_ZONE = zoneinfo.ZoneInfo('Europe/Moscow')


class TradingTime:
    def __init__(self, asset) -> None:
        schedule = TRADING_SCHEDULES[asset.asset_type]()
        self._trading_sessions = dict(schedule.base_hours)

        if asset.morning_trading:
            self._trading_sessions.update(schedule.morning_hours)
        if asset.evening_trading:
            self._trading_sessions.update(schedule.evening_hours)
        self._update_trading_schedule_with_time_offset()
        self._sorted_sess_cache = None

    @property
    def is_trading_now(self) -> bool:
        if not self._today_is_a_trading_day:
            return False
        for open_time, close_time in self._sorted_sessions:
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
        return self._seconds_count_till_trading_after_all_sessions_close

    @property
    def _seconds_until_next_session_today(self) -> int:
        return self._seconds_till_nearest_session(
            self._current_datetime.time()
        )

    @property
    def _seconds_count_till_trading_after_all_sessions_close(self) -> int:
        midnights = self._midnights_count_till_trading_day
        secs_midn_to_session = self._seconds_till_nearest_session(time(0, 0))
        full_days_pause_secs = 24 * 60 * 60 * (midnights - 1)
        return (
            self._seconds_till_midnight
            + secs_midn_to_session
            + full_days_pause_secs
        )

    @property
    def _seconds_till_midnight(self) -> int:
        return (
            self._time_difference_in_seconds(
                time(23, 59, 59), self._current_datetime.time()
            )
            + 1
        )

    def _seconds_till_nearest_session(self, tyme: time) -> int:
        for session in self._sorted_sessions:
            if session.open > tyme:
                return self._time_difference_in_seconds(session.open, tyme)
        raise ValueError(f'Unexpected search for session after close. {tyme}')

    def _time_difference_in_seconds(self, t1: time, t2: time):
        delta = datetime.combine(
            self._current_datetime.date(), t1
        ) - datetime.combine(self._current_datetime.date(), t2)
        return delta.seconds

    @property
    def _sorted_sessions(self) -> list:
        if not self._sorted_sess_cache:
            self._sorted_sess_cache = sorted(self._trading_sessions.values())
        return self._sorted_sess_cache

    @property
    def _midnights_count_till_trading_day(self) -> int:
        if self._will_trade_today:
            return 0
        today = self._current_datetime.weekday()
        if today > TRADE_DAYS[1] - 1:
            return DAYS_IN_WEEK - today + TRADE_DAYS[0]
        if today < TRADE_DAYS[0]:
            return TRADE_DAYS[0] - today
        return 1

    @property
    def _is_later_then_last_session_close(self) -> bool:
        return self._current_datetime.time() > self._sorted_sessions[-1].close

    @property
    def _will_trade_today(self) -> bool:
        return (
            not self._is_later_then_last_session_close
            and self._today_is_a_trading_day
        )

    def _update_trading_schedule_with_time_offset(self) -> None:
        dt = self._current_datetime.date()
        self._trading_sessions = {
            title: TradingSession(
                open=(datetime.combine(dt, period.open) + TIME_OFFSET).time(),
                close=(
                    datetime.combine(dt, period.close) - TIME_OFFSET
                ).time(),
            )
            for title, period in self._trading_sessions.items()
        }


class SpreadTradingTime(TradingTime):
    def __init__(self, spread) -> None:
        self.schedules = (
            TradingTime(spread.near_leg)._sorted_sessions
            + TradingTime(spread.far_leg)._sorted_sessions
        )
        self._trading_sessions = self._combine_trading_sessions()
        self._sorted_sess_cache = None

    def _combine_trading_sessions(self):
        events = [(period.open, 1) for period in self.schedules]
        events += [(period.close, -1) for period in self.schedules]
        sum = 0
        result = {}
        period_open = None
        for time_moment in sorted(events):
            sum += time_moment[1]
            if sum > 1:
                period_open = time_moment[0]
            if sum < 2 and period_open is not None:
                period_close = time_moment[0]
                result[
                    f'{str(period_open)} - {str(period_close)}'
                ] = TradingSession(period_open, period_close)
                period_open = None
        return result


class SimpleTradingTime:
    def __init__(
        self, schedule: Union[FutureTradingHours, StockTradingHours]
    ) -> None:
        schedule = schedule
        self._trading_sessions = dict(schedule.base_hours)
        self._trading_sessions.update(schedule.morning_hours)
        self._trading_sessions.update(schedule.evening_hours)
        self._update_trading_schedule_with_time_offset()
        self._sorted_sess_cache = None

    @property
    def is_trading_now(self) -> bool:
        if not self._today_is_a_trading_day:
            return False
        for open_time, close_time in self._sorted_sessions:
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
    def _sorted_sessions(self) -> list:
        if not self._sorted_sess_cache:
            self._sorted_sess_cache = sorted(self._trading_sessions.values())
        return self._sorted_sess_cache

    def _update_trading_schedule_with_time_offset(self) -> None:
        dt = self._current_datetime.date()
        self._trading_sessions = {
            title: TradingSession(
                open=(
                    datetime.combine(dt, period.open) + TIME_OFFSET
                ).time(),
                close=(
                    datetime.combine(dt, period.close) - TIME_OFFSET
                ).time(),
            )
            for title, period in self._trading_sessions.items()
        }
