import logging
import os
import time

import requests
from dotenv import load_dotenv
from requests.models import HTTPError
from telegram import Bot

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s'
)


PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
API = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
bot = Bot(token=TELEGRAM_TOKEN)
time_constant1 = 300
time_constant2 = 15


def parse_homework_status(homework):
    status = homework.get('status')
    homework_name = homework.get('homework_name')
    if status == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    elif status == 'approved':
        verdict = ('Ревьюеру всё понравилось, '
                   'можно приступать к следующему уроку.')
    else:
        verdict = 'работа взята в ревью'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_date):
    headers = {'Authorization': f'OAuth {TELEGRAM_TOKEN}'}
    params = {'from_date': current_date}
    try:
        homework_statuses = requests.get(API, headers=headers, params=params)
    except requests.ConnectionError as error:
        logging.error(error)

    try:
        return homework_statuses.json()
    except HTTPError:
        logging.error("Невалидный JSON")


def send_message(message, bot_client):
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())  # начальное значение timestamp

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(
                    new_homework.get('homeworks')[0])
                )
            current_timestamp = new_homework.get('current_date',
                                                 current_timestamp)
            time.sleep(time_constant1)  # опрашивать раз в пять минут

        except Exception as e:
            logging.error(f'Бот столкнулся с ошибкой: {e}')
            time.sleep(time_constant2)


if __name__ == '__main__':
    main()
