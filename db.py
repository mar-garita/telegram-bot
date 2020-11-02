from pymongo import MongoClient


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
        }
        db.users.insert_one(user)
    return user
