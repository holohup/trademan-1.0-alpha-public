from base.models import Figi
from django.core.management.base import BaseCommand
from django.db import transaction

EVENING_TRADED_STOCKS = (
    'AFKS', 'AFLT', 'ALRS', 'BELU', 'CBOM', 'CHMF', 'DSKY', 'ENPG', 'FEES',
    'FESH', 'FLOT', 'GAZP', 'GMKN', 'HYDR', 'IRAO', 'LKOH', 'MAGN', 'MGNT',
    'MOEX', 'MTLR', 'MTLRP', 'MTSS', 'MVID', 'NLMK', 'NVTK', 'OGKB', 'PHOR',
    'PIKK', 'PLZL', 'POSI', 'ROSN', 'RTKM', 'RUAL', 'SBER', 'SBERP', 'SGZH',
    'SIBN', 'SMLT', 'SNGS', 'SNGSP', 'SPBE', 'TATN', 'TATNP', 'TRNFP', 'UPRO',
    'VTBR',
)
MORNING_TRADED_STOCKS = (
    'AFKS', 'AFLT', 'ALRS', 'CBOM', 'CHMF', 'DSKY', 'ENPG', 'FEES', 'GAZP',
    'GMKN', 'HYDR', 'IRAO', 'LKOH', 'MAGN', 'MGNT', 'MOEX', 'MTSS', 'NLMK',
    'NVTK', 'PHOR', 'PIKK', 'PLZL', 'ROSN', 'RTKM', 'RUAL', 'SBER', 'SBERP',
    'SNGS', 'SNGSP', 'TATN', 'TATNP', 'TRNFP', 'VTBR',
)
EVENING_NOT_TRADED_FUTURES = ()
MORNING_NOT_TRADED_FUTURES = ()


class Command(BaseCommand):
    help = (
        'Добавляет вечерние и утренние сессии в атрибуты FIGI '
        'для акций и убирает для фьючерсов'
    )

    def handle(self, *args, **options):
        updated_stocks = [
            Figi(
                pk=stock.pk,
                morning_trading=stock.ticker in MORNING_TRADED_STOCKS,
                evening_trading=stock.ticker in EVENING_TRADED_STOCKS,
            )
            for stock in Figi.objects.filter(asset_type='S')
        ]
        updated_futures = [
            Figi(
                pk=future.pk,
                morning_trading=future.basic_asset
                not in MORNING_NOT_TRADED_FUTURES,
                evening_trading=future.basic_asset
                not in EVENING_NOT_TRADED_FUTURES,
            )
            for future in Figi.objects.filter(asset_type='F')
        ]
        with transaction.atomic():
            Figi.objects.bulk_update(
                updated_stocks, ['morning_trading', 'evening_trading']
            )
            Figi.objects.bulk_update(
                updated_futures, ['morning_trading', 'evening_trading']
            )
