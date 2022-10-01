import os

from dotenv import load_dotenv
from tinkoff.invest.retrying.settings import RetryClientSettings

# place stops and shorts

LONG_LEVELS = (15, 20, 25)
SHORT_LEVELS = (20, 25, 30)
STOPS_SUM = 300000
ORDER_TTL = 120

# tinkoff settings

RETRY_SETTINGS = RetryClientSettings(use_retry=True, max_retry_attempt=100)

load_dotenv()
TCS_RO_TOKEN = os.getenv('TCS_RO_TOKEN')
TCS_RW_TOKEN = os.getenv('TCS_RW_TOKEN')
TCS_ACCOUNT_ID = os.getenv('ACCOUNT_ID')
TELEGRAM_TOKEN = os.getenv('TG_TOKEN')
TELEGRAM_CHAT_ID = int(os.getenv('TG_CHAT_ID'))

# endpoints

ENDPOINT_HOST = 'http://192.168.2.40:8000'
STOPS_ENDPOINT = '/api/v1/stops/'
SHORTS_ENDPOINT = '/api/v1/shorts/'
