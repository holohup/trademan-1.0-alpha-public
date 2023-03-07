import zoneinfo
from datetime import datetime, time, timedelta

from bot.tools.classes import Asset

TRADE_DAYS = (0, 4)
MORNING_TRADE_HOURS = {'morning': (time(9, 00), time(9, 59, 59))}
EVENING_TRADE_HOURS = {'evening': (time(19, 5), time(23, 50))}
STOCKS_TRADE_HOURS = {'base': (time(10, 00), time(18, 39, 59))}
FUTURES_TRADE_HOURS = {
    'before_clearing': (time(10, 00), time(14, 00)),
    'after_clearing': (time(14, 5), time(18, 45)),
}
TIME_OFFSET = timedelta(seconds=30)
ZONE = zoneinfo.ZoneInfo('Europe/Moscow')

OFFSET_ADJUSTED_WORK_HOURS = {
    key: (
        (
            datetime.combine(datetime.now(ZONE).date(), value[0]) + TIME_OFFSET
        ).time(),
        (
            datetime.combine(datetime.now(ZONE).date(), value[1]) - TIME_OFFSET
        ).time(),
    )
    for key, value in STOCKS_TRADE_HOURS.items()
}


class TradingTime:
    def __init__(self, asset: Asset) -> None:
        self._asset = asset
        self._trading_hours = dict(STOCKS_TRADE_HOURS)
        if asset.morning_trading:
            self._trading_hours.update(MORNING_TRADE_HOURS)
        if asset.evening_trading:
            self._trading_hours.update(EVENING_TRADE_HOURS)

    @property
    def is_trading_now(self) -> bool:
        if self._today_is_a_trading_day:
            for open_time, close_time in self._trading_hours.values():
                if open_time <= self._current_time.time() <= close_time:
                    return True
        return False

    @property
    def _current_time(self) -> datetime.now:
        return datetime.now(ZONE)

    @property
    def _today_is_a_trading_day(self) -> bool:
        return TRADE_DAYS[0] <= self._current_time.weekday() <= TRADE_DAYS[1]
