import os

from dotenv import load_dotenv
from tinkoff.invest.retrying.settings import RetryClientSettings

CURRENT_INTEREST_RATE = '16'

# place stops and shorts

LONG_LEVELS = ('15', '20', '25')
SHORT_LEVELS = ('20', '25', '30')
STOPS_SUM = 300000
ORDER_TTL = 120

# Art Cashin's formula

NUKE_LEVELS = ('0', '1', '5', '7')

# Dividend scanner for futures

MAX_FUTURES_AHEAD = 3
PERCENT_THRESHOLD = 1

# tinkoff settings
SLEEP_PAUSE = 1
RETRY_SETTINGS = RetryClientSettings(use_retry=True, max_retry_attempt=100)

load_dotenv()
TCS_RO_TOKEN = os.getenv('TCS_RO_TOKEN', '000')
TCS_RW_TOKEN = os.getenv('TCS_RW_TOKEN', '000')
TCS_ACCOUNT_ID = os.getenv('ACCOUNT_ID', '000')
TELEGRAM_TOKEN = os.getenv(
    'TG_TOKEN', '123456789:AABBCCDDEEFFaabbccddeeff-1234567890'
)
TELEGRAM_CHAT_ID = int(os.getenv('TG_CHAT_ID', '000'))

# endpoints

ENDPOINT_HOST = os.getenv('BASE_HOST', 'http://127.0.0.1:8000/')

ENDPOINTS = {
    'shorts': 'api/v1/shorts/',
    'stops': 'api/v1/stops/',
    'stop_orders': 'api/v1/stop_orders/',
    'spreads': 'api/v1/spreads/',
    'sellbuy': 'api/v1/sellbuy/',
    'health': 'api/v1/health/',
    'ticker': 'api/v1/ticker/',
}
