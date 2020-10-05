import logging
from random import randint

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

import keys


logging.basicConfig(filename="bot.log", level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d '
                                                                                                        '%H:%M:%S')


def greet_user(update, context):
    print(update)
    print("Вызван /start")
    update.message.reply_text("Hello User!")


def talk_with_user(update, context):
    text = update.message.text
    print(text)
    update.message.reply_text(text)


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


def main():
    updater = Updater(keys.API_KEY, use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", greet_user))
    dp.add_handler(CommandHandler("play", play_number))
    dp.add_handler(MessageHandler(Filters.text, talk_with_user))

    logging.info("Bot started")
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()



