from datetime import datetime
from telegram.error import BadRequest

from db import db, get_subscribe


def send_updates(context):
    time_now = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
    print(time_now)
    for user in get_subscribe(db):
        try:
            context.bot.send_message(chat_id=user['chat_id'], text=f'Текущее время {time_now}')
        except BadRequest:
            print(f"ERROR: Chat id={user['chat_id']} not found")
