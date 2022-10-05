from settings import SHORTS_ENDPOINT, ENDPOINT_HOST, STOPS_ENDPOINT
from settings import RESTORESTOPS_ENDPOINT, SELLBUY_ENDPOINT, SPREADS_ENDPOINT
from tinkoff.invest.retrying.sync.client import RetryingClient
from tinkoff.invest.utils import quotation_to_decimal
from settings import RETRY_SETTINGS, TCS_RO_TOKEN
from tools.classes import Asset
from http import HTTPStatus
import aiohttp
import asyncio

ENDPOINTS = {
    'shorts': SHORTS_ENDPOINT,
    'stops': STOPS_ENDPOINT,
    'restore_stops': RESTORESTOPS_ENDPOINT,
    'spreads': SPREADS_ENDPOINT,
    'sellbuy': SELLBUY_ENDPOINT
}


async def async_patch_executed(command: str, id: int, executed: int):
    url = ENDPOINT_HOST + ENDPOINTS[command] + str(id) + '/'
    async with aiohttp.ClientSession() as session:
        async with session.patch(url, data={'executed': executed}) as response:
            return response.status == HTTPStatus.OK


async def async_get_api_data(command: str):
    url = ENDPOINT_HOST + ENDPOINTS[command]
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()


def get_current_prices(assets):
    figis = [asset.figi for asset in assets]
    with RetryingClient(TCS_RO_TOKEN, RETRY_SETTINGS) as client:
        response = client.market_data.get_last_prices(figi=figis)
    prices = {item.figi: quotation_to_decimal(item.price) for item in response.last_prices}
    for asset in assets:
        asset.price = prices[asset.figi]
    return assets


def prepare_asset_data(data):
    assets = []
    for asset in data:
        assets.append(Asset(
            figi=asset['figi'],
            increment=asset['increment'],
            ticker=asset['ticker'],
            lot=asset['lot'],
            id=asset.get('id'),
            price=asset.get('price', '0'),
            sell=asset.get('sell'),
            amount=asset.get('amount'),
            executed=asset.get('executed'),
        ))
    return assets

if __name__ == '__main__':
    print(
        asyncio.run(async_patch_executed('sellbuy', 1, executed=15))
    )