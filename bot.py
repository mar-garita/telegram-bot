from datetime import time
import logging
import pytz

from telegram.bot import Bot
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)
from telegram.ext import messagequeue as mq
from telegram.ext.jobqueue import Days
from telegram.utils.request import Request

from handlers import (greet_user, play_number, send_cat_image, get_user_location, talk_with_user,
                      check_user_image, subscribe, unsubscribe, sets_alarm, cat_image_rating)
from job_queue import send_updates
from questionnaire import (questionnaire_start, questionnaire_name, questionnaire_rating,
                           questionnaire_skip, questionnaire_comment, questionnaire_dontknow)
import keys


logging.basicConfig(filename="bot.log", level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d '
                                                                                                        '%H:%M:%S')


class MQBot(Bot):
    def __init__(self, *args, is_queued_def=True, msg_queue=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._is_messages_queued_default = is_queued_def
        self._msg_queue = msg_queue or mq.MessageQueue()

    def __del__(self):
        try:
            self._msg_queue.stop()
        except:
            pass

    @mq.queuedmessage
    def send_message(self, *args, **kwargs):
        return super().send_message(*args, **kwargs)


def main():
    request = Request(
        con_pool_size=8,
    )
    bot = MQBot(keys.API_KEY, request=request)
    updater = Updater(bot=bot)

    jq = updater.job_queue
    target_time = time(23, 53, tzinfo=pytz.timezone('Asia/Tel_Aviv'))
    target_day = (Days.TUE, Days.THU, Days.SAT)
    jq.run_daily(send_updates, target_time, target_day)

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
    dp.add_handler(CommandHandler("cat", send_cat_image))
    dp.add_handler(CommandHandler( "alarm", sets_alarm))
    dp.add_handler(CallbackQueryHandler(cat_image_rating, pattern="^(rating|)"))
    dp.add_handler(MessageHandler(Filters.regex('^(Прислать котика)$'), send_cat_image))
    dp.add_handler(MessageHandler(Filters.location, get_user_location))
    dp.add_handler(MessageHandler(Filters.photo, check_user_image))
    dp.add_handler(MessageHandler(Filters.text, talk_with_user))

    logging.info("Bot started")
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
