from django.core.management.base import BaseCommand
from base.models import Figi, Stops

STOP_BLACKLIST = ['RNFT', 'POLY', 'RENI', 'KRKOP', 'RGSS', 'SPBE']
SHORT_BLACKLIST = ['SBER', 'SBERP', 'VSMO', 'GAZP', 'RTKM', 'RTKMP', 'RNFT']
WHITELIST = [
    'ROSN', 'GAZP', 'KRKNP', 'NKNC', 'LENT', 'MRKP', 'KAZTP', 'VSMO', 'OKEY', 'RTKMP', 'PMSB', 'HHRU',
    'AKRN', 'QIWI', 'KZOS', 'SELG', 'ETLN', 'NMTP', 'LSNGP', 'BANE', 'KAZT', 'NKNCP', 'ENRU', 'TGKB',
    'RSTI', 'HYDR', 'TATNP', 'MTLRP', 'DSKY', 'UPRO', 'GLTR', 'OGKB', 'KZOSP', 'BSPB', 'MVID', 'RTKM',
    'BELU', 'ENPG', 'MDMG', 'TGKA', 'LSRG', 'AGRO', 'BANEP', 'CHMF', 'MTSS', 'OZON', 'IRAO', 'POSI',
    'RUAL', 'POLY', 'SGZH', 'RASP', 'TRNFP', 'FIVE', 'MTLR', 'SMLT', 'SNGSP', 'TATN', 'SBER', 'GAZP',
    'LKOH', 'AFLT', 'NVTK', 'ROSN', 'SBERP', 'GMKN', 'VTBR', 'YNDX', 'PLZL', 'PHOR', 'AFKS', 'FESH',
    'NLMK', 'ALRS', 'MOEX', 'MGNT', 'VKCO', 'SNGS', 'MAGN', 'TCSG', 'TTLK', 'PMSBP',
]


class Command(BaseCommand):
    help = 'Восстановление дефолтных black_list и white_list для автостопов'

    def handle(self, *args, **options):
        qs = Figi.objects.filter(type='S')
        for stock in qs:
            new_values = {
                'whitelist': stock.ticker in WHITELIST,
                'stop_blacklist': stock.ticker in STOP_BLACKLIST,
                'short_blacklist': stock.ticker in SHORT_BLACKLIST,
            }
            stop_stock, _ = Stops.objects.update_or_create(asset=stock, defaults=new_values)
