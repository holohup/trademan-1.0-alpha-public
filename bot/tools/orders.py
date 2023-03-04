from settings import RETRY_SETTINGS, TCS_ACCOUNT_ID, TCS_RO_TOKEN, TCS_RW_TOKEN
from tinkoff.invest import AsyncClient, exceptions
from tinkoff.invest.retrying.aio.client import AsyncRetryingClient
from tools.adapters import OrderAdapter, StopOrderAdapter


async def place_stop_order(order):
    params = StopOrderAdapter(order).order_params
    async with AsyncRetryingClient(TCS_RW_TOKEN, RETRY_SETTINGS) as client:
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
                    f'Похоже, заявка сработала и ее не получается снять: '
                    f'{error}'
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


async def get_price_from_order_book(asset):
    async with AsyncRetryingClient(TCS_RO_TOKEN, RETRY_SETTINGS) as client:
        r = await client.market_data.get_order_book(figi=asset.figi, depth=1)
    if not r.asks or not r.bids:
        raise ValueError(
            'Нет бидов или асков. Возможно, сессия еще не началась.'
        )
    return r.asks[0].price if asset.sell else r.bids[0].price


async def place_order(asset, type: str):
    params = OrderAdapter(asset, type).order_params
    async with AsyncClient(TCS_RW_TOKEN) as client:
        return await client.orders.post_order(**params)
