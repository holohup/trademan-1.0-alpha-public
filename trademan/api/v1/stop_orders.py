from abc import ABC, abstractmethod
from decimal import Decimal
from typing import List

from tinkoff.invest.retrying.sync.client import RetryingClient
from tinkoff.invest.schemas import MoneyValue, Quotation, StopOrder
from tinkoff.invest.schemas import StopOrderDirection as SoD
from tinkoff.invest.schemas import StopOrderExpirationType as SOeT
from tinkoff.invest.utils import decimal_to_quotation, quotation_to_decimal


class StopOrderAdapter(ABC):
    @abstractmethod
    def get_stop_orders_params(self):
        pass

    @abstractmethod
    def place_stop_orders(self, orders):
        pass


class TinkoffStopOrderAdapter(StopOrderAdapter):
    def __init__(self, token, account_id, retry_settings) -> None:
        self._token = token
        self._retry_settings = retry_settings
        self._account_id = account_id

    def place_stop_orders(self, orders):
        with RetryingClient(self._token, self._retry_settings) as client:
            client.cancel_all_orders(account_id=self._account_id)
        for order in orders:
            order_params = self._prepare_order_params(order)
            with RetryingClient(self._token, self._retry_settings) as client:
                r = client.stop_orders.post_stop_order(**order_params)
            print(r)

    def _prepare_order_params(self, order):
        direction = (
            SoD.STOP_ORDER_DIRECTION_SELL
            if order.sell
            else SoD.STOP_ORDER_DIRECTION_BUY
        )
        ratio = (
            Decimal('0.1') if order.asset.asset_type == 'B' else Decimal('1')
        )
        return {
            'figi': order.asset.figi,
            'price': decimal_to_quotation(order.price * ratio),
            'stop_price': decimal_to_quotation(order.stop_price * ratio),
            'quantity': order.lots,
            'account_id': self._account_id,
            'direction': direction,
            'stop_order_type': order.order_type,
            'expiration_type': SOeT.STOP_ORDER_EXPIRATION_TYPE_GOOD_TILL_CANCEL
        }

    def get_stop_orders_params(self):
        response = self._get_stop_orders()
        if not response:
            return None
        return [self._parse_order_params(order) for order in response]

    def _get_stop_orders(self) -> List[StopOrder]:
        with RetryingClient(self._token, self._retry_settings) as client:
            return client.stop_orders.get_stop_orders(
                account_id=self._account_id
            ).stop_orders

    def _parse_order_params(self, order: StopOrder):
        return {
            'lots': order.lots_requested,
            'order_type': order.order_type,
            'stop_price': self._money_value_to_decimal(order.stop_price),
            'price': self._money_value_to_decimal(order.price),
            'sell': order.direction == SoD.STOP_ORDER_DIRECTION_SELL,
            'figi': order.figi,
        }

    def _money_value_to_decimal(self, mv: MoneyValue):
        return quotation_to_decimal(Quotation(units=mv.units, nano=mv.nano))

    def _place_stop_order(self):
        pass
