from glob import glob
from random import choice

from utils import get_emoji, random_number, main_keyboard


def greet_user(update, context):
    print(update)
    print("Вызван /start")
    context.user_data['emoji'] = get_emoji(context.user_data)

    update.message.reply_text(
        f"Hello User {context.user_data['emoji']}",
        reply_markup=main_keyboard()
    )


def talk_with_user(update, context):
    context.user_data['emoji'] = get_emoji(context.user_data)
    text = update.message.text
    print(text)
    update.message.reply_text(f"{text} {context.user_data['emoji']}", reply_markup=main_keyboard())


def play_number(update, context):
    print(context.args)

    if context.args:
        try:
            user_input = int(context.args[0])
            message = random_number(user_input)
        except (ValueError, TypeError):
            message = "Некорректный ввод! Введите число!"
    else:
        message = "Введите число"
    update.message.reply_text(message, reply_markup=main_keyboard())


def send_cat_picture(update, context):
    print("Вызван /cat")
    cat_images_list = glob('images/cat*.jp*g')
    cat_image = choice(cat_images_list)

    chat_id = update.effective_chat.id
    context.bot.send_photo(chat_id=chat_id, photo=open(cat_image, 'rb'), reply_markup=main_keyboard())


def get_user_location(update, context):
    context.user_data['emoji'] = get_emoji(context.user_data)
    coordinates = update.message.location
    print(coordinates)
    update.message.reply_text(
        f"Ваши координаты {coordinates} {context.user_data['emoji']}!",
        reply_markup=main_keyboard()
    )
