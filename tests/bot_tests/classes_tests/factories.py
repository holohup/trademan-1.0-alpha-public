import random
from decimal import Decimal

import factory

from bot.tools.classes import Asset


class AssetFactory(factory.Factory):
    class Meta:
        model = Asset

    ticker = factory.Faker('word')
    figi = factory.Faker('word')
    increment = factory.LazyFunction(lambda: Decimal(random.random()))
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
    morning_trading = factory.Faker('boolean')
    evening_trading = factory.Faker('boolean')
