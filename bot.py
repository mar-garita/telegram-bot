from emoji import emojize
from glob import glob
import logging
from random import choice, randint
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

import keys
import settings


logging.basicConfig(filename="bot.log", level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d '
                                                                                                        '%H:%M:%S')


def greet_user(update, context):
    print(update)
    print("Вызван /start")
    context.user_data['emoji'] = get_emoji(context.user_data)
    update.message.reply_text(f"Hello User {context.user_data['emoji']}")


def talk_with_user(update, context):
    context.user_data['emoji'] = get_emoji(context.user_data)
    text = update.message.text
    print(text)
    update.message.reply_text(f"{text} {context.user_data['emoji']}")


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
    update.message.reply_text(message)


def send_cat_picture(update, context):
    print("Вызван /cat")
    cat_images_list = glob('images/cat*.jp*g')
    cat_image = choice(cat_images_list)

    chat_id = update.effective_chat.id
    context.bot.send_photo(chat_id=chat_id, photo=open(cat_image, 'rb'))


def main():
    updater = Updater(keys.API_KEY, use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", greet_user))
    dp.add_handler(CommandHandler("play", play_number))
    dp.add_handler(CommandHandler( "cat", send_cat_picture))
    dp.add_handler(MessageHandler(Filters.text, talk_with_user))

    logging.info("Bot started")
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()



