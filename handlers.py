from emoji import emojize
from glob import glob
import os
from random import choice

from db import (db, create_or_get_user, subscribe_user, unsubscribe_user,
                save_cat_image_rating, user_rating, get_image_rating)
from job_queue import alarm
import settings
from utils import is_cat, random_number, main_keyboard, image_rating_inline_keyboard


def greet_user(update, context):
    user = create_or_get_user(db, update.effective_user, update.message.chat_id)
    print(update)
    print("Вызван /start")

    update.message.reply_text(
        f"Hello {user['first_name']} {user['emoji']}",
        reply_markup=main_keyboard()
    )


def talk_with_user(update, context):
    user = create_or_get_user(db, update.effective_user, update.message.chat_id)
    text = update.message.text
    print(text)
    update.message.reply_text(f"{text} {user['emoji']}", reply_markup=main_keyboard())


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


def send_cat_image(update, context):
    user = create_or_get_user(db, update.effective_user, update.message.chat_id)
    print("Вызван /cat")
    cat_images_list = glob('images/cat*.jp*g')
    cat_image_filename = choice(cat_images_list)

    chat_id = update.effective_chat.id
    if user_rating(db, cat_image_filename, user['user_id']):
        total_rating = get_image_rating(db, cat_image_filename)
        keyboard = None
        caption=f'CAT RATING: {total_rating}'
    else:
        keyboard = image_rating_inline_keyboard(cat_image_filename)
        caption = None
    context.bot.send_photo(
        chat_id=chat_id,
        photo=open(cat_image_filename, 'rb'),
        reply_markup=keyboard,
        caption=caption,
    )


def get_user_location(update, context):
    user = create_or_get_user(db, update.effective_user, update.message.chat_id)
    coordinates = update.message.location
    print(coordinates)
    update.message.reply_text(
        f"Ваши координаты {coordinates} {user['emoji']}!",
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


def subscribe(update, context):
    user = create_or_get_user(db, update.effective_user, update.message.chat_id)
    subscribe_user(db, user)
    update.message.reply_text("Вы подписались на рассылку")


def unsubscribe(update, context):
    user = create_or_get_user(db, update.effective_user, update.message.chat_id)
    unsubscribe_user(db, user)
    update.message.reply_text("Вы отписались от рассылки")


def sets_alarm(update, context):
    print(context.args)
    try:
        alarm_seconds = abs(int(context.args[0]))
        context.job_queue.run_once(alarm, alarm_seconds, context=update.message.chat.id)
        update.message.reply_text(f'Вы получите уведомление через {alarm_seconds} секунд')
    except (ValueError, TypeError):
        update.message.reply_text("Введите количество секунд после команды /alarm")


def cat_image_rating(update, context):
    update.callback_query.answer()
    callback_type, image_name, rating = update.callback_query.data.split("|")
    rating = int(rating)
    user = create_or_get_user(db, update.effective_user, update.effective_chat.id)
    save_cat_image_rating(db, user, image_name, rating)
    total_rating = get_image_rating(db, image_name)
    update.callback_query.edit_message_caption(caption=f'CAT RATING: {total_rating}')
