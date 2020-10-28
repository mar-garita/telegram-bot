from telegram import ReplyKeyboardRemove, ReplyKeyboardMarkup


def questionnaire_start(update, context):
    update.message.reply_text(
        "Введите ваше имя",
        reply_markup=ReplyKeyboardRemove()
    )
    return "name"


def questionnaire_name(update, context):
    user_name = update.message.text
    if len(user_name.split()) < 2:
        update.message.reply_text("Ведите ваше имя и фамилию")
        return "name"
    else:
        context.user_data["questionnaire"] = {"name": user_name}
        reply_keyboard = [["1", "2", "3", "4", "5"]]
        update.message.reply_text(
            "Оцените бота по шкале от 1 до 5",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        )
        return "rating"


def questionnaire_rating(update, context):
    context.user_data["questionnaire"]["rating"] = int(update.message.text)
    update.message.reply_text(
        "Оставьте комментарий или пропустите этот шаг, введя /skip"
    )
    return "comment"
