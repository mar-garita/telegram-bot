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
    """
    The function sends a greeting to the user. Pre-checks whether the user exists in the database or not.
    :param update: Information that came from the telegram platform.
    :param context: Input from the user. Always a string.
    """
    user = create_or_get_user(db, update.effective_user, update.message.chat_id)
    print(update)
    print("Вызван /start")

    update.message.reply_text(
        f"Hello {user['first_name']} {user['emoji']}",
        reply_markup=main_keyboard()
    )


def talk_with_user(update, context):
    """Sends a message to the user that it received from the user"""
    user = create_or_get_user(db, update.effective_user, update.message.chat_id)
    text = update.message.text
    print(text)
    update.message.reply_text(f"{text} {user['emoji']}", reply_markup=main_keyboard())


def play_number(update, context):
    """
    The numbers game. First, the user enters a number, then the bot selects a random number.
    Checks whose number is higher, and he won.
    Для старта игры пользователь вводит "/play number"
    """
    user = create_or_get_user(db, update.effective_user, update.message.chat_id)
    print(context.args)

    if context.args:
        try:
            user_input = int(context.args[0])
            # Called function random_number()
            message = random_number(user_input)
        except (ValueError, TypeError):
            message = "Некорректный ввод! Введите число!"
    else:
        message = "Введите '/play + число'"
    update.message.reply_text(message, reply_markup=main_keyboard())


def send_cat_image(update, context):
    """
    The function sends the user a randomly selected picture with a cat. If the user voted for this image,
    the rating of votes is displayed under the photo. If the user did not vote for this image, displays
    the inline-keyboard for voting.
    """
    user = create_or_get_user(db, update.effective_user, update.message.chat_id)
    print("Вызван /cat")
    cat_images_list = glob('images/cat*.jp*g')
    cat_image_filename = choice(cat_images_list)

    chat_id = update.effective_chat.id
    if user_rating(db, cat_image_filename, user['user_id']):
        total_rating = get_image_rating(db, cat_image_filename)
        keyboard = None
        emoji_heart = emojize(settings.EMOJI_HEART, use_aliases=True)
        caption = f'{emoji_heart} {total_rating}'
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
    """
    Gets the user's coordinates.
    """
    user = create_or_get_user(db, update.effective_user, update.message.chat_id)
    coordinates = update.message.location
    print(coordinates)
    update.message.reply_text(
        f"Ваши координаты {coordinates} {user['emoji']}!",
        reply_markup=main_keyboard()
    )


def check_user_image(update, context):
    """
    The function receives an image from the user and checks whether there is a cat on it
    """
    user = create_or_get_user(db, update.effective_user, update.message.chat_id)
    update.message.reply_text("Фото обрабатывается")
    # creating a folder named "downloads" for images
    os.makedirs("downloads", exist_ok=True,)
    user_image = context.bot.getFile(update.message.photo[-1].file_id)
    # creating a file name
    file_name = os.path.join("downloads", f"{user_image.file_id}.jpg")
    # saving an image
    user_image.download(file_name)

    # if there is a cat in the photo:
    if is_cat(file_name):
        emoji = emojize(settings.RESPONCE_EMOJI[1], use_aliases=True)
        update.message.reply_text(f"На фото обнаружен котик, добавляю в библиотеку {emoji}")
        # moving the image to the images folder
        new_file_name = os.path.join("images", f"cat_{user_image.file_id}.jpg")
        os.rename(file_name, new_file_name)

    else:
        emoji = emojize(settings.RESPONCE_EMOJI[0], use_aliases=True)
        update.message.reply_text(f"Котик на фото не обнаружен {emoji}")
        # if the cat in the photo is not found, then delete this file from the 'downloads' folder:
        os.remove(file_name)


def subscribe(update, context):
    """
    The function subscribes the user to a newsletter from the bot.
    """
    user = create_or_get_user(db, update.effective_user, update.message.chat_id)
    subscribe_user(db, user)
    update.message.reply_text("Вы подписались на рассылку")


def unsubscribe(update, context):
    """
    the function unsubscribes the user to the newsletter from the bot.
    """
    user = create_or_get_user(db, update.effective_user, update.message.chat_id)
    unsubscribe_user(db, user)
    update.message.reply_text("Вы отписались от рассылки")


def sets_alarm(update, context):
    """
    Sends a message to the user after a specified number of seconds.
    """
    # print(context.args)
    try:
        alarm_seconds = abs(int(context.args[0]))  # number of seconds
        # running a task once:
        context.job_queue.run_once(alarm, alarm_seconds, context=update.message.chat.id)
        update.message.reply_text(f'Вы получите уведомление через {alarm_seconds} секунд')
    except (ValueError, TypeError):
        update.message.reply_text("Введите количество секунд после команды /alarm")


def cat_image_rating(update, context):
    # confirmation of receiving data from the inline-keyboard
    update.callback_query.answer()
    # data is a string (example: rating|images/cat2.jpg|1),
    # splitting a string by separator ("|") results in a list of three elements
    callback_type, image_name, rating = update.callback_query.data.split("|")
    rating = int(rating)
    user = create_or_get_user(db, update.effective_user, update.effective_chat.id)
    save_cat_image_rating(db, user, image_name, rating)
    total_rating = get_image_rating(db, image_name)
    emoji_heart = emojize(settings.EMOJI_HEART, use_aliases=True)
    # image caption:
    update.callback_query.edit_message_caption(caption=f'{emoji_heart} {total_rating}')
