from pymongo.mongo_client import MongoClient
from datetime import date
import logging

uri = "mongodb://root:JlVQfH9cTsdvjK3uqry8mnip1iK81KDgl9g7TwAa4U7JgGBOIbpcgH7s6Fikp247@jk4cgscg8440gcswkw4cgswg:27017/?directConnection=true"
mongo = MongoClient(uri).Rankings
chatdb = mongo.chat

def increase_count(chat, user):
    user = str(user)
    today = str(date.today())
    user_db = chatdb.find_one({"chat": chat})

    if not user_db or today not in user_db:
        user_db = {today: {}}
    else:
        user_db = user_db[today]

    chatdb.update_one(
        {"chat": chat},
        {"$inc": {f"{today}.{user}": 1}},
        upsert=True
    )

name_cache = {}

async def get_name(app, id):
    global name_cache

    if id in name_cache:
        return name_cache[id]
    else:
        try:
            i = await app.get_users(id)
            name = f'{(i.first_name or "")} {(i.last_name or "")}'
            name_cache[id] = name
            return name
        except Exception as e:
            logging.error(f"Error getting user name for ID {id}: {e}")
            return id
