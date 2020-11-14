from datetime import datetime
from emoji import emojize
from pymongo import MongoClient
from random import choice

import settings


# connecting to the database MongoDB
client = MongoClient('localhost', 27017)
# selecting a database to save data
db = client.botdb


def create_or_get_user(db, effective_user, chat_id):
    """
    The function checks whether the user exists in the database. if not, it adds it.
    :param db:
    :param effective_user: Data about the current user sent by telegram.
    :param chat_id:
    :return:
    """
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
        db.users.insert_one(user)  # insert a document in the collection "users"
    return user


def save_questionnaire(db, user_id, questionnaire_data):
    """
    Saves the user's questionnaire every time they fill it out.
    """
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
    """Saves the subscription status"""
    if not user_data.get('subscribe'):
        db.users.update_one(
            {'_id': user_data['_id']},
            {'$set': {'subscribe': True}}
        )


def unsubscribe_user(db, user_data):
    """Deletes the subscription status"""
    db.users.update_one(
        {'_id': user_data['_id']},
        {'$set': {'subscribe': False}}
    )


def get_subscribe(db):
    """Retrieves all users whose "subscribe" status is set to True from the database"""
    return db.users.find({"subscribe": True})


def save_cat_image_rating(db, user_data, image_name, rating):
    """
    Saves the user's vote in the database.
    """
    image = db.images.find_one({"image_name": image_name})
    # if the image is not in the database, it means that it has no votes:
    if not image:
        image = {
            "image_name": image_name,
            "ratings": [{"user_id": user_data["user_id"], "rating": rating}]
        }
        # saving images and voting images
        db.images.insert_one(image)
    # if the user didn't vote:
    elif not user_rating(db, image_name, user_data["user_id"]):
        # add a user's vote
        db.images.update_one(
            {"image_name": image_name},
            {"$push": {"ratings": {"user_id": user_data["user_id"], "rating": rating}}}
        )


def user_rating(db, image_name, user_id):
    """
    Checks whether the user voted for this image, and if they voted, it returns True, if not - False
    """
    if db.images.find_one({"image_name": image_name, "ratings.user_id": user_id}):
        return True
    return False


def get_image_rating(db, image_name):
    """
    Adds the number of likes and dislikes for an image
    """
    result = db.images.aggregate([
        {
            '$match': {
                'image_name': image_name   # select the desired image by name
            }
        }, {
            '$unwind': {
                'path': '$ratings'  # 'path' specifies the path, 'ratings' - dictionary with the vote of a user
            }
        }, {
            '$group': {  # groups votes
                '_id': '$image_name',
                'total_rating': {
                    '$sum': '$ratings.rating'  # adds all values of the "rating" key in the "ratings" list"
                }
            }
        }
    ])
    total_rating = next(result, None)
    if total_rating:
        return total_rating['total_rating']
    return 0
