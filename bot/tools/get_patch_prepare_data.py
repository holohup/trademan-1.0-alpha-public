from http import HTTPStatus

import aiohttp
from settings import ENDPOINT_HOST, ENDPOINTS, RETRY_SETTINGS, TCS_RO_TOKEN
from tinkoff.invest.retrying.sync.client import RetryingClient
from tinkoff.invest.utils import quotation_to_decimal
from tools.classes import Asset, Spread


async def async_patch_executed(
    command: str, id: int, executed: int, price: float = 0
):
    data = {'executed': executed}
    if price:
        data['exec_price'] = price
    url = ENDPOINT_HOST + ENDPOINTS[command] + str(id) + '/'
    async with aiohttp.ClientSession() as session:
        async with session.patch(url, data=data) as response:
            return response.status == HTTPStatus.OK


async def async_get_api_data(command: str):
    url = ENDPOINT_HOST + ENDPOINTS[command]
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()


async def async_check_health():
    url = ENDPOINT_HOST + ENDPOINTS['health']
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return response.status


def get_current_prices(assets):
    figis = [asset.figi for asset in assets]
    with RetryingClient(TCS_RO_TOKEN, RETRY_SETTINGS) as client:
        response = client.market_data.get_last_prices(figi=figis)
    prices = {
        item.figi: quotation_to_decimal(item.price)
        for item in response.last_prices
    }
    for asset in assets:
        asset.price = prices[asset.figi]
    return assets


def prepare_asset_data(data):
    assets = []
    for asset in data:
        assets.append(
            Asset(
                figi=asset['figi'],
                increment=asset['increment'],
                ticker=asset['ticker'],
                lot=asset['lot'],
                id=asset.get('id'),
                price=asset.get('price', '0'),
                sell=asset.get('sell'),
                amount=asset.get('amount'),
                executed=asset.get('executed'),
            )
        )
    return assets


def prepare_spreads_data(data):
    spreads = []
    for spread in data:
        if spread['near_leg_type'] == 'S':
            ratio = spread['base_asset_amount']
        else:
            ratio = 1
        spreads.append(
            Spread(
                far_leg=Asset(
                    figi=spread['figi'],
                    increment=spread['increment'],
                    ticker=spread['ticker'],
                    lot=spread['lot'],
                    sell=spread['sell'],
                    amount=spread['amount'],
                    executed=spread['executed'],
                ),
                near_leg=Asset(
                    figi=spread['near_leg_figi'],
                    increment=spread['near_leg_increment'],
                    ticker=spread['near_leg_ticker'],
                    lot=spread['near_leg_lot'],
                    sell=not spread['sell'],
                    amount=spread['amount'] * ratio,
                    executed=spread['executed'] * ratio,
                ),
                price=spread['price'],
                amount=spread['amount'],
                executed=spread['executed'],
                near_leg_type=spread['near_leg_type'],
                base_asset_amount=spread['base_asset_amount'],
                sell=spread['sell'],
                id=spread['id'],
                exec_price=spread['exec_price'],
            )
        )
    return spreads
