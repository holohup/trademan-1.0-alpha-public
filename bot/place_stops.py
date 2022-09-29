from settings import LONG_LEVELS, SHORT_LEVELS, STOPS_SUM
from tools.classes import Asset
from tools.get_data import get_shorts, get_stops
from tools.orders import get_current_prices
# from tools.utils import check_for_stop
# from bot import updater

def prepare_asset_data(data):
    assets = []
    for asset in data:
        assets.append(Asset(
            figi=asset['figi'],
            increment=asset['increment'],
            ticker=asset['ticker'],
            lot=asset['lot']
        ))
    return get_current_prices(assets)

def price_is_valid(price):
    return True if price > 0 else False

def place_long_stops():
    stops_assets = get_stops()
    assets = prepare_asset_data(stops_assets)
    orders = []
    for asset in assets:
        if price_is_valid(asset.price):
            for discount in LONG_LEVELS:
                stop_price = (100-discount) * asset.price / 100
                orders.append([asset, stop_price, int(STOPS_SUM / stop_price)])
        else:
            raise ValueError(f'Price is <=0! {asset}, {asset.price}')
    orders_placed = 0
    for order in orders:
        # if check_for_stop():
        #     return f'cancelling placing orders. total {orders_placed} placed.'
        order[0].place_long_stop(order[1], order[2])
        orders_placed += 1
    return f'Stop placement complete. {orders_placed} stops placed.\n' \
           f'Levels in %: {LONG_LEVELS}, sum: {STOPS_SUM}'


def place_short_stops():
    shorts_assets = get_shorts()
    assets = prepare_asset_data(shorts_assets)
    orders = []
    for asset in assets:
        if price_is_valid(asset.price):
            for discount in SHORT_LEVELS:
                stop_price = (100+discount) * asset.price / 100
                orders.append([asset, stop_price, int(STOPS_SUM / stop_price)])
        else:
            raise ValueError(f'Price is <=0! {asset}, {asset.price}')
    orders_placed = 0
    for order in orders:
        # if check_for_stop():
        #     return f'cancelling placing orders. total {orders_placed} placed.'
        order[0].place_short_stop(order[1], order[2])
        orders_placed += 1
    return f'Short stops placement complete. {orders_placed} stops placed.\n' \
           f'Levels in %: {SHORT_LEVELS}, sum: {STOPS_SUM}'


if __name__ == '__main__':
    print(place_long_stops())
    # print(place_short_stops())
