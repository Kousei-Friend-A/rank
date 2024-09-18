from pymongo.mongo_client import MongoClient
from datetime import date
import logging

uri = "mongodb://root:6cK44nQntSN0Cru8Nqstxxb8CDbSxsFo9PL55UByB323BM42z9H7HsaqXFn4etD4@eog8448c8skw4wk0cogwsk4s:27017/?directConnection=true"
mongo = MongoClient(uri).Rankings
chatdb = mongo.chat

def increase_count(chat, user):
    user = str(user)
    today = str(date.today())
    
    chatdb.update_one(
        {"chat": chat},
        {
            "$setOnInsert": {today: {}},  # Create today's entry if it doesn't exist
            "$inc": {f"{today}.{user}": 1}  # Increment the user's count for today
        },
        upsert=True
    )

def get_user_profile(chat, user):
    user = str(user)
    today = str(date.today())
    
    user_data = chatdb.find_one({"chat": chat})

    if not user_data or today not in user_data:
        return {
            "today_count": 0,
            "total_count": 0
        }

    today_count = user_data[today].get(user, 0)  # Messages sent today
    total_count = sum(user_data[today].values())  # Total messages today

    return {
        "today_count": today_count,
        "total_count": total_count
    }

name_cache = {}

async def get_name(app, id):
    global name_cache

    if id in name_cache:
        return name_cache[id]
    else:
        try:
            user_info = await app.get_users(id)
            name = f'{(user_info.first_name or "")} {(user_info.last_name or "")}'
            name_cache[id] = name
            return name
        except Exception as e:
            logging.error(f"Error getting user name for ID {id}: {e}")
            return id
