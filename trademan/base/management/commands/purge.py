from django.core.management.base import BaseCommand, CommandError
from tinkoff.invest.retrying.sync.client import RetryingClient
from tinkoff.invest.retrying.settings import RetryClientSettings
from tinkoff.invest.utils import quotation_to_decimal
from django.conf import settings
from base.models import Figi
from tinkoff.invest.schemas import RealExchange


class Command(BaseCommand):
    help = 'Обнуление базы'

    def handle(self, *args, **options):
        Figi.objects.all().delete()