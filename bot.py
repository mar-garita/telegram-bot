import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler


from handlers import (greet_user, play_number, send_cat_picture, get_user_location,
                      talk_with_user, check_user_image, subscribe, unsubscribe)
from job_queue import send_updates
from questionnaire import (questionnaire_start, questionnaire_name, questionnaire_rating, questionnaire_skip,
                           questionnaire_comment, questionnaire_dontknow)
import keys


logging.basicConfig(filename="bot.log", level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d '
                                                                                                        '%H:%M:%S')


def main():
    updater = Updater(keys.API_KEY, use_context=True)

    jq = updater.job_queue
    jq.run_repeating(send_updates, interval=10, first=0)

    dp = updater.dispatcher

    questionnaire = ConversationHandler(
        entry_points=[
            MessageHandler(Filters.regex('^(Заполнить анкету)$'), questionnaire_start)
        ],
        states={
            "name": [MessageHandler(Filters.text, questionnaire_name)],
            "rating": [MessageHandler(Filters.regex('^(1|2|3|4|5)$'), questionnaire_rating)],
            "comment": [
                CommandHandler("skip", questionnaire_skip),
                MessageHandler(Filters.text, questionnaire_comment)
            ],
        },
        fallbacks=[
            MessageHandler(
                Filters.text | Filters.video | Filters.photo | Filters.document | Filters.location,
                questionnaire_dontknow)
        ]
    )
    dp.add_handler(questionnaire)

    dp.add_handler(CommandHandler("start", greet_user))
    dp.add_handler(CommandHandler("play", play_number))
    dp.add_handler(CommandHandler("subscribe", subscribe))
    dp.add_handler(CommandHandler("unsubscribe", unsubscribe))
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
