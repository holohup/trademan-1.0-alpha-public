import datetime
from decimal import Decimal

import pytest
from tinkoff.invest.schemas import (Future, FuturesResponse, MoneyValue,
                                    Quotation, RealExchange)
from tinkoff.invest.schemas import SecurityTradingStatus as STS
from tinkoff.invest.schemas import Share, SharesResponse, ShareType

from bot.scanner.scanner import FutureData, StockData, YieldingSpread


@pytest.fixture
def futures_response():
    return FuturesResponse(
        [
            Future(
                figi='FUTYNDF06230',
                ticker='YNM3',
                class_code='SPBFUT',
                lot=1,
                currency='rub',
                klong=Quotation(units=2, nano=0),
                kshort=Quotation(units=2, nano=0),
                dlong=Quotation(units=0, nano=250000000),
                dshort=Quotation(units=0, nano=249900000),
                dlong_min=Quotation(units=0, nano=134000000),
                dshort_min=Quotation(units=0, nano=118000000),
                short_enabled_flag=True,
                name='YNDF-6.23 Яндекс',
                exchange='FORTS',
                first_trade_date=datetime.datetime(
                    2022, 9, 1, 20, 59, 59, tzinfo=datetime.timezone.utc
                ),
                last_trade_date=datetime.datetime(
                    2033, 6, 15, 20, 59, 59, tzinfo=datetime.timezone.utc
                ),
                futures_type='DELIVERY_TYPE_PHYSICAL_DELIVERY',
                asset_type='TYPE_SECURITY',
                basic_asset='YNDX',
                basic_asset_size=Quotation(units=10, nano=0),
                country_of_risk='RU',
                country_of_risk_name='Российская Федерация',
                sector='SECTOR_TELECOM',
                expiration_date=datetime.datetime(
                    2033, 6, 16, 0, 0, tzinfo=datetime.timezone.utc
                ),
                trading_status=STS.SECURITY_TRADING_STATUS_NORMAL_TRADING,
                otc_flag=False,
                buy_available_flag=True,
                sell_available_flag=True,
                min_price_increment=Quotation(units=1, nano=0),
                api_trade_available_flag=True,
                uid='eb2b8f57-5fb6-4dd0-a8d5-424f5a5a9cd4',
                real_exchange=RealExchange.REAL_EXCHANGE_MOEX,
                position_uid='1f9da0cd-e53e-4ee7-a6e7-ba206bcecaaa',
                basic_asset_position_uid='cb51e157-1f73-4c62-baac-93f11755056a',
                for_iis_flag=True,
                first_1min_candle_date=datetime.datetime(
                    2022, 9, 20, 7, 30, tzinfo=datetime.timezone.utc
                ),
                first_1day_candle_date=datetime.datetime(
                    2022, 9, 20, 7, 0, tzinfo=datetime.timezone.utc
                ),
            ),
            Future(
                figi='FUTSPYF09220',
                ticker='SFU2',
                class_code='SPBFUT',
                lot=1,
                currency='rub',
                klong=Quotation(units=2, nano=0),
                kshort=Quotation(units=2, nano=0),
                dlong=Quotation(units=0, nano=244400000),
                dshort=Quotation(units=0, nano=529900000),
                dlong_min=Quotation(units=0, nano=130800000),
                dshort_min=Quotation(units=0, nano=236900000),
                short_enabled_flag=True,
                name='SPYF-9.22 S&P 500',
                exchange='FORTS',
                first_trade_date=datetime.datetime(
                    2021, 9, 13, 20, 59, 59, tzinfo=datetime.timezone.utc
                ),
                last_trade_date=datetime.datetime(
                    2022, 9, 16, 20, 59, 59, tzinfo=datetime.timezone.utc
                ),
                futures_type='DELIVERY_TYPE_CASH_SETTLEMENT',
                asset_type='TYPE_INDEX',
                basic_asset='SPDR S&P 500 ETF Trust',
                basic_asset_size=Quotation(units=1, nano=0),
                country_of_risk='RU',
                country_of_risk_name='Российская Федерация',
                sector='',
                expiration_date=datetime.datetime(
                    2022, 9, 16, 0, 0, tzinfo=datetime.timezone.utc
                ),
                trading_status=STS.SECURITY_TRADING_STATUS_NOT_AVAILABLE_FOR_TRADING,
                otc_flag=False,
                buy_available_flag=True,
                sell_available_flag=True,
                min_price_increment=Quotation(units=0, nano=10000000),
                api_trade_available_flag=True,
                uid='1f9a6138-c81d-470e-8927-60d3efd6b9bd',
                real_exchange=RealExchange.REAL_EXCHANGE_RTS,
                position_uid='1f9a603a-2e92-4336-adfa-7606689a05bc',
                basic_asset_position_uid='',
                for_iis_flag=True,
                first_1min_candle_date=datetime.datetime(
                    2021, 9, 13, 9, 0, tzinfo=datetime.timezone.utc
                ),
                first_1day_candle_date=datetime.datetime(
                    2021, 9, 13, 7, 0, tzinfo=datetime.timezone.utc
                ),
            ),
            Future(
                figi='FUTSNGP06220',
                ticker='SGM2',
                class_code='SPBFUT',
                lot=1,
                currency='rub',
                klong=Quotation(units=2, nano=0),
                kshort=Quotation(units=2, nano=0),
                dlong=Quotation(units=0, nano=250000000),
                dshort=Quotation(units=0, nano=250000000),
                dlong_min=Quotation(units=0, nano=134000000),
                dshort_min=Quotation(units=0, nano=118000000),
                short_enabled_flag=True,
                name='SNGP-6.22 Сургутнефтегаз (привилегированные)',
                exchange='FORTS',
                first_trade_date=datetime.datetime(
                    2021, 12, 2, 20, 59, 59, tzinfo=datetime.timezone.utc
                ),
                last_trade_date=datetime.datetime(
                    2022, 6, 16, 20, 59, 59, tzinfo=datetime.timezone.utc
                ),
                futures_type='DELIVERY_TYPE_PHYSICAL_DELIVERY',
                asset_type='TYPE_SECURITY',
                basic_asset='SNGSP',
                basic_asset_size=Quotation(units=1000, nano=0),
                country_of_risk='RU',
                country_of_risk_name='Российская Федерация',
                sector='SECTOR_ENERGY',
                expiration_date=datetime.datetime(
                    2022, 6, 17, 0, 0, tzinfo=datetime.timezone.utc
                ),
                trading_status=STS.SECURITY_TRADING_STATUS_NOT_AVAILABLE_FOR_TRADING,
                otc_flag=False,
                buy_available_flag=True,
                sell_available_flag=True,
                min_price_increment=Quotation(units=0, nano=0),
                api_trade_available_flag=True,
                uid='1f99a3b6-eed5-4d39-8c6a-ff2d484ce282',
                real_exchange=RealExchange.REAL_EXCHANGE_MOEX,
                position_uid='1f99a20e-835d-42b3-b66b-6f50ee3d47c8',
                basic_asset_position_uid='178797ec-6065-4b32-b6ba-a79a54bc1479',
                for_iis_flag=True,
                first_1min_candle_date=datetime.datetime(
                    2021, 12, 13, 8, 0, tzinfo=datetime.timezone.utc
                ),
                first_1day_candle_date=datetime.datetime(
                    2021, 12, 13, 7, 0, tzinfo=datetime.timezone.utc
                ),
            ),
            Future(
                figi='FUTALRS12220',
                ticker='ALZ2',
                class_code='SPBFUT',
                lot=1,
                currency='rub',
                klong=Quotation(units=2, nano=0),
                kshort=Quotation(units=2, nano=0),
                dlong=Quotation(units=0, nano=380300000),
                dshort=Quotation(units=0, nano=361000000),
                dlong_min=Quotation(units=0, nano=212800000),
                dshort_min=Quotation(units=0, nano=166600000),
                short_enabled_flag=True,
                name='ALRS-12.22 Алроса',
                exchange='FORTS',
                first_trade_date=datetime.datetime(
                    2022, 2, 18, 20, 59, 59, tzinfo=datetime.timezone.utc
                ),
                last_trade_date=datetime.datetime(
                    2033, 12, 15, 20, 59, 59, tzinfo=datetime.timezone.utc
                ),
                futures_type='DELIVERY_TYPE_PHYSICAL_DELIVERY',
                asset_type='TYPE_SECURITY',
                basic_asset='ALRS',
                basic_asset_size=Quotation(units=100, nano=0),
                country_of_risk='RU',
                country_of_risk_name='Российская Федерация',
                sector='SECTOR_MATERIALS',
                expiration_date=datetime.datetime(
                    2033, 12, 16, 0, 0, tzinfo=datetime.timezone.utc
                ),
                trading_status=STS.SECURITY_TRADING_STATUS_NOT_AVAILABLE_FOR_TRADING,
                otc_flag=False,
                buy_available_flag=False,
                sell_available_flag=True,
                min_price_increment=Quotation(units=1, nano=0),
                api_trade_available_flag=True,
                uid='99e89917-5f0b-4c28-97a4-dc4b43c8ff4a',
                real_exchange=RealExchange.REAL_EXCHANGE_MOEX,
                position_uid='1f9b211b-de09-40e8-83de-b69d453c7fe9',
                basic_asset_position_uid='962f3a99-3b2d-4af6-995e-26be412b7b22',
                for_iis_flag=True,
                first_1min_candle_date=datetime.datetime(
                    2022, 4, 5, 8, 50, tzinfo=datetime.timezone.utc
                ),
                first_1day_candle_date=datetime.datetime(
                    2022, 4, 5, 7, 0, tzinfo=datetime.timezone.utc
                ),
            ),
            Future(
                figi='FUTAFLT03230',
                ticker='AFH3',
                class_code='SPBFUT',
                lot=1,
                currency='rub',
                klong=Quotation(units=2, nano=0),
                kshort=Quotation(units=2, nano=0),
                dlong=Quotation(units=0, nano=253300000),
                dshort=Quotation(units=0, nano=249900000),
                dlong_min=Quotation(units=0, nano=135900000),
                dshort_min=Quotation(units=0, nano=118000000),
                short_enabled_flag=True,
                name='AFLT-3.23 Аэрофлот',
                exchange='FORTS',
                first_trade_date=datetime.datetime(
                    2022, 8, 15, 20, 59, 59, tzinfo=datetime.timezone.utc
                ),
                last_trade_date=datetime.datetime(
                    2033, 3, 16, 20, 59, 59, tzinfo=datetime.timezone.utc
                ),
                futures_type='DELIVERY_TYPE_PHYSICAL_DELIVERY',
                asset_type='TYPE_SECURITY',
                basic_asset='ALRS',
                basic_asset_size=Quotation(units=100, nano=0),
                country_of_risk='RU',
                country_of_risk_name='Российская Федерация',
                sector='SECTOR_CONSUMER',
                expiration_date=datetime.datetime(
                    2033, 3, 17, 0, 0, tzinfo=datetime.timezone.utc
                ),
                trading_status=STS.SECURITY_TRADING_STATUS_NOT_AVAILABLE_FOR_TRADING,
                otc_flag=False,
                buy_available_flag=True,
                sell_available_flag=True,
                min_price_increment=Quotation(units=1, nano=0),
                api_trade_available_flag=True,
                uid='a8fb2fa6-d5a2-4b12-9cbc-13c60610a425',
                real_exchange=RealExchange.REAL_EXCHANGE_MOEX,
                position_uid='1f9ce2e4-02df-4887-aeb1-df6f2634651f',
                basic_asset_position_uid='8615c3f2-758c-42be-a69d-c97ac9d95f04',
                for_iis_flag=True,
                first_1min_candle_date=datetime.datetime(
                    2022, 8, 29, 13, 20, tzinfo=datetime.timezone.utc
                ),
                first_1day_candle_date=datetime.datetime(
                    2022, 8, 29, 7, 0, tzinfo=datetime.timezone.utc
                ),
            ),
        ]
    )


