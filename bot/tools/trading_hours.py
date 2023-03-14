from abc import ABC, abstractmethod
from datetime import time
from typing import NamedTuple


class TradingSession(NamedTuple):
    open: time
    close: time


class TradingHours(ABC):
    @abstractmethod
    def base_hours(self):
        pass

    @abstractmethod
    def morning_hours(self):
        pass

    @abstractmethod
    def evening_hours(self):
        pass


class FutureTradingHours(TradingHours):
    @property
    def base_hours(self):
        return {
            'before_noon': TradingSession(time(9, 00), time(14, 00)),
            'after_noon': TradingSession(time(14, 10), time(18, 50)),
        }

    @property
    def morning_hours(self):
        return {}

    @property
    def evening_hours(self):
        return {'evening': TradingSession(time(19, 15), time(23, 50))}


class StockTradingHours(TradingHours):
    @property
    def base_hours(self):
        return {'base': TradingSession(time(10, 00), time(18, 39, 59))}

    @property
    def morning_hours(self):
        return {'morning': TradingSession(time(9, 00), time(9, 50))}

    @property
    def evening_hours(self):
        return {'evening': TradingSession(time(19, 5), time(23, 50))}
