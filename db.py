from datetime import datetime
from emoji import emojize
from pymongo import MongoClient
from random import choice

import settings


client = MongoClient('localhost', 27017)

db = client.botdb


def create_or_get_user(db, effective_user, chat_id):
    user = db.users.find_one({"user_id": effective_user.id})
    if not user:
        user = {
            "user_id": effective_user.id,
            "first_name": effective_user.first_name,
            "last_name": effective_user.last_name,
            "username": effective_user.username,
            "chat_id": chat_id,
            "emoji": emojize(choice(settings.USER_EMOJI), use_aliases=True),
        }
        db.users.insert_one(user)
    return user


def save_questionnaire(db, user_id, questionnaire_data):
    user = db.users.find_one({"user_id": user_id})
    questionnaire_data["created"] = datetime.now()
    if not 'questionnaire' in user:
        db.users.update_one(
            {'_id': user['_id']},
            {'$set': {'questionnaire': [questionnaire_data]}}
        )
    else:
        db.users.update_one(
            {'_id': user['_id']},
            {'$push': {'questionnaire': questionnaire_data}}
        )
