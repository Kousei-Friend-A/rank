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

@app.on_message(filters.command("profile"))
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

print("Bot started")
app.run()
