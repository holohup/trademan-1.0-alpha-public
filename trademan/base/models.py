from django.db import models


class Figi(models.Model):
    figi = models.CharField(max_length=15, verbose_name='figi', unique=True)
    ticker = models.CharField(max_length=10, verbose_name='Тикер')
    name = models.CharField(max_length=100, verbose_name='Название компании')
    lot = models.PositiveIntegerField(verbose_name='Размер лота')
    min_price_increment = models.DecimalField(
        decimal_places=10, max_digits=20, verbose_name='Шаг цены'
    )
    asset_type = models.CharField(
        max_length=1,
        choices=(('S', 'Stock'), ('F', 'Future')),
        verbose_name='Акция или фьючерс',
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
    basic_asset = models.CharField(
        'Базовый актив', null=True, blank=True, max_length=100
    )
    morning_trading = models.BooleanField(
        'Утренние торги', default=False
    )
    evening_trading = models.BooleanField(
        'Вечерние торги', default=False
    )

    def save(self, *args, **kwargs):
        if not self.pk and self.asset_type == 'F':
            self.morning_trading = True
            self.evening_trading = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.ticker}'

    class Meta:
        unique_together = (
            'ticker',
            'asset_type',
        )
        verbose_name = 'figi'


class BaseAssetModel(models.Model):
    active = models.BooleanField(default=True, verbose_name='Активно?')
    asset = models.ForeignKey(
        Figi,
        on_delete=models.CASCADE,
        verbose_name='Актив',
        related_name='%(class)s',
    )
    sell = models.BooleanField(verbose_name='Продать?')
    amount = models.PositiveIntegerField(
        verbose_name='Количество к исполнению'
    )
    executed = models.PositiveIntegerField(
        default=0, verbose_name='Исполнено шт.'
    )
    exec_price = models.DecimalField(
        decimal_places=10,
        max_digits=20,
        verbose_name='Ср. цена исполн.',
        default=0,
    )

    def __str__(self):
        action = 'Sell' if self.sell else 'Buy'
        return f'''{action} {self.asset.ticker},
         [{self.executed}/{self.amount}] executed'''

    class Meta:
        abstract = True


class SellBuy(BaseAssetModel):
    class Meta:
        verbose_name = 'Купи-Продай'
        verbose_name_plural = 'Купи-Продайки'


class SpreadStats(models.Model):
    far_leg_executed = models.PositiveIntegerField(
        'Far leg executed', default=0
    )
    near_leg_executed = models.PositiveIntegerField(
        'Near leg executed', default=0
    )
    far_leg_avg_price = models.DecimalField(
        decimal_places=10,
        max_digits=20,
        verbose_name='Avg far leg execution price',
        default=0,
    )
    near_leg_avg_price = models.DecimalField(
        decimal_places=10,
        max_digits=20,
        verbose_name='Avg near leg execution price',
        default=0,
    )

    @property
    def avg_exec_price(self):
        if self.near_leg_executed == 0 and self.far_leg_executed == 0:
            return 0
        return (
            self.far_leg_avg_price * self.far_leg_executed
            - self.near_leg_avg_price * self.near_leg_executed
        ) / self.far_leg_executed


class Spread(models.Model):
    far_leg = models.ForeignKey(
        Figi,
        on_delete=models.CASCADE,
        verbose_name='Дальн. нога',
        related_name='far_spreads',
    )
    near_leg = models.ForeignKey(
        Figi,
        on_delete=models.CASCADE,
        verbose_name='Ближн. нога',
        related_name='near_spreads',
    )
    stats = models.ForeignKey(
        SpreadStats,
        on_delete=models.CASCADE,
        verbose_name='Execution stats',
        related_name='spreads',
    )
    active = models.BooleanField(default=True, verbose_name='Активно?')
    sell = models.BooleanField(verbose_name='Продать?')
    price = models.IntegerField(verbose_name='Цена спреда')
    amount = models.PositiveIntegerField(verbose_name='To execute')
    editable_ratio = models.PositiveSmallIntegerField(
        'Far leg / near leg even ratio', default=0
    )

    @property
    def executed(self):
        return self.stats.far_leg_executed

    @property
    def avg_exec_price(self):
        return self.stats.avg_exec_price

    @property
    def ratio(self):
        if self.editable_ratio != 0:
            return self.editable_ratio
        if (
            self.far_leg.asset_type == 'F'
            and self.far_leg.basic_asset == self.near_leg.ticker
        ):
            return self.far_leg.basic_asset_size
        if self.far_leg.asset_type == self.near_leg.asset_type:
            return 1
        return 0

    def __str__(self):
        action = 'Sell ' if self.sell else 'Buy '
        return action + (
            f'{self.far_leg.ticker} - {self.near_leg.ticker}, '
            f'[{self.executed}/{self.amount}]'
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
        related_name='stops',
    )
    whitelist = models.BooleanField(
        default=False, verbose_name='Stocks whitelist'
    )
    stop_blacklist = models.BooleanField(
        default=False, verbose_name='Blacklist for longs'
    )
    short_blacklist = models.BooleanField(
        default=False, verbose_name='Blacklist for shorts'
    )

    class Meta:
        verbose_name = 'Стоп'
        verbose_name_plural = 'Стопы'
