import logging
import os
import time

import requests
import json
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s'
)
logger = logging.getLogger(__name__)


PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
API = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
bot = Bot(token=TELEGRAM_TOKEN)
SLEEP_TIME1 = 300
SLEEP_TIME2 = 15


def parse_homework_status(homework):
    status = homework.get('status')
    homework_name = homework.get('homework_name')
    if homework_name is None or status is None:
        logger.warning('Проблема с запросом API')
        return 'Проблема с запросом API'
    elif status == 'rejected':
        verdict = 'К сожалению, в работе нашлись ошибки.'
    elif status == 'approved':
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_date):
    headers = {'Authorization': f'OAuth {TELEGRAM_TOKEN}'}
    if current_date is None:
        current_date = int(time.time())
    params = {'from_date': current_date}
    try:
        homework_statuses = requests.get(API, headers=headers, params=params)
    except requests.RequestException as error:
        logging.error(error)
        raise Exception('Бот столкнулся с ошибкой')
    try:
        return homework_statuses.json()
    except json.JSONDecodeError:
        logging.error("Невалидный JSON")


def send_message(message):
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())  # начальное значение timestamp
    logger.info("starting")
    while True:
        try:
            new_homework = get_homeworks(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(
                    new_homework.get('homeworks')[0])
                )
            current_timestamp = new_homework.get('current_date',
                                                 current_timestamp)
            time.sleep(SLEEP_TIME1)  # опрашивать раз в пять минут

        except Exception as e:
            logging.error(f'Бот столкнулся с ошибкой: {e}')
            send_message(f'Бот столкнулся с ошибкой: {e}')
            time.sleep(SLEEP_TIME2)


if __name__ == '__main__':
    main()
