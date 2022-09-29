from django.db import models

class Figi(models.Model):
    figi = models.CharField(max_length=15, verbose_name='figi', unique=True)
    ticker = models.CharField(max_length=10, verbose_name='Тикер')
    name = models.CharField(max_length=100, verbose_name='Название компании')
    lot = models.PositiveIntegerField(verbose_name='Размер лота')
    min_price_increment = models.DecimalField(
        decimal_places=10, max_digits=20, verbose_name='Минимальный шаг цены'
    )
    type = models.CharField(
        max_length=1,
        choices=(('S', 'Stock'), ('F', 'Future')),
        verbose_name='Акция или фьючерс'
    )

    def __str__(self):
        return f'{self.ticker}'

    class Meta:
        unique_together = ('ticker', 'type',)
        verbose_name = 'figi'


class BaseAssetModel(models.Model):
    active = models.BooleanField(default=False, verbose_name='Активная заявка?')
    asset = models.ForeignKey(Figi, on_delete=models.PROTECT, verbose_name='Актив')
    sell = models.BooleanField(verbose_name='Продать?')
    amount = models.PositiveIntegerField(verbose_name='Количество')
    executed = models.PositiveIntegerField(default=0, verbose_name='Сколько уже исполнено')

    def __str__(self):
        action = 'Sell' if self.sell else 'Buy'
        return action + f'{self.asset.ticker}, [{self.executed}/{self.amount}] executed'

    class Meta:
        abstract = True


class SellBuy(BaseAssetModel):
    class Meta:
        verbose_name = 'Купи-Продай'
        verbose_name_plural = 'Купи-Продайки'


class Spread(BaseAssetModel):
    near_leg = models.ForeignKey(
        Figi,
        on_delete=models.PROTECT,
        verbose_name='Ближняя нога',
        related_name='near_leg'
    )
    price = models.IntegerField(verbose_name='Цена спреда')

    def __str__(self):
        action = 'Sell' if self.sell else 'Buy'
        return action + (
            f'{self.near_leg.ticker}{self.asset.ticker},'
            f'[{self.executed}/{self.amount}] executed'
        )

    class Meta:
        verbose_name = 'Спред'
        verbose_name_plural = 'Спреды'


class RestoreStops(BaseAssetModel):
    price = models.DecimalField(decimal_places=10, max_digits=20, verbose_name='Цена')

    class Meta:
        verbose_name = 'Восстановление стопов'
        verbose_name_plural = 'Восстановления стопов'

class Stops(models.Model):
    stock = models.ForeignKey(Figi, on_delete=models.PROTECT, verbose_name='Акция')
    whitelist = models.BooleanField(default=False, verbose_name='Stocks whitelist')
    stop_blacklist = models.BooleanField(default=False, verbose_name='Blacklist for longs')
    short_blacklist = models.BooleanField(default=False, verbose_name='Blacklist for shorts')

    class Meta:
        verbose_name = 'Стоп'
        verbose_name_plural = 'Стопы'