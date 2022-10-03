from tools.get_patch_prepare_data import async_get_api_data, prepare_asset_data


async def restore_stops():
    stops = prepare_asset_data(await async_get_api_data('restore_stops'))
    stops_placed = []
    for stop in stops:
        if stop.sell:
            await stop.place_short_stop(stop.price, stop.amount)
            stops_placed.append(stop.ticker)
        else:
            await stop.place_long_stop(stop.price, stop.amount)
            stops_placed.append(stop.ticker)
    return f'Stops successfully restored for {stops_placed}'

if __name__ == '__main__':
    pass
