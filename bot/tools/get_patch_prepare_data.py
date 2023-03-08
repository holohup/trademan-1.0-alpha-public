import json
from decimal import Decimal
from http import HTTPStatus
from typing import List
from urllib import request

import aiohttp
from queue_handler import QUEUE
from settings import ENDPOINT_HOST, ENDPOINTS, RETRY_SETTINGS, TCS_RO_TOKEN
from tinkoff.invest.retrying.sync.client import RetryingClient
from tinkoff.invest.utils import quotation_to_decimal
from tools.adapters import SpreadToJsonAdapter
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


async def async_patch_spread(spread: Spread):
    data = SpreadToJsonAdapter(spread).output
    url = ENDPOINT_HOST + ENDPOINTS['spreads'] + str(spread.id) + '/'
    async with aiohttp.ClientSession() as session:
        async with session.patch(url, json=data) as response:
            if response.status == HTTPStatus.OK:
                return True
            response_text = await response.text()
            await QUEUE.put(f'Error patching spreads. {response_text[:4000]}')
            return False


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
                min_price_increment=asset['min_price_increment'],
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


def parse_ticker_info(ticker: str) -> List[Asset]:
    url = ENDPOINT_HOST + ENDPOINTS['ticker'] + ticker + '/'
    return json.loads(request.urlopen(url).read())


class SpreadDataParser:
    def __init__(self, data) -> None:
        self._data = data


def prepare_leg(data, sell_direction: bool, amount: int):
    return Asset(
        figi=data['figi'],
        ticker=data['ticker'],
        min_price_increment=Decimal(data['min_price_increment']),
        lot=data['lot'],
        executed=data['executed'],
        avg_exec_price=Decimal(data['avg_exec_price']),
        morning_trading=data['morning_trading'],
        evening_trading=data['evening_trading'],
        asset_type=data['asset_type'],
        sell=sell_direction,
        amount=amount,
    )


def prepare_spread(spread_data):
    ratio = spread_data['ratio']
    sell = spread_data['sell']
    amount = spread_data['amount']
    far_leg = prepare_leg(spread_data['far_leg'], sell, amount)
    near_leg = prepare_leg(spread_data['near_leg'], not sell, amount * ratio)
    return Spread(
        id=spread_data['id'],
        far_leg=far_leg,
        near_leg=near_leg,
        price=spread_data['price'],
        sell=sell,
        ratio=ratio,
        amount=spread_data['amount']
    )


def prepare_spreads_data(data):
    spreads = []
    for spread in data:
        spreads.append(prepare_spread(spread))
    return spreads
