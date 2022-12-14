import os
import zoneinfo
from datetime import timedelta, time, datetime
from dotenv import load_dotenv
from tinkoff.invest.retrying.settings import RetryClientSettings

# messing with working hours time
PAUSE_BETWEEN_UPDATES = 60

WORK_DAYS = (0, 4)
WORK_HOURS = {
    'morning': (time(10, 00), time(14, 00)),
    'day': (time(14, 5), time(18, 39, 59)),
    'evening': (time(19, 5), time(23, 40)),
}
TIME_OFFSET = timedelta(seconds=30)
ZONE = zoneinfo.ZoneInfo('Europe/Moscow')

OFFSET_ADJUSTED_WORK_HOURS = {
    key: (
        (
                datetime.combine(datetime.now(ZONE).date(), value[0]) + TIME_OFFSET
        ).time(),
        (
                datetime.combine(datetime.now(ZONE).date(), value[1]) - TIME_OFFSET
        ).time(),
    )
    for key, value in WORK_HOURS.items()
}

# place stops and shorts

LONG_LEVELS = ('15', '20', '25')
SHORT_LEVELS = ('20', '25', '30')
STOPS_SUM = 300000
ORDER_TTL = 120

# tinkoff settings
SLEEP_PAUSE = 1
RETRY_SETTINGS = RetryClientSettings(use_retry=True, max_retry_attempt=100)

load_dotenv()
TCS_RO_TOKEN = os.getenv('TCS_RO_TOKEN')
TCS_RW_TOKEN = os.getenv('TCS_RW_TOKEN')
TCS_ACCOUNT_ID = os.getenv('ACCOUNT_ID')
TELEGRAM_TOKEN = os.getenv('TG_TOKEN')
TELEGRAM_CHAT_ID = int(os.getenv('TG_CHAT_ID'))

# endpoints

ENDPOINT_HOST = 'http://192.168.2.180:8000/'

ENDPOINTS = {
    'shorts': 'api/v1/shorts/',
    'stops': 'api/v1/stops/',
    'restore_stops': 'api/v1/restorestops/',
    'spreads': 'api/v1/spreads/',
    'sellbuy': 'api/v1/sellbuy/',
    'health': 'api/v1/health/'
}


if __name__ == '__main__':
    print(OFFSET_ADJUSTED_WORK_HOURS)
