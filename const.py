import asyncio

LOOP = asyncio.get_event_loop()

APP_NAME = 'base_loader/1.0'
EMAIL = 'belikov.demayn3011@gmail.com'

BASE_URL = 'https://dev-100-api.huntflow.dev'
BASE_HEADERS = {
    'User-Agent': f'{APP_NAME} ({EMAIL})',
    'Host': 'dev-100-api.huntflow.dev',
    'Accept': '*/*',
    'Authorization': 'Bearer ',
}
GOOD_STATUSES = {
    200,
    201,
}

XLSX_FILE_EXTEND = '.xlsx'
WRITE = 'write'

STEP = 2

LOG_FILE = 'report.log'

CONTENT_TYPES = {
    'doc': 'application/msword',
    'pdf': 'application/pdf',
}
