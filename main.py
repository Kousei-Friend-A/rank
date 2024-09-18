from utils.db import get_name, increase_count, chatdb, user_db, get_ranking, get_bot_status, broadcast_message
import uvloop
from pyrogram import Client, filters
from datetime import date
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

uvloop.install()
app = Client(
    "rankingbot",
    api_id="8143727",
    api_hash="e2e9b22c6522465b62d8445840a526b1",
    bot_token="7455412177:AAH88hiP4bt_DsMdTWyyfRBNRth3Xyl53JE",
)

@app.on_message(filters.group & ~filters.bot & ~filters.forwarded & ~filters.via_bot & ~filters.service)
async def inc_user(_, message: Message):
    if message.text:
        if message.text.strip() in ["/top", "/top@RankingX_bot"]:
            return await show_top_today(_, message)

    chat = message.chat.id
    user = message.from_user.id
    increase_count(chat, user)

@app.on_message(filters.private & filters.command("start"))
async def start(_, message: Message):
    await message.reply_text(
        "**Hi, I am a ranking bot.**\n\n"
        "I can rank the top 10 users in a chat based on the number of messages they have sent.\n"
        "Add me to a group and make me admin."
    )

@app.on_message(filters.private & filters.command("top"))
async def top_in_private(_, message: Message):
    await message.reply_text("The /top command can only be used in groups.")

@app.on_message(filters.private & filters.command("status"))
async def status(_, message: Message):
    total_users, total_chats = get_bot_status()
    response = f"**Bot Status:**\n\nTotal Users: {total_users}\nTotal Chats: {total_chats}\n"
    await message.reply_text(response)

@app.on_message(filters.private & filters.command("profile"))
@app.on_message(filters.group & filters.command("profile"))
async def profile(_, message: Message):
    user_id = message.from_user.id
    user_record = user_db.find_one({"user_id": str(user_id)})

    if user_record:
        level = user_record.get("level", 1)
        message_count = user_record.get("message_count", 0)
        response = f"**Your Profile:**\n\n**Level:** {level}\n**Messages Sent:** {message_count}\n"
    else:
        response = "You don't have a profile yet."

    await message.reply_text(response)

async def show_top_today(_, message: Message):
    chat = chatdb.find_one({"chat": message.chat.id})
    today = str(date.today())

    if not chat or today not in chat:
        return await message.reply_text("No data available for today.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Overall Ranking", callback_data="overall")]]))

    response = "🔰 **Today's Top Users :**\n\n"
    for pos, (user_id, count) in enumerate(sorted(chat[today].items(), key=lambda x: x[1], reverse=True)[:10], start=1):
        user_name = await get_name(app, user_id)
        response += f"**{pos}.** {user_name} - {count}\n"

    total_messages = sum(chat[today].values())
    response += f'\n✉️ Today messages: {total_messages}'

    await message.reply_text(response, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Overall Ranking", callback_data="overall")]]))

@app.on_callback_query(filters.regex("overall"))
async def show_top_overall_callback(_, query: CallbackQuery):
    chat = chatdb.find_one({"chat": query.message.chat.id})

    if not chat:
        return await query.answer("No data available", show_alert=True)

    response = "🔰 **Overall Top Users :**\n\n"
    overall_dict = {}
    for user_id, message_counts in chat.items():
        if user_id in ["chat", "_id"]:
            continue
        for date_key, count in message_counts.items():
            overall_dict[user_id] = overall_dict.get(user_id, 0) + count

    for pos, (user_id, count) in enumerate(sorted(overall_dict.items(), key=lambda x: x[1], reverse=True)[:10], start=1):
        user_name = await get_name(app, user_id)
        response += f"**{pos}.** {user_name} - {count}\n"

    await query.message.edit_text(response, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Today's Ranking", callback_data="today")]]))

@app.on_callback_query(filters.regex("today"))
async def show_top_today_callback(_, query: CallbackQuery):
    chat = chatdb.find_one({"chat": query.message.chat.id})
    today = str(date.today())

    if not chat or today not in chat:
        return await query.answer("No data available for today", show_alert=True)

    response = "🔰 **Today's Top Users :**\n\n"
    for pos, (user_id, count) in enumerate(sorted(chat[today].items(), key=lambda x: x[1], reverse=True)[:10], start=1):
        user_name = await get_name(app, user_id)
        response += f"**{pos}.** {user_name} - {count}\n"

    await query.message.edit_text(response, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Overall Ranking", callback_data="overall")]]))

@app.on_message(filters.private & filters.command("broadcast"))
async def broadcast(_, message: Message):
    if not message.reply_to_message:
        await message.reply_text("Please reply to a message to broadcast.")
        return
    broadcast_text = message.reply_to_message.text
    result = await broadcast_message(broadcast_text)
    await message.reply_text(result)

print("Bot started")
app.run()
