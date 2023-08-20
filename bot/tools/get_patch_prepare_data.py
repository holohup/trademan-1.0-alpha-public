import json
from decimal import Decimal
from http import HTTPStatus
from typing import List
from urllib import request

import aiohttp
from queue_handler import QUEUE
from settings import (ENDPOINT_HOST, ENDPOINTS, RETRY_SETTINGS, TCS_ACCOUNT_ID,
                      TCS_RO_TOKEN)
from tinkoff.invest.retrying.aio.client import AsyncRetryingClient
from tinkoff.invest.retrying.sync.client import RetryingClient
from tinkoff.invest.utils import quotation_to_decimal
from tools.adapters import SellBuyToJsonAdapter, SpreadToJsonAdapter
from tools.classes import Asset, Spread


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


async def async_patch_sellbuy(sellbuy: Asset):
    data = SellBuyToJsonAdapter(sellbuy).output
    url = ENDPOINT_HOST + ENDPOINTS['sellbuy'] + str(sellbuy.id) + '/'
    async with aiohttp.ClientSession() as session:
        async with session.patch(url, json=data) as response:
            if response.status == HTTPStatus.OK:
                return True
            response_text = await response.text()
            await QUEUE.put(f'Error patching sellbuy. {response_text[:4000]}')
            return False


async def async_create_sellbuy(sellbuy: Asset):
    data = {
        'figi': sellbuy.figi,
        'sell': sellbuy.sell,
        'amount': sellbuy.amount,
    }
    url = ENDPOINT_HOST + ENDPOINTS['sellbuy']
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            response_json = await response.json()
            if response.status == HTTPStatus.CREATED:
                return response_json['id']
            raise ConnectionError(
                f'Error creating sellbuy. {str(response_json)}'
            )


async def async_get_api_data(command: str):
    url = ENDPOINT_HOST + ENDPOINTS[command]
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()


async def async_post_api_data(command: str):
    url = ENDPOINT_HOST + ENDPOINTS[command]
    async with aiohttp.ClientSession() as session:
        async with session.post(url) as response:
            text = await response.text()
            return text.strip('"')


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


async def get_current_prices_by_uid(assets):
    uids = [asset.uid for asset in assets]
    async with AsyncRetryingClient(TCS_RO_TOKEN, RETRY_SETTINGS) as client:
        response = await client.market_data.get_last_prices(instrument_id=uids)
    return {
        item.instrument_uid: quotation_to_decimal(item.price)
        for item in response.last_prices
    }


def get_portfolio_positions():
    with RetryingClient(TCS_RO_TOKEN, RETRY_SETTINGS) as client:
        response = client.operations.get_portfolio(account_id=TCS_ACCOUNT_ID)
        return response.positions


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


def parse_ticker_info(ticker: str) -> dict:
    url = ENDPOINT_HOST + ENDPOINTS['ticker'] + ticker + '/'
    return json.loads(request.urlopen(url).read())


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
        amount=spread_data['amount'],
    )


def prepare_spreads_data(data):
    return [prepare_spread(spread) for spread in data]


def prepare_sellbuy_asset(data):
    return Asset(
        id=data['id'],
        figi=data['figi'],
        ticker=data['ticker'],
        min_price_increment=Decimal(data['min_price_increment']),
        lot=data['lot'],
        executed=data['executed'],
        avg_exec_price=Decimal(data['avg_exec_price']),
        morning_trading=data['morning_trading'],
        evening_trading=data['evening_trading'],
        asset_type=data['asset_type'],
        sell=data['sell'],
        amount=data['amount'],
    )


def prepare_assets_data(data) -> List[Asset]:
    return [prepare_sellbuy_asset(asset) for asset in data]
