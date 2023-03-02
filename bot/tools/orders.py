from settings import (ORDER_TTL, RETRY_SETTINGS, TCS_ACCOUNT_ID, TCS_RO_TOKEN,
                      TCS_RW_TOKEN)
from tinkoff.invest import AsyncClient, exceptions
from tinkoff.invest.retrying.aio.client import AsyncRetryingClient
from tinkoff.invest.schemas import Quotation
from tinkoff.invest.schemas import StopOrderDirection as SODir
from tinkoff.invest.schemas import StopOrderExpirationType as SType
from tinkoff.invest.schemas import StopOrderType as SOType
from tools.utils import delta_minutes_to_utc

from tools.adapters import OrderAdapter

# from bot.tools.classes import Asset


async def place_long_stop(figi, price, lots):
    async with AsyncRetryingClient(TCS_RW_TOKEN, RETRY_SETTINGS) as client:
        params = {
            'figi': figi,
            'price': price,
            'stop_price': price,
            'quantity': lots,
            'account_id': TCS_ACCOUNT_ID,
            'direction': SODir.STOP_ORDER_DIRECTION_BUY,
            'stop_order_type': SOType.STOP_ORDER_TYPE_TAKE_PROFIT,
            'expiration_type': SType.STOP_ORDER_EXPIRATION_TYPE_GOOD_TILL_DATE,
            'expire_date': delta_minutes_to_utc(ORDER_TTL),
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
            'direction': SODir.STOP_ORDER_DIRECTION_SELL,
            'stop_order_type': SOType.STOP_ORDER_TYPE_TAKE_PROFIT,
            'expiration_type': SType.STOP_ORDER_EXPIRATION_TYPE_GOOD_TILL_DATE,
            'expire_date': delta_minutes_to_utc(ORDER_TTL),
        }
        return await client.stop_orders.post_stop_order(**params)


async def cancel_all_orders():
    async with AsyncRetryingClient(TCS_RW_TOKEN, RETRY_SETTINGS) as client:
        await client.cancel_all_orders(account_id=TCS_ACCOUNT_ID)
    return 'All active orders cancelled'


async def cancel_order(order_id):
    params = {'account_id': TCS_ACCOUNT_ID, 'order_id': order_id}
    async with AsyncClient(TCS_RW_TOKEN) as client:
        try:
            await client.orders.cancel_order(**params)
        except exceptions.AioRequestError as error:
            if error.code.value[0] == 5:
                print(
                    f'''Похоже, заявка сработала и ее не получается снять:
                     {error}'''
                )


async def get_execution_report(order_id):
    async with AsyncRetryingClient(TCS_RO_TOKEN, RETRY_SETTINGS) as client:
        try:
            r = await client.orders.get_order_state(
                account_id=TCS_ACCOUNT_ID, order_id=order_id
            )
        except Exception as error:
            message = (
                'Не удается получить данные об исполнении заявки:\n'
                f'account_id={TCS_ACCOUNT_ID}, order_id={order_id}\n'
                f'error: {error}'
            )
            raise exceptions.AioRequestError(200, message, metadata=message)
        else:
            if r.lots_executed > 0:
                print(
                    f'''Получен ответ о кол-ве исполненных заявок:
                     {r.lots_executed}'''
                )
        return r


async def get_price_to_place_order(figi: str, sell: bool) -> Quotation:
    async with AsyncRetryingClient(TCS_RO_TOKEN, RETRY_SETTINGS) as client:
        r = await client.market_data.get_order_book(figi=figi, depth=1)
    if not r.asks or not r.bids:
        raise ValueError(
            f'Нет ни одного аска в стакане! Возможно, сессия еще не началась.'
            f'{figi} {sell}'
        )
    return r.asks[0].price if sell else r.bids[0].price


async def get_closest_execution_price(figi: str, sell: bool) -> Quotation:
    return await get_price_to_place_order(figi, sell)


async def place_order(asset, type: str):
    params = OrderAdapter(asset, type).order_params()
    async with AsyncClient(TCS_RW_TOKEN) as client:
        return await client.orders.post_order(**params)
