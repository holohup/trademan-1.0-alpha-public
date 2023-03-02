from datetime import datetime

from settings import ORDER_TTL, TCS_ACCOUNT_ID
from tinkoff.invest import OrderDirection, OrderType
from tinkoff.invest.schemas import StopOrderDirection as SODir
from tinkoff.invest.schemas import StopOrderExpirationType as SType
from tinkoff.invest.schemas import StopOrderType as SOType
from tools.utils import delta_minutes_to_utc


class OrderAdapter:
    DIRECTIONS = {
        'sell': OrderDirection.ORDER_DIRECTION_SELL,
        'buy': OrderDirection.ORDER_DIRECTION_BUY,
    }
    ORDER_TYPES = {
        'market': OrderType.ORDER_TYPE_MARKET,
        'limit': OrderType.ORDER_TYPE_LIMIT,
    }

    def __init__(self, asset, order_type: str) -> None:
        self._asset = asset
        self._order_type = order_type

    @property
    def order_params(self):
        params = {
            'account_id': TCS_ACCOUNT_ID,
            'order_type': self.ORDER_TYPES[self._order_type],
            'order_id': str(datetime.utcnow().timestamp()),
            'figi': self._asset.figi,
            'quantity': self._asset.get_lots(self._asset.next_order_amount),
        }
        params['direction'] = (
            self.DIRECTIONS['sell']
            if self._asset.sell
            else self.DIRECTIONS['buy']
        )
        if self._order_type == 'limit':
            params['price'] = self._asset.price
        return params


class StopOrderAdapter:
    ORDER_TYPES = {
        'stop_loss': SOType.STOP_ORDER_TYPE_STOP_LOSS,
        'take_profit': SOType.STOP_ORDER_TYPE_TAKE_PROFIT,
        'stop_limit': SOType.STOP_ORDER_TYPE_STOP_LIMIT,
    }
    EXPIRATION_TYPES = {
        'gtd': SType.STOP_ORDER_EXPIRATION_TYPE_GOOD_TILL_DATE,
        'gtc': SType.STOP_ORDER_EXPIRATION_TYPE_GOOD_TILL_CANCEL,
    }
    DIRECTIONS = {
        'sell': SODir.STOP_ORDER_DIRECTION_SELL,
        'buy': SODir.STOP_ORDER_DIRECTION_BUY,
    }

    def __init__(self, stop_order):
        self._asset = stop_order.asset
        self._price = self._asset.get_correct_price(stop_order.price)
        self._params = {
            'figi': self._asset.figi,
            'price': self._price,
            'stop_price': self._price,
            'quantity': self._asset.get_lots(
                int(stop_order.sum / stop_order.price)
            ),
            'account_id': TCS_ACCOUNT_ID,
            'direction': self.DIRECTIONS[stop_order.params.direction],
            'stop_order_type': self.ORDER_TYPES[stop_order.params.stop_type],
            'expiration_type': self.EXPIRATION_TYPES[
                stop_order.params.expiration
            ],
        }
        if stop_order.params.expiration == 'gtd':
            self._params['expire_date'] = delta_minutes_to_utc(ORDER_TTL)

    @property
    def order_params(self):
        return self._params
