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
    if 'questionnaire' not in user:
        db.users.update_one(
            {'_id': user['_id']},
            {'$set': {'questionnaire': [questionnaire_data]}}
        )
    else:
        db.users.update_one(
            {'_id': user['_id']},
            {'$push': {'questionnaire': questionnaire_data}}
        )


def subscribe_user(db, user_data):
    if not user_data.get('subscribe'):
        db.users.update_one(
            {'_id': user_data['_id']},
            {'$set': {'subscribe': True}}
        )


def unsubscribe_user(db, user_data):
    db.users.update_one(
        {'_id': user_data['_id']},
        {'$set': {'subscribe': False}}
    )


def get_subscribe(db):
    return db.users.find({"subscribe": True})


def save_cat_image_rating(db, user_data, image_name, rating):
    image = db.images.find_one({"image_name": image_name})
    if not image:
        image = {
            "image_name": image_name,
            "ratings": [{"user_id": user_data["user_id"], "rating": rating}]
        }
        db.images.insert_one(image)
    elif not user_rating(db, image_name, user_data["user_id"]):
        db.images.update_one(
            {"image_name": image_name},
            {"$push": {"ratings": {"user_id": user_data["user_id"], "rating": rating}}}
        )


def user_rating(db, image_name, user_id):
    if db.images.find_one({"image_name": image_name, "ratings.user_id": user_id}):
        return True
    return False


def get_image_rating(db, image_name):
    result = db.images.aggregate([
        {
            '$match': {
                'image_name': image_name
            }
        }, {
            '$unwind': {
                'path': '$ratings'
            }
        }, {
            '$group': {
                '_id': '$image_name',
                'total_rating': {
                    '$sum': '$ratings.rating'
                }
            }
        }
    ])
    total_rating = next(result, None)
    if total_rating:
        return total_rating['total_rating']
    return 0
