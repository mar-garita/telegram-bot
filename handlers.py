from emoji import emojize
from glob import glob
import os
from random import choice

from db import db, create_or_get_user
import settings
from utils import get_emoji, is_cat, random_number, main_keyboard


def greet_user(update, context):
    user = create_or_get_user(db, update.effective_user, update.message.chat_id)
    print(update)
    print("Вызван /start")
    context.user_data['emoji'] = get_emoji(context.user_data)

    update.message.reply_text(
        f"Hello User {context.user_data['emoji']}",
        reply_markup=main_keyboard()
    )


def talk_with_user(update, context):
    user = create_or_get_user(db, update.effective_user, update.message.chat_id)
    context.user_data['emoji'] = get_emoji(context.user_data)
    text = update.message.text
    print(text)
    update.message.reply_text(f"{text} {context.user_data['emoji']}", reply_markup=main_keyboard())


def play_number(update, context):
    user = create_or_get_user(db, update.effective_user, update.message.chat_id)
    print(context.args)

    if context.args:
        try:
            user_input = int(context.args[0])
            message = random_number(user_input)
        except (ValueError, TypeError):
            message = "Некорректный ввод! Введите число!"
    else:
        message = "Введите '/play + число'"
    update.message.reply_text(message, reply_markup=main_keyboard())


def send_cat_picture(update, context):
    user = create_or_get_user(db, update.effective_user, update.message.chat_id)
    print("Вызван /cat")
    cat_images_list = glob('images/cat*.jp*g')
    cat_image = choice(cat_images_list)

    chat_id = update.effective_chat.id
    context.bot.send_photo(chat_id=chat_id, photo=open(cat_image, 'rb'), reply_markup=main_keyboard())


def get_user_location(update, context):
    user = create_or_get_user(db, update.effective_user, update.message.chat_id)
    context.user_data['emoji'] = get_emoji(context.user_data)
    coordinates = update.message.location
    print(coordinates)
    update.message.reply_text(
        f"Ваши координаты {coordinates} {context.user_data['emoji']}!",
        reply_markup=main_keyboard()
    )


def check_user_image(update, context):
    user = create_or_get_user(db, update.effective_user, update.message.chat_id)
    update.message.reply_text("Фото обрабатывается")
    os.makedirs("downloads", exist_ok=True,)
    user_image = context.bot.getFile(update.message.photo[-1].file_id)
    file_name = os.path.join("downloads", f"{user_image.file_id}.jpg")
    user_image.download(file_name)

    if is_cat(file_name):
        emoji = emojize(settings.RESPONCE_EMOJI[1], use_aliases=True)
        update.message.reply_text(f"На фото обнаружен котик, добавляю в библиотеку {emoji}")
        new_file_name = os.path.join("images", f"cat_{user_image.file_id}.jpg")
        os.rename(file_name, new_file_name)

    else:
        emoji = emojize(settings.RESPONCE_EMOJI[0], use_aliases=True)
        update.message.reply_text(f"Котик на фото не обнаружен {emoji}")
        os.remove(file_name)
