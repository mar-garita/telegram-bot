import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


from handlers import (greet_user, play_number, send_cat_picture, get_user_location,
                      talk_with_user, check_user_image)
import keys


logging.basicConfig(filename="bot.log", level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d '
                                                                                                        '%H:%M:%S')


def main():
    updater = Updater(keys.API_KEY, use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", greet_user))
    dp.add_handler(CommandHandler("play", play_number))
    dp.add_handler(CommandHandler("cat", send_cat_picture))
    dp.add_handler(MessageHandler(Filters.regex('^(Прислать котика)$'), send_cat_picture))
    dp.add_handler(MessageHandler(Filters.location, get_user_location))
    dp.add_handler(MessageHandler(Filters.photo, check_user_image))
    dp.add_handler(MessageHandler(Filters.text, talk_with_user))

    logging.info("Bot started")
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
