from tools.utils import get_correct_price, get_lots
from tools.orders import place_long_stop, place_short_stop


class Asset:
    def __init__(self, ticker, figi, increment, lot):
        self.ticker = ticker
        self.figi = figi
        self.increment = increment
        self.lot = lot
        self.price = 0

    def __str__(self):
        return self.ticker

    def get_correct_price(self, price):
        return get_correct_price(price, self.increment)

    def get_lots(self, number_of_stocks):
        return get_lots(number_of_stocks, self.lot)

    def place_long_stop(self, price, number_of_stocks):
        return place_long_stop(self.figi, self.get_correct_price(price), self.get_lots(number_of_stocks))

    def place_short_stop(self, price, number_of_stocks):
        return place_short_stop(self.figi, self.get_correct_price(price), self.get_lots(number_of_stocks))
