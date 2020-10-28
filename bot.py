import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler


from handlers import (greet_user, play_number, send_cat_picture, get_user_location,
                      talk_with_user, check_user_image)
from questionnaire import questionnaire_start, questionnaire_name, questionnaire_rating
import keys


logging.basicConfig(filename="bot.log", level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d '
                                                                                                        '%H:%M:%S')


def main():
    updater = Updater(keys.API_KEY, use_context=True)

    dp = updater.dispatcher

    questionnaire = ConversationHandler(
        entry_points=[
            MessageHandler(Filters.regex('^(Заполнить анкету)$'), questionnaire_start)
        ],
        states={
            "name": [MessageHandler(Filters.text, questionnaire_name)],
            "rating": [MessageHandler(Filters.regex('^(1|2|3|4|5)$'), questionnaire_rating)],
        },
        fallbacks=[]
    )
    dp.add_handler(questionnaire)

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
