import sys
from typing import NamedTuple

from base.models import Figi
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from tinkoff.invest.retrying.settings import RetryClientSettings
from tinkoff.invest.retrying.sync.client import RetryingClient
from tinkoff.invest.schemas import Future, RealExchange, Share
from tinkoff.invest.utils import quotation_to_decimal


class InstrumentSettings(NamedTuple):
    db_short: str
    exchange: RealExchange
    tcs_name: str


INSTRUMENTS = {
    'Stocks': InstrumentSettings(
        'S', RealExchange.REAL_EXCHANGE_MOEX, 'shares'
    ),
    'Futures': InstrumentSettings(
        'F', RealExchange.REAL_EXCHANGE_MOEX, 'futures'
    ),
}


if not all(
    [settings.TCS_RO_TOKEN, settings.TCS_RW_TOKEN, settings.TCS_ACCOUNT_ID]
):
    message = (
        'Не удалось загрузить все переменные из окружения. Переменные:\n'
        f'TCS_ACCOUNT_ID: {settings.TCS_ACCOUNT_ID}\n'
        f'TCS_RW_TOKEN: {settings.TCS_RW_TOKEN}\n'
        f'TCS_RO_TOKEN: {settings.TCS_RO_TOKEN}'
    )
    sys.exit(message)


def prevalidate_instrument(inst: any([Share, Future]), type: str) -> bool:
    return all(
        (
            inst.real_exchange == INSTRUMENTS[type].exchange,
            quotation_to_decimal(inst.min_price_increment) > 0,
        )
    )


def fill_fields(inst: any([Share, Future]), type: str) -> dict:
    result = {
        'ticker': inst.ticker,
        'lot': inst.lot,
        'name': inst.name,
        'min_price_increment': quotation_to_decimal(inst.min_price_increment),
        'api_trading_available': inst.api_trade_available_flag,
        'short_enabled': inst.short_enabled_flag,
        'buy_enabled': inst.buy_available_flag,
        'sell_enabled': inst.sell_available_flag,
        'type': INSTRUMENTS[type].db_short,
    }
    if type == 'Futures':
        result['basic_asset_size'] = int(
            quotation_to_decimal(inst.basic_asset_size)
        )
    return result


def get_api_response(instrument):
    with RetryingClient(
        settings.TCS_RO_TOKEN,
        RetryClientSettings(use_retry=True, max_retry_attempt=10),
    ) as client:
        try:
            return getattr(
                client.instruments, INSTRUMENTS[instrument].tcs_name
            )()
        except Exception as error:
            raise CommandError(f'Data update failed! {error}')


def update_db(response, type):
    updated = 0
    figis = set()
    for inst in response.instruments:
        if not prevalidate_instrument(inst=inst, type=type):
            continue
        updated += 1
        new_values = fill_fields(inst, type)
        figis.add(inst.figi)
        Figi.objects.update_or_create(figi=inst.figi, defaults=new_values)
    return updated, figis


def clean_up(type, figis):
    result = ''
    for figi in Figi.objects.filter(type=INSTRUMENTS[type].db_short):
        if figi.figi not in figis:
            result += f'Deleting figi with ticker {figi}\n'
            figi.delete()
    return result


class Command(BaseCommand):
    help = 'Обновление базы акций и фьючерсов с ТКС'

    def handle(self, *args, **options):
        new_figi = set()
        result_message = ''
        clean_up_flag = True
        upd_insts = {type: 0 for type in INSTRUMENTS.keys()}
        for inst_type in INSTRUMENTS.keys():
            response = get_api_response(inst_type)
            result_message += f'{inst_type} update received\n'
            upd_insts[inst_type], new_figi = update_db(response, inst_type)
            result_message += f'{inst_type} filtered: {upd_insts[inst_type]}\n'
            if clean_up_flag and upd_insts[inst_type] > 0:
                result_message += clean_up(inst_type, new_figi)

        call_command('stopsdb')
        result_message += 'Stops db updated\n'
        return result_message
