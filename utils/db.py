from pymongo.mongo_client import MongoClient
from datetime import date

uri = "mongodb+srv://friendakouseimanu:asdfg@cluster0.1trpq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
mongo = MongoClient(uri)
chatdb = mongo.Rankings.chat
statistics_db = mongo.Rankings.statistics  # New collection for statistics

def increase_count(chat, user):
    user = str(user)
    today = str(date.today())
    user_db = chatdb.find_one({"chat": chat})

    if not user_db:
        user_db = {}
        total_stats = {
            "total_users": 0,
            "total_messages": 0,
            "total_chats": 1  # New chat
        }
        statistics_db.update_one({}, {"$set": total_stats}, upsert=True)
    else:
        total_stats = statistics_db.find_one({}) or {"total_users": 0, "total_messages": 0, "total_chats": 0}

    # Increase message count
    if today not in user_db:
        user_db[today] = {}

    if user in user_db[today]:
        user_db[today][user] += 1
    else:
        user_db[today][user] = 1

    # Update statistics
    total_stats["total_messages"] += 1
    total_stats["total_users"] = len(user_db[today])
    statistics_db.update_one({}, {"$set": total_stats})

    chatdb.update_one({"chat": chat}, {"$set": {today: user_db}}, upsert=True)

name_cache = {}

async def get_name(app, id):
    global name_cache

    if id in name_cache:
        return name_cache[id]
    else:
        try:
            i = await app.get_users(id)
            i = f'{(i.first_name or "")} {(i.last_name or "")}'
            name_cache[id] = i
            return i
        except Exception as e:
            print(f"Error fetching user name: {e}")
            return id
