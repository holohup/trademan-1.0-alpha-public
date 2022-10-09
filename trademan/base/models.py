from django.db import models


class Figi(models.Model):
    figi = models.CharField(max_length=15, verbose_name='figi', unique=True)
    ticker = models.CharField(max_length=10, verbose_name='Тикер')
    name = models.CharField(max_length=100, verbose_name='Название компании')
    lot = models.PositiveIntegerField(verbose_name='Размер лота')
    min_price_increment = models.DecimalField(
        decimal_places=10, max_digits=20, verbose_name='Шаг цены'
    )
    type = models.CharField(
        max_length=1,
        choices=(('S', 'Stock'), ('F', 'Future'), ('B', 'Bond')),
        verbose_name='Акция или фьючерс'
    )
    api_trading_available = models.BooleanField(verbose_name='API')
    short_enabled = models.BooleanField(verbose_name='Short')
    buy_enabled = models.BooleanField(verbose_name='Buy')
    sell_enabled = models.BooleanField(verbose_name='Sell')
    basic_asset_size = models.IntegerField(
        'Коли-во б. актива во фьючерсе',
        null=True,
        blank=True,
    )

    def __str__(self):
        return f'{self.ticker}'

    class Meta:
        unique_together = ('ticker', 'type',)
        verbose_name = 'figi'


class BaseAssetModel(models.Model):
    active = models.BooleanField(default=True, verbose_name='Активная заявка?')
    asset = models.ForeignKey(
        Figi,
        on_delete=models.CASCADE,
        verbose_name='Актив',
        related_name='%(class)s'
    )
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
    asset = models.ForeignKey(
        Figi,
        on_delete=models.CASCADE,
        verbose_name='Дальняя нога',
        related_name='%(class)s'
    )
    near_leg = models.ForeignKey(
        Figi,
        on_delete=models.CASCADE,
        verbose_name='Ближняя нога',
        related_name='near_leg'
    )
    price = models.IntegerField(verbose_name='Цена спреда')

    def __str__(self):
        action = 'Sell ' if self.sell else 'Buy '
        return action + (
            f'{self.near_leg.ticker} - {self.asset.ticker}, '
            f'[{self.executed}/{self.amount}] executed'
        )

    class Meta:
        verbose_name = 'Спред'
        verbose_name_plural = 'Спреды'


class RestoreStops(BaseAssetModel):
    price = models.FloatField(verbose_name='Цена')

    class Meta:
        verbose_name = 'Восстановление стопов'
        verbose_name_plural = 'Восстановления стопов'


class Stops(models.Model):
    asset = models.ForeignKey(
        Figi,
        on_delete=models.CASCADE,
        verbose_name='Акция',
        related_name='stops'
    )
    whitelist = models.BooleanField(default=False, verbose_name='Stocks whitelist')
    stop_blacklist = models.BooleanField(default=False, verbose_name='Blacklist for longs')
    short_blacklist = models.BooleanField(default=False, verbose_name='Blacklist for shorts')

    class Meta:
        verbose_name = 'Стоп'
        verbose_name_plural = 'Стопы'


class Bonds(models.Model):
    asset = models.ForeignKey(
        Figi,
        on_delete=models.CASCADE,
        verbose_name='Облигация',
        related_name='bonds'
    )
    whitelist = models.BooleanField(default=True, verbose_name='Bonds whitelist')

    class Meta:
        verbose_name = 'Облигация'
        verbose_name_plural = 'Облигации'
