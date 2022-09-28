from django.core.management.base import BaseCommand, CommandError
from tinkoff.invest.retrying.sync.client import RetryingClient
from tinkoff.invest.retrying.settings import RetryClientSettings
from tinkoff.invest.utils import quotation_to_decimal
from django.conf import settings
from base.models import Figi
from tinkoff.invest.schemas import RealExchange


class Command(BaseCommand):
    help = 'Обновление базы акций и фьючерсов с ТКС'

    def handle(self, *args, **options):
        with RetryingClient(
                settings.TCS_RO_TOKEN,
                RetryClientSettings(use_retry=True, max_retry_attempt=10)
        ) as client:
            try:
                response_stocks = client.instruments.shares()
                response_futures = client.instruments.futures()
            except Exception as error:
                raise CommandError(f'Could not fetch data! {error}')
        for share in response_stocks.instruments:
            if share.real_exchange == RealExchange.REAL_EXCHANGE_MOEX:
                new_values = {
                    'ticker': share.ticker,
                    'lot': share.lot,
                    'name': share.name,
                    'min_price_increment': quotation_to_decimal(share.min_price_increment),
                    'type': 'S'
                }
                tcs_stock, _ = Figi.objects.update_or_create(figi=share.figi, defaults=new_values)

        for future in response_futures.instruments:
            if (
                    future.real_exchange == RealExchange.REAL_EXCHANGE_RTS
                    and future.api_trade_available_flag is True
            ):
                new_values = {
                    'ticker': future.ticker,
                    'lot': future.lot,
                    'name': future.name,
                    'min_price_increment': quotation_to_decimal(future.min_price_increment),
                    'type': 'F'
                }
                tcs_future, _ = Figi.objects.update_or_create(figi=future.figi, defaults=new_values)