@pytest.fixture
def shares_response():
    return SharesResponse(
        [
            Share(
                figi='BBG000BN56Q9',
                ticker='ALRS',
                class_code='TQBR',
                isin='RU000A0JSQ90',
                lot=10,
                currency='rub',
                klong=Quotation(units=2, nano=0),
                kshort=Quotation(units=2, nano=0),
                dlong=Quotation(units=1, nano=0),
                dshort=Quotation(units=1, nano=0),
                dlong_min=Quotation(units=1, nano=0),
                dshort_min=Quotation(units=1, nano=0),
                short_enabled_flag=False,
                name='Детский Мир',
                exchange='MOEX_PLUS',
                ipo_date=datetime.datetime(
                    2014, 2, 11, 0, 0, tzinfo=datetime.timezone.utc
                ),
                issue_size=739000000,
                country_of_risk='RU',
                country_of_risk_name='Российская Федерация',
                sector='consumer',
                issue_size_plan=739000000,
                nominal=MoneyValue(currency='rub', units=0, nano=400000),
                trading_status=STS.SECURITY_TRADING_STATUS_NOT_AVAILABLE_FOR_TRADING,
                otc_flag=False,
                buy_available_flag=True,
                sell_available_flag=True,
                div_yield_flag=True,
                share_type=ShareType.SHARE_TYPE_COMMON,
                min_price_increment=Quotation(units=0, nano=20000000),
                api_trade_available_flag=True,
                uid='6e061639-6198-4448-9568-1eadb1b0e127',
                real_exchange=RealExchange.REAL_EXCHANGE_MOEX,
                position_uid='e07311a4-fac4-472b-b1d7-c3a7b3e56a6d',
                for_iis_flag=True,
                first_1min_candle_date=datetime.datetime(
                    2018, 3, 7, 18, 43, tzinfo=datetime.timezone.utc
                ),
                first_1day_candle_date=datetime.datetime(
                    2017, 2, 10, 7, 0, tzinfo=datetime.timezone.utc
                ),
            ),
            Share(
                figi='BBG000RMWQD4',
                ticker='ENPG',
                class_code='TQBR',
                isin='RU000A100K72',
                lot=1,
                currency='rub',
                klong=Quotation(units=2, nano=0),
                kshort=Quotation(units=2, nano=0),
                dlong=Quotation(units=0, nano=200000000),
                dshort=Quotation(units=0, nano=229900000),
                dlong_min=Quotation(units=0, nano=105600000),
                dshort_min=Quotation(units=0, nano=109000000),
                short_enabled_flag=False,
                name='En+ Group',
                exchange='MOEX_EVENING_WEEKEND',
                ipo_date=datetime.datetime(
                    2019, 6, 24, 0, 0, tzinfo=datetime.timezone.utc
                ),
                issue_size=638848896,
                country_of_risk='RU',
                country_of_risk_name='Российская Федерация',
                sector='materials',
                issue_size_plan=638848896,
                nominal=MoneyValue(currency='usd', units=0, nano=70000),
                trading_status=STS.SECURITY_TRADING_STATUS_NOT_AVAILABLE_FOR_TRADING,
                otc_flag=False,
                buy_available_flag=True,
                sell_available_flag=True,
                div_yield_flag=False,
                share_type=ShareType.SHARE_TYPE_COMMON,
                min_price_increment=Quotation(units=0, nano=500000000),
                api_trade_available_flag=True,
                uid='e2bd2eba-75de-4127-b39c-2f2dbe3866c3',
                real_exchange=RealExchange.REAL_EXCHANGE_MOEX,
                position_uid='62dae90c-238b-433d-ae4e-47c72b324bc7',
                for_iis_flag=True,
                first_1min_candle_date=datetime.datetime(
                    2020, 2, 20, 7, 34, tzinfo=datetime.timezone.utc
                ),
                first_1day_candle_date=datetime.datetime(
                    2020, 2, 20, 7, 0, tzinfo=datetime.timezone.utc
                ),
            ),
            Share(
                figi='BBG004PYF2N3',
                ticker='POLY',
                class_code='TQBR',
                isin='JE00B6T5S470',
                lot=1,
                currency='rub',
                klong=Quotation(units=2, nano=0),
                kshort=Quotation(units=2, nano=0),
                dlong=Quotation(units=0, nano=291500000),
                dshort=Quotation(units=0, nano=345600000),
                dlong_min=Quotation(units=0, nano=158300000),
                dshort_min=Quotation(units=0, nano=160000000),
                short_enabled_flag=True,
                name='Polymetal',
                exchange='MOEX_EVENING_WEEKEND',
                ipo_date=datetime.datetime(
                    2011, 10, 28, 0, 0, tzinfo=datetime.timezone.utc
                ),
                issue_size=473626239,
                country_of_risk='RU',
                country_of_risk_name='Российская Федерация',
                sector='materials',
                issue_size_plan=0,
                nominal=MoneyValue(currency='gbp', units=0, nano=0),
                trading_status=STS.SECURITY_TRADING_STATUS_NOT_AVAILABLE_FOR_TRADING,
                otc_flag=False,
                buy_available_flag=True,
                sell_available_flag=True,
                div_yield_flag=True,
                share_type=ShareType.SHARE_TYPE_COMMON,
                min_price_increment=Quotation(units=0, nano=100000000),
                api_trade_available_flag=True,
                uid='127361c2-32ec-448c-b3ec-602166f537ea',
                real_exchange=RealExchange.REAL_EXCHANGE_MOEX,
                position_uid='f869a0b6-e4cd-4e15-a25a-095c936f2e3f',
                for_iis_flag=True,
                first_1min_candle_date=datetime.datetime(
                    2018, 3, 7, 18, 34, tzinfo=datetime.timezone.utc
                ),
                first_1day_candle_date=datetime.datetime(
                    2013, 6, 20, 7, 0, tzinfo=datetime.timezone.utc
                ),
            ),
            Share(
                figi='BBG000GQSVC2',
                ticker='NKNCP',
                class_code='TQBR',
                isin='RU0006765096',
                lot=10,
                currency='rub',
                klong=Quotation(units=2, nano=0),
                kshort=Quotation(units=2, nano=0),
                dlong=Quotation(units=0, nano=500000000),
                dshort=Quotation(units=0, nano=199900000),
                dlong_min=Quotation(units=0, nano=292900000),
                dshort_min=Quotation(units=0, nano=95400000),
                short_enabled_flag=False,
                name='Нижнекамскнефтехим - акции привилегированные',
                exchange='MOEX',
                ipo_date=datetime.datetime(
                    2003, 8, 15, 0, 0, tzinfo=datetime.timezone.utc
                ),
                issue_size=218983750,
                country_of_risk='RU',
                country_of_risk_name='Российская Федерация',
                sector='materials',
                issue_size_plan=218983750,
                nominal=MoneyValue(currency='rub', units=1, nano=0),
                trading_status=STS.SECURITY_TRADING_STATUS_NOT_AVAILABLE_FOR_TRADING,
                otc_flag=False,
                buy_available_flag=True,
                sell_available_flag=True,
                div_yield_flag=True,
                share_type=ShareType.SHARE_TYPE_PREFERRED,
                min_price_increment=Quotation(units=0, nano=20000000),
                api_trade_available_flag=True,
                uid='bc21fb4f-8838-4355-8697-fb0d8fc809c8',
                real_exchange=RealExchange.REAL_EXCHANGE_MOEX,
                position_uid='7b7201cb-fe73-49a8-95d6-bd5edf4b849c',
                for_iis_flag=True,
                first_1min_candle_date=datetime.datetime(
                    2018, 3, 7, 19, 55, tzinfo=datetime.timezone.utc
                ),
                first_1day_candle_date=datetime.datetime(
                    2008, 4, 18, 0, 0, tzinfo=datetime.timezone.utc
                ),
            ),
            Share(
                figi='BBG000FWGSZ5',
                ticker='IRKT',
                class_code='TQBR',
                isin='RU0006752979',
                lot=100,
                currency='rub',
                klong=Quotation(units=2, nano=0),
                kshort=Quotation(units=2, nano=0),
                dlong=Quotation(units=0, nano=450000000),
                dshort=Quotation(units=0, nano=940000000),
                dlong_min=Quotation(units=0, nano=258400000),
                dshort_min=Quotation(units=0, nano=392800000),
                short_enabled_flag=False,
                name='Корпорация ИРКУТ',
                exchange='MOEX',
                ipo_date=datetime.datetime(
                    2002, 8, 15, 0, 0, tzinfo=datetime.timezone.utc
                ),
                issue_size=2085163865,
                country_of_risk='RU',
                country_of_risk_name='Российская Федерация',
                sector='industrials',
                issue_size_plan=791051875,
                nominal=MoneyValue(currency='rub', units=3, nano=0),
                trading_status=STS.SECURITY_TRADING_STATUS_NOT_AVAILABLE_FOR_TRADING,
                otc_flag=False,
                buy_available_flag=True,
                sell_available_flag=True,
                div_yield_flag=True,
                share_type=ShareType.SHARE_TYPE_COMMON,
                min_price_increment=Quotation(units=0, nano=20000000),
                api_trade_available_flag=True,
                uid='cfb50a23-2465-497e-bc7e-e4f0e042cf3d',
                real_exchange=RealExchange.REAL_EXCHANGE_MOEX,
                position_uid='1a583ddf-b4af-426b-890f-2749767a8379',
                for_iis_flag=True,
                first_1min_candle_date=datetime.datetime(
                    2018, 3, 7, 19, 42, tzinfo=datetime.timezone.utc
                ),
                first_1day_candle_date=datetime.datetime(
                    2004, 3, 9, 0, 0, tzinfo=datetime.timezone.utc
                ),
            ),
        ]
    )


