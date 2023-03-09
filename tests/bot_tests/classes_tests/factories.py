import random
from decimal import Decimal

import factory

from bot.tools.classes import Asset, Spread


class AssetFactory(factory.Factory):
    class Meta:
        model = Asset

    ticker = factory.Faker('word')
    figi = factory.Faker('word')
    min_price_increment = factory.LazyFunction(
        lambda: Decimal(random.random())
    )
    lot = factory.LazyFunction(lambda: random.randint(5, 15))
    price = factory.LazyFunction(lambda: Decimal(random.randint(100, 200)))
    id = factory.LazyFunction(lambda: random.randint(0, 100))
    sell = factory.Faker('boolean')
    amount = factory.LazyFunction(lambda: random.randint(50, 100))
    executed = factory.LazyFunction(lambda: random.randint(0, 50))
    avg_exec_price = factory.LazyFunction(
        lambda: Decimal(10 * random.random())
    )
    order_placed = False
    order_id = None
    asset_type = factory.Faker('random_element', elements=('S', 'F'))
    morning_trading = factory.Faker('boolean')
    evening_trading = factory.Faker('boolean')


class SpreadFactory(factory.Factory):
    class Meta:
        model = Spread

    far_leg = AssetFactory(
        sell=True,
        amount=100,
        asset_type='F',
        morning_trading=True,
        evening_trading=True,
    )
    near_leg = AssetFactory(
        sell=False,
        amount=10000,
        asset_type='S',
        morning_trading=False,
        evening_trading=False,
    )
    sell = True
    price = factory.LazyFunction(lambda: random.randint(100, 1000))
    id = factory.LazyFunction(lambda: random.randint(0, 100))
    ratio = 100
    amount = 200
