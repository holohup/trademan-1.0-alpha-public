from tools.get_patch_prepare_data import (async_get_api_data,
                                          async_post_api_data)


async def restore_stops(command, args):
    return await async_post_api_data('stop_orders')


async def save_stops(command, args):
    return await async_get_api_data('stop_orders')