@pytest.fixture
def sample_f_f_yielding_spread():
    return YieldingSpread(
        far_leg=FutureData(
            figi='FUTMGNT09230',
            ticker='MNU3',
            price=Decimal('4565.000000'),
            buy_margin=Decimal('1013.500000'),
            basic_asset_size=1,
            basic_asset='MGNT',
            expiration_date=datetime.datetime(
                2033, 3, 29, 21, 1, tzinfo=datetime.timezone.utc
            ),
            min_price_increment_amount=Decimal('1.00000000'),
            short_enabled=True,
            sell_margin=Decimal('1070.750000'),
        ),
        near_leg=FutureData(
            figi='FUTMGNT06230',
            ticker='MNM3',
            price=Decimal('4552.000000'),
            buy_margin=Decimal('967.0500000'),
            basic_asset_size=1,
            basic_asset='MGNT',
            expiration_date=datetime.datetime(
                2023, 6, 16, 0, 0, tzinfo=datetime.timezone.utc
            ),
            min_price_increment_amount=Decimal('1.00000000'),
            short_enabled=True,
            sell_margin=Decimal('998.1200000'),
        ),
        near_leg_type='F',
        far_to_near_ratio=1,
        margin=0,
        marginal_profit=0.0,
    )


@pytest.fixture
def sample_s_f_yielding_spread():
    return YieldingSpread(
        far_leg=FutureData(
            figi='FUTMGNT09230',
            ticker='MNU3',
            price=Decimal('4565.000000'),
            buy_margin=Decimal('1013.500000'),
            basic_asset_size=1,
            basic_asset='MGNT',
            expiration_date=datetime.datetime(
                2023, 9, 22, 0, 0, tzinfo=datetime.timezone.utc
            ),
            min_price_increment_amount=Decimal('1.00000000'),
            short_enabled=True,
            sell_margin=Decimal('1070.750000'),
        ),
        near_leg=StockData(
            figi='FUTMGNT06230',
            ticker='MAGN',
            price=Decimal('45.52000000'),
            buy_margin=Decimal('45.52000000'),
        ),
        near_leg_type='S',
        far_to_near_ratio=100,
        margin=0,
        marginal_profit=0.0,
    )


@pytest.fixture
def sample_yielding_spread():
    return YieldingSpread(
        far_leg=FutureData(
            figi='FUTMGNT09230',
            ticker='MNU3',
            price=Decimal('120000.000000'),
            buy_margin=Decimal('10000.000000'),
            basic_asset_size=1,
            basic_asset='MGNT',
            expiration_date=datetime.datetime.now(tz=datetime.timezone.utc)
            + datetime.timedelta(days=365),
            min_price_increment_amount=Decimal('1.00000000'),
            short_enabled=True,
            sell_margin=Decimal('20000.000000'),
        ),
        near_leg=StockData(
            figi='FUTMGNT06230',
            ticker='MAGN',
            price=Decimal('500.00000000'),
            buy_margin=Decimal('500.000000'),
        ),
        near_leg_type='S',
        far_to_near_ratio=100,
        margin=0,
        marginal_profit=0.0,
    )
