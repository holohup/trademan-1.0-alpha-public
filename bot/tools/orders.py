from tinkoff.invest.retrying.aio.client import AsyncRetryingClient
from tinkoff.invest import AsyncClient
from tinkoff.invest.schemas import StopOrderType, StopOrderDirection, StopOrderExpirationType
from tinkoff.invest import exceptions, OrderDirection, OrderType
from tinkoff.invest.schemas import Quotation
from settings import ORDER_TTL, RETRY_SETTINGS, TCS_RW_TOKEN, TCS_ACCOUNT_ID, TCS_RO_TOKEN
from tools.utils import delta_minutes_to_utc
from datetime import datetime



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


async def cancel_all_orders():
    async with AsyncRetryingClient(TCS_RW_TOKEN, RETRY_SETTINGS) as client:
        await client.cancel_all_orders(account_id=TCS_ACCOUNT_ID)
    return 'All active orders cancelled'


async def cancel_order(order_id):
    params = {'account_id': TCS_ACCOUNT_ID, 'order_id': order_id}
    # async with AsyncRetryingClient(TCS_RW_TOKEN, RETRY_SETTINGS) as client:
    async with AsyncClient(TCS_RW_TOKEN) as client:
        try:
            await client.orders.cancel_order(**params)
        except exceptions.AioRequestError as error:
            if error.code.value[0] == 5:
                print(f'Похоже, заявка сработала и ее не получается снять: {error}')


async def get_assets_executed(order_id):
    # async with AsyncClient(TCS_RO_TOKEN) as client:
    async with AsyncRetryingClient(TCS_RO_TOKEN, RETRY_SETTINGS) as client:
        try:
            r = await client.orders.get_order_state(account_id=TCS_ACCOUNT_ID, order_id=order_id)
        except Exception as error:
            message = ('Не удается получить данные об исполнении заявки:\n'
                       f'account_id={TCS_ACCOUNT_ID}, order_id={order_id}\n'
                       f'error: {error}'
                       )
            print(message)
            raise exceptions.AioRequestError(200, message, metadata=message)
        else:
            r = r.lots_executed
            if r > 0:
                print(f'Получен ответ о кол-ве исполненных заявок: {r}')
        return r


async def get_price_to_place_order(figi: str, sell: bool) -> Quotation:
    # async with AsyncClient(TCS_RO_TOKEN) as client:
    async with AsyncRetryingClient(TCS_RO_TOKEN, RETRY_SETTINGS) as client:
        r = await client.market_data.get_order_book(figi=figi, depth=2)
    if not r.asks or not r.bids:
        raise ValueError('Нет ни одного аска в стакане! Возможно, сессия еще не началась.')
    if sell:
        return r.asks[1].price
    else:
        return r.bids[1].price


async def place_sellbuy_order(figi: str, sell: bool, price: Quotation, lots):
    params = {
        'account_id': TCS_ACCOUNT_ID,
        'order_type': OrderType.ORDER_TYPE_LIMIT,
        'order_id': str(datetime.utcnow().timestamp()),
        'figi': figi,
        'quantity': lots,
        'price': price,
    }
    if sell:
        params['direction'] = OrderDirection.ORDER_DIRECTION_SELL
    else:
        params['direction'] = OrderDirection.ORDER_DIRECTION_BUY

    async with AsyncClient(TCS_RW_TOKEN) as client:
    # async with AsyncRetryingClient(TCS_RW_TOKEN, RETRY_SETTINGS) as client:
        try:
            r = await client.orders.post_order(**params)
        except Exception as error:
            print(error)
            raise error
        return r

