from clarifai.rest import ClarifaiApp
from emoji import emojize
from random import randint
from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

import keys
import settings


def random_number(user_number):
    """
    The function generates a random number, compares it with the user's number, and gives the answer
    :param user_number: the number entered by the user
    :return: whose number is greater
    """
    bot_number = randint(user_number - 10, user_number + 10)

    if bot_number > user_number:
        message = f"Ваше число {user_number}, число бота {bot_number}. Бот выиграл!"
    elif bot_number < user_number:
        message = f"Ваше число {user_number}, число бота {bot_number}. Вы выиграли!"
    else:
        message = f"Ваше число {user_number}, число бота {bot_number}. Ничья!"
    return message


def main_keyboard():
    return ReplyKeyboardMarkup([
        ['Прислать котика', KeyboardButton('Отправить мои координаты', request_location=True), 'Заполнить анкету']
    ])


def is_cat(file_name):
    """
    Sends data to https://www.clarifai.com/ and receives a response. True - if the photo has a cat, False - if not.
    :param file_name:
    :return:
    """
    app = ClarifaiApp(api_key=keys.CLARIFAI_API_KEY)
    # public_models.general_model - this is the basic model for recognizing objects in the photo
    model = app.public_models.general_model
    # response from clarifai:
    response = model.predict_by_filename(file_name, max_concepts=5)
    if response['status']['code'] == 10000:
        # 'concepts' - this is a list of five dictionaries
        for concept in response['outputs'][0]['data']['concepts']:
            # If the 'name' key value is 'cat' in at least one of the five dictionaries, return True:
            if concept['name'] == 'cat':
                return True
    return False


def image_rating_inline_keyboard(image_name):
    """
    Creates a keyboard for a vote under the photo (👍 and 👎)
    """
    callback_text = f'rating|{image_name}|'  # file name
    emoji_like = emojize(settings.EMOJI_LIKE, use_aliases=True)
    emoji_dislike = emojize(settings.EMOJI_DISLIKE, use_aliases=True)
    keyboard = [
        [
            InlineKeyboardButton(emoji_like, callback_data=callback_text + '1'),
            InlineKeyboardButton(emoji_dislike, callback_data=callback_text + '-1')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


if __name__ == "__main__":
    print(is_cat("images/cat1.jpg"))
    print(is_cat("images/no_cat.jpg"))
