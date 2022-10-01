from django.core.management.base import BaseCommand, CommandError
from tinkoff.invest.retrying.sync.client import RetryingClient
from tinkoff.invest.retrying.settings import RetryClientSettings
from tinkoff.invest.utils import quotation_to_decimal
from django.conf import settings
from base.models import Figi
from tinkoff.invest.schemas import RealExchange, Share, Future
from typing import Any


def prevalidate_instrument(inst: any([Share, Future]), _type: str) -> bool:
    # if quotation_to_decimal(inst.min_price_increment) <= 0:
    #     print(inst.trading_status, inst.ticker)
    if _type == 'Share':
        return all((
                inst.real_exchange == RealExchange.REAL_EXCHANGE_MOEX,
                quotation_to_decimal(inst.min_price_increment) > 0,
        ))
    if _type == 'Future':
        return all((
            inst.real_exchange == RealExchange.REAL_EXCHANGE_RTS,
            quotation_to_decimal(inst.min_price_increment) > 0,
        ))


def fill_fields(inst: any([Share, Future])) -> dict:
    return {
        'ticker': inst.ticker,
        'lot': inst.lot,
        'name': inst.name,
        'min_price_increment': quotation_to_decimal(inst.min_price_increment),
        'api_trading_available': inst.api_trade_available_flag,
        'short_enabled': inst.short_enabled_flag,
        'buy_enabled': inst.buy_available_flag,
        'sell_enabled': inst.sell_available_flag
    }


class Command(BaseCommand):
    help = 'Обновление базы акций и фьючерсов с ТКС'

    def handle(self, *args, **options):
        clean_up_flag = False
        received_figi = set()
        result_message = ''
        with RetryingClient(
                settings.TCS_RO_TOKEN,
                RetryClientSettings(use_retry=True, max_retry_attempt=10)
        ) as client:
            try:
                response_stocks = client.instruments.shares()
                result_message += 'Stocks update received\n'
                response_futures = client.instruments.futures()
                result_message += 'Futures update received\n'
            except Exception as error:
                result_message += 'Error updating prices\n'
                raise CommandError(f'Data update failed! {error}')
            else:
                clean_up_flag = True

                for share in response_stocks.instruments:
                    if prevalidate_instrument(inst=share, _type='Share'):
                        new_values = fill_fields(share)
                        new_values.update(type='S')
                        received_figi.add(share.figi)
                        tcs_stock, _ = Figi.objects.update_or_create(figi=share.figi, defaults=new_values)

                for future in response_futures.instruments:
                    if prevalidate_instrument(inst=future, _type='Future'):
                        new_values = fill_fields(future)
                        new_values.update(type='F')
                        received_figi.add(future.figi)
                        tcs_future, _ = Figi.objects.update_or_create(figi=future.figi, defaults=new_values)

                if clean_up_flag:
                    for figi in Figi.objects.all():
                        if figi.figi not in received_figi:
                            result_message += f'Deleting figi with ticker {figi}\n'
                            figi.delete()
            finally:
                return result_message

