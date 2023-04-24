from django.core.management.base import BaseCommand
from django.db import transaction

from base.models import Figi

EVENING_TRADED_STOCKS = (
    'AFKS', 'AFLT', 'ALRS', 'BELU', 'CBOM', 'CHMF', 'DSKY', 'ENPG', 'FEES',
    'FESH', 'FLOT', 'GAZP', 'GMKN', 'HYDR', 'IRAO', 'LKOH', 'MAGN', 'MGNT',
    'MOEX', 'MTLR', 'MTLRP', 'MTSS', 'MVID', 'NLMK', 'NVTK', 'OGKB', 'PHOR',
    'PIKK', 'PLZL', 'POSI', 'ROSN', 'RTKM', 'RUAL', 'SBER', 'SBERP', 'SGZH',
    'SIBN', 'SMLT', 'SNGS', 'SNGSP', 'SPBE', 'TATN', 'TATNP', 'TRNFP', 'UPRO',
    'VTBR', 'AGRO'
)
MORNING_TRADED_STOCKS = (
    'AFKS', 'AFLT', 'ALRS', 'CBOM', 'CHMF', 'DSKY', 'ENPG', 'FEES', 'GAZP',
    'GMKN', 'HYDR', 'IRAO', 'LKOH', 'MAGN', 'MGNT', 'MOEX', 'MTSS', 'NLMK',
    'NVTK', 'PHOR', 'PIKK', 'PLZL', 'ROSN', 'RTKM', 'RUAL', 'SBER', 'SBERP',
    'SNGS', 'SNGSP', 'TATN', 'TATNP', 'TRNFP', 'VTBR',
)
EVENING_NOT_TRADED_FUTURES = ()
MORNING_NOT_TRADED_FUTURES = ()


def update_figis():
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
    updated_bonds = [
        Figi(
            pk=bond.pk,
            evening_trading=(
                bond.ticker.startswith('SU') and bond.name.startswith('ОФЗ')
            ),
        )
        for bond in Figi.objects.filter(asset_type='B')
    ]
    with transaction.atomic():
        Figi.objects.bulk_update(
            updated_stocks, ['morning_trading', 'evening_trading']
        )
        Figi.objects.bulk_update(
            updated_futures, ['morning_trading', 'evening_trading']
        )
        Figi.objects.bulk_update(updated_bonds, ['evening_trading'])
    return 'Stocks, futures and bonds updated according to lists in cmd.'


def null_stocks_morning_trading():
    updated_stocks = [
        Figi(pk=stock.pk, morning_trading=False)
        for stock in Figi.objects.filter(asset_type='S', morning_trading=True)
    ]
    with transaction.atomic():
        Figi.objects.bulk_update(updated_stocks, ['morning_trading'])
    return 'All stocks morning trading attribute sets to False'


class Command(BaseCommand):
    help = '''Добавляет вечерние и утренние сессии в атрибуты FIGI для акций и
        убирает для фьючерсов. Список акций с утренними торгами взят с сайта
        мосбиржи, но для Тинькова почему-то не актуален - можно вызвать с
        аргументом nomorning, чтобы обнулить поле morning_trading у акций.
        Также добавляет флаг вечерних торгов бондам.'''

    def add_arguments(self, parser):
        parser.add_argument(
            'arg',
            nargs='?',
            default=None,
            type=str,
            help='Null stocks morning_trading',
        )

    def handle(self, *args, **options):
        if options['arg'] == 'nomorning':
            return null_stocks_morning_trading()
        return update_figis()
