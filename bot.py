import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

import keys


logging.basicConfig( filename="bot.log", level=logging.INFO )


def hello(update, context):
    print("Вызван /start")
    update.message.reply_text("Hello Kity!")


def talk_with_user(update, context):
    text = update.message.text
    print(text)
    update.message.reply_text(text)


def main():
    updater = Updater(keys.API_KEY, use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", hello))
    dp.add_handler(MessageHandler(Filters.text, talk_with_user))

    logging.info("Bot started")
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()



