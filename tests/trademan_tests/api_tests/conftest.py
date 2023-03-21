import datetime

import pytest
from tinkoff.invest.schemas import (MoneyValue, StopOrder, StopOrderDirection,
                                    StopOrderType)


@pytest.fixture
def sample_stop_orders_response():
    return [
        StopOrder(
            stop_order_id='0be85c85-9f6e-433e-aa52-4f34b6e863a7',
            lots_requested=1,
            figi='FUTALRS06230',
            direction=StopOrderDirection.STOP_ORDER_DIRECTION_SELL,
            currency='rub',
            order_type=StopOrderType.STOP_ORDER_TYPE_STOP_LIMIT,
            create_date=datetime.datetime(
                2023, 3, 21, 14, 36, 25, 378240, tzinfo=datetime.timezone.utc
            ),
            activation_date_time=datetime.datetime(
                1970, 1, 1, 0, 0, tzinfo=datetime.timezone.utc
            ),
            expiration_time=datetime.datetime(
                2023, 6, 16, 0, 0, tzinfo=datetime.timezone.utc
            ),
            price=MoneyValue(currency='rub', units=3501, nano=0),
            stop_price=MoneyValue(currency='rub', units=3500, nano=0),
        ),
        StopOrder(
            stop_order_id='313a48b0-7b06-4198-8887-e2bc44b56d2d',
            lots_requested=65,
            figi='BBG004731032',
            direction=StopOrderDirection.STOP_ORDER_DIRECTION_SELL,
            currency='rub',
            order_type=StopOrderType.STOP_ORDER_TYPE_TAKE_PROFIT,
            create_date=datetime.datetime(
                2023, 3, 21, 14, 34, 43, 362710, tzinfo=datetime.timezone.utc
            ),
            activation_date_time=datetime.datetime(
                1970, 1, 1, 0, 0, tzinfo=datetime.timezone.utc
            ),
            expiration_time=datetime.datetime(
                1970, 1, 1, 0, 0, tzinfo=datetime.timezone.utc
            ),
            price=MoneyValue(currency='rub', units=4750, nano=0),
            stop_price=MoneyValue(currency='rub', units=4750, nano=0),
        ),
        StopOrder(
            stop_order_id='67c9580a-1b98-459b-92e3-2fbe46be9003',
            lots_requested=2,
            figi='BBG004730RP0',
            direction=StopOrderDirection.STOP_ORDER_DIRECTION_BUY,
            currency='rub',
            order_type=StopOrderType.STOP_ORDER_TYPE_STOP_LIMIT,
            create_date=datetime.datetime(
                2023, 3, 21, 14, 34, 9, 199165, tzinfo=datetime.timezone.utc
            ),
            activation_date_time=datetime.datetime(
                1970, 1, 1, 0, 0, tzinfo=datetime.timezone.utc
            ),
            expiration_time=datetime.datetime(
                1970, 1, 1, 0, 0, tzinfo=datetime.timezone.utc
            ),
            price=MoneyValue(currency='rub', units=500, nano=0),
            stop_price=MoneyValue(currency='rub', units=501, nano=0),
        ),
        StopOrder(
            stop_order_id='ca07c6dc-357b-464a-bf8c-ba24b56fb07c',
            lots_requested=1,
            figi='FUTGAZR06240',
            direction=StopOrderDirection.STOP_ORDER_DIRECTION_SELL,
            currency='rub',
            order_type=StopOrderType.STOP_ORDER_TYPE_STOP_LOSS,
            create_date=datetime.datetime(
                2023, 3, 21, 14, 35, 48, 557595, tzinfo=datetime.timezone.utc
            ),
            activation_date_time=datetime.datetime(
                1970, 1, 1, 0, 0, tzinfo=datetime.timezone.utc
            ),
            expiration_time=datetime.datetime(
                2024, 6, 21, 0, 0, tzinfo=datetime.timezone.utc
            ),
            price=MoneyValue(currency='rub', units=0, nano=0),
            stop_price=MoneyValue(currency='rub', units=10000, nano=0),
        ),
        StopOrder(
            stop_order_id='b1a739d9-2df4-4101-8cb5-52e8f7befbd2',
            lots_requested=18,
            figi='BBG00K53DJP0',
            direction=StopOrderDirection.STOP_ORDER_DIRECTION_BUY,
            currency='rub',
            order_type=StopOrderType.STOP_ORDER_TYPE_TAKE_PROFIT,
            create_date=datetime.datetime(
                2023, 3, 21, 14, 33, 34, 299028, tzinfo=datetime.timezone.utc
            ),
            activation_date_time=datetime.datetime(
                1970, 1, 1, 0, 0, tzinfo=datetime.timezone.utc
            ),
            expiration_time=datetime.datetime(
                2024, 2, 28, 23, 59, tzinfo=datetime.timezone.utc
            ),
            price=MoneyValue(currency='rub', units=500, nano=0),
            stop_price=MoneyValue(currency='rub', units=500, nano=0),
        ),
        StopOrder(
            stop_order_id='0c9a5ac6-c459-4fa8-a6d1-f2b20622bb5e',
            lots_requested=10,
            figi='BBG00K53DJP0',
            direction=StopOrderDirection.STOP_ORDER_DIRECTION_BUY,
            currency='rub',
            order_type=StopOrderType.STOP_ORDER_TYPE_STOP_LOSS,
            create_date=datetime.datetime(
                2023, 3, 21, 14, 33, 17, 380826, tzinfo=datetime.timezone.utc
            ),
            activation_date_time=datetime.datetime(
                1970, 1, 1, 0, 0, tzinfo=datetime.timezone.utc
            ),
            expiration_time=datetime.datetime(
                2024, 2, 28, 23, 59, tzinfo=datetime.timezone.utc
            ),
            price=MoneyValue(currency='rub', units=0, nano=0),
            stop_price=MoneyValue(currency='rub', units=2000, nano=0),
        ),
    ]


@pytest.fixture
def sample_empty_stop_orders_response():
    return []
