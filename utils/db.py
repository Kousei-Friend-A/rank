from pymongo import MongoClient
from datetime import date

# MongoDB connection setup
uri = "mongodb://root:JlVQfH9cTsdvjK3uqry8mnip1iK81KDgl9g7TwAa4U7JgGBOIbpcgH7s6Fikp247@jk4cgscg8440gcswkw4cgswg:27017/?directConnection=true"
mongo = MongoClient(uri).Rankings
chatdb = mongo.chat
user_db = mongo.users

# Increment message count and update user level
def increase_count(chat, user):
    today = str(date.today())
    user = str(user)

    # Fetch or initialize today's data
    chat_data = chatdb.find_one({"chat": chat})
    if not chat_data:
        chat_data = {}
    today_data = chat_data.get(today, {})

    # Update today's message count
    if user in today_data:
        today_data[user] += 1
    else:
        today_data[user] = 1

    # Update overall message count
    overall_data = chat_data.get("overall", {})
    if user in overall_data:
        overall_data[user] += 1
    else:
        overall_data[user] = 1

    # Save updates
    chat_data[today] = today_data
    chat_data["overall"] = overall_data
    chatdb.update_one({"chat": chat}, {"$set": chat_data}, upsert=True)

    # Update user XP and level
    update_user_level(user)

def update_user_level(user_id):
    user_id = str(user_id)
    user_record = user_db.find_one({"user_id": user_id})
    if not user_record:
        user_db.insert_one({"user_id": user_id, "message_count": 1, "level": 1})
    else:
        message_count = user_record["message_count"] + 1
        new_level = calculate_level(message_count)
        old_level = user_record["level"]
        if new_level > old_level:
            # Notify user about level-up
            send_level_up_notification(user_id, old_level, new_level)
        user_db.update_one({"user_id": user_id}, {"$set": {"message_count": message_count, "level": new_level}})

def calculate_level(message_count):
    # Simple leveling formula: 1 level per 100 messages
    return (message_count // 100) + 1

def get_bot_status():
    total_users = user_db.count_documents({})
    total_chats = chatdb.count_documents({})
    return total_users, total_chats

def get_ranking(chat_id, period='today'):
    """ Get rankings for a chat based on the period ('today' or 'overall') """
    chat_data = chatdb.find_one({"chat": chat_id})
    if not chat_data:
        return {}

    if period == 'today':
        date_str = str(date.today())
        rankings = chat_data.get(date_str, {})
    elif period == 'overall':
        rankings = chat_data.get("overall", {})
    else:
        raise ValueError("Invalid period specified. Use 'today' or 'overall'.")

    # Sort rankings in descending order
    sorted_rankings = dict(sorted(rankings.items(), key=lambda item: item[1], reverse=True))
    return sorted_rankings

async def get_name(app, user_id):
    try:
        user = await app.get_users(user_id)
        return f"{user.first_name or ''} {user.last_name or ''}".strip()
    except Exception as e:
        print(f"Error fetching user info: {e}")
        return str(user_id)

def broadcast_message(message_text):
    """ Broadcast a message to all users in the user_db collection """
    try:
        users = user_db.find()
        for user in users:
            try:
                # Example: Send message to users (assuming `send_message` function is available)
                # Replace `send_message` with actual implementation
                send_message(user['user_id'], message_text)
            except Exception as e:
                print(f"Error sending message to {user['user_id']}: {e}")
        return "Broadcast message sent successfully."
    except Exception as e:
        return f"An error occurred: {e}"

def send_message(user_id, message_text):
    """ Dummy function for sending a message to a user - replace with actual implementation """
    # This function should be replaced with your actual method for sending messages
    print(f"Sending to {user_id}: {message_text}")

