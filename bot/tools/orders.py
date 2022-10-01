
from tinkoff.invest.retrying.sync.client import RetryingClient
from tinkoff.invest.retrying.aio.client import AsyncRetryingClient
from tinkoff.invest.utils import quotation_to_decimal
from tinkoff.invest.exceptions import RequestError
from tinkoff.invest.schemas import StopOrderType, StopOrderDirection, StopOrderExpirationType

from settings import ORDER_TTL, RETRY_SETTINGS, TCS_RW_TOKEN, TCS_ACCOUNT_ID, TCS_RO_TOKEN
from tools.utils import delta_minutes_to_utc




async def place_long_stop(figi, price, lots):
    async with AsyncRetryingClient(TCS_RW_TOKEN, RETRY_SETTINGS) as client:
        params = {
            'figi': figi,
            'price': price,
            'stop_price': price,
            'quantity': lots,
            'account_id': TCS_ACCOUNT_ID,
            'direction': StopOrderDirection.STOP_ORDER_DIRECTION_BUY,
            'stop_order_type': StopOrderType.STOP_ORDER_TYPE_TAKE_PROFIT,
            'expiration_type': StopOrderExpirationType.STOP_ORDER_EXPIRATION_TYPE_GOOD_TILL_DATE,
            'expire_date': delta_minutes_to_utc(ORDER_TTL)
        }
        return await client.stop_orders.post_stop_order(**params)

async def place_short_stop(figi, price, lots):
    async with AsyncRetryingClient(TCS_RW_TOKEN, RETRY_SETTINGS) as client:
        params = {
            'figi': figi,
            'price': price,
            'stop_price': price,
            'quantity': lots,
            'account_id': TCS_ACCOUNT_ID,
            'direction': StopOrderDirection.STOP_ORDER_DIRECTION_SELL,
            'stop_order_type': StopOrderType.STOP_ORDER_TYPE_TAKE_PROFIT,
            'expiration_type': StopOrderExpirationType.STOP_ORDER_EXPIRATION_TYPE_GOOD_TILL_DATE,
            'expire_date': delta_minutes_to_utc(ORDER_TTL)
        }
        return await client.stop_orders.post_stop_order(**params)


def get_current_prices(assets):
    figis = [asset.figi for asset in assets]
    with RetryingClient(TCS_RO_TOKEN, RETRY_SETTINGS) as client:
        response = client.market_data.get_last_prices(figi=figis)
    prices = {item.figi: quotation_to_decimal(item.price) for item in response.last_prices}
    for asset in assets:
        try:
            asset.price = float(prices[asset.figi])
        except Exception as error:
            raise ValueError(f'{error}')
    return assets

async def cancel_all_orders():
    async with AsyncRetryingClient(TCS_RW_TOKEN, RETRY_SETTINGS) as client:
        await client.cancel_all_orders(account_id=TCS_ACCOUNT_ID)
    return 'All active orders cancelled'
