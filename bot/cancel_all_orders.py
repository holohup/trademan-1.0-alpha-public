from tools.orders import cancel_all_orders


async def cancel_orders(*args, **kwargs):
    return await cancel_all_orders()


if __name__ == '__main__':
    print(cancel_orders())
