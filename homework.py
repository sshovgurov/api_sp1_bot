import os
import time
import logging
import requests
from dotenv import load_dotenv
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


def parse_homework_status(homework):
    status = homework.get('status')
    homework_name = homework.get('homework_name')
    if status == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    else:
        verdict = ('Ревьюеру всё понравилось, '
                   'можно приступать к следующему уроку.')
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_date):
    headers = {'Authorization': f'OAuth {TELEGRAM_TOKEN}'}
    params = {'from_date': current_date}
    homework_statuses = requests.get(API, headers=headers, params=params)
    return homework_statuses.json()


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
            time.sleep(300)  # опрашивать раз в пять минут

        except Exception as e:
            print(f'Бот столкнулся с ошибкой: {e}')
            time.sleep(5)


if __name__ == '__main__':
    main()
