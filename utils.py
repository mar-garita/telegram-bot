from clarifai.rest import ClarifaiApp
from emoji import emojize
from random import choice, randint
from telegram import ReplyKeyboardMarkup, KeyboardButton

import keys
import settings


def get_emoji(user_data):
    if 'emoji' not in user_data:
        emoji_smile = choice(settings.USER_EMOJI)
        emoji_smile = emojize(emoji_smile, use_aliases=True)
        return emoji_smile
    return user_data['emoji']


def random_number(user_number):
    bot_number = randint(user_number - 10, user_number + 10)

    if bot_number > user_number:
        message = f"Ваше число {user_number}, число бота {bot_number}. Бот выиграл!"
    elif bot_number < user_number:
        message = f"Ваше число {user_number}, число бота {bot_number}. Вы выиграли!"
    else:
        message = f"Ваше число {user_number}, число бота {bot_number}. Ничья!"
    return message


def main_keyboard():
    return ReplyKeyboardMarkup([['Прислать котика', KeyboardButton('Отправить мои координаты', request_location=True)]])


def is_cat(file_name):
    app = ClarifaiApp(api_key=keys.CLARIFAI_API_KEY)
    model = app.public_models.general_model
    response = model.predict_by_filename(file_name, max_concepts=5)
    if response['status']['code'] == 10000:
        for concept in response['outputs'][0]['data']['concepts']:
            if concept['name'] == 'cat':
                return True
    return False


if __name__ == "__main__":
    print(is_cat("images/cat1.jpg"))
    print(is_cat("images/no_cat.jpg"))
