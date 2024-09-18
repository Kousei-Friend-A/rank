from utils.db import get_name, increase_count, chatdb
import uvloop
from pyrogram.client import Client
from pyrogram import filters
from datetime import date
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

uvloop.install()
app = Client(
    "boto",
    api_id="8143727",
    api_hash="e2e9b22c6522465b62d8445840a526b1",
    bot_token="7455412177:AAH88hiP4bt_DsMdTWyyfRBNRth3Xyl53JE",
)

def create_reply_markup(button_text, callback_data):
    return InlineKeyboardMarkup([[InlineKeyboardButton(button_text, callback_data=callback_data)]])

@app.on_message(
    ~filters.bot & ~filters.forwarded & filters.group & ~filters.via_bot & ~filters.service
)
async def inc_user(_, message: Message):
    if message.text:
        command = message.text.strip()
        if command in ["/top@RankingssBot", "/top"]:
            return await show_top_today(_, message)
        elif command in ["/start@RankingssBot", "/start"]:
            return await message.reply_text(
                "**Hi, I am a ranking bot.**\n\nI can rank the top 10 users in a chat based on the number of messages they have sent.\n\nClick /top to see the top 10 users in this chat."
            )
        elif command in ["/profile@RankingssBot", "/profile"]:
            return await show_user_profile(_, message)

    chat = message.chat.id
    user = message.from_user.id
    increase_count(chat, user)
    logging.info(f"{chat}, {user} increased")

@app.on_message(filters.private)
async def start(_, message: Message):
    await message.reply_text(
        "**Hi, I am a ranking bot.**\n\nI can rank the top 10 users in a chat based on the number of messages they have sent.\n\nAdd me to a group and make me admin.\n\nClick /top to see the top 10 users in the chat."
    )

async def show_user_profile(_, message: Message):
    chat = message.chat.id
    user = message.from_user.id
    today = str(date.today())
    
    user_data = chatdb.find_one({"chat": chat})

    if not user_data or today not in user_data:
        return await message.reply_text("No profile data available for today.")

    user_messages_today = user_data[today].get(str(user), 0)
    total_messages = sum(user_data[today].values())
    user_name = await get_name(app, user)

    response_text = (
        f"**{user_name}'s Profile:**\n"
        f"📅 **Today's Messages:** {user_messages_today}\n"
        f"✉️ **Total Messages Today:** {total_messages}\n"
    )

    await message.reply_text(response_text)

async def show_top_today(_, message: Message):
    logging.info(f"Showing today's top in {message.chat.id}")
    chat = chatdb.find_one({"chat": message.chat.id})
    today = str(date.today())

    if not chat or today not in chat:
        return await message.reply_text("No data available", reply_markup=create_reply_markup("Overall Ranking", "overall"))

    t = "🔰 **Today's Top Users :**\n\n"
    pos = 1
    for i, k in sorted(chat[today].items(), key=lambda x: x[1], reverse=True)[:10]:
        name = await get_name(app, i)
        t += f"**{pos}.** {name} - {k}\n"
        pos += 1

    total = sum(chat[today].values())
    t += f'\n✉️ Today messages: {total}'

    await message.reply_text(t, reply_markup=create_reply_markup("Overall Ranking", "overall"))

@app.on_callback_query(filters.regex("overall"))
async def show_top_overall_callback(_, query: CallbackQuery):
    logging.info(f"Showing overall top in {query.message.chat.id}")
    chat = chatdb.find_one({"chat": query.message.chat.id})

    if not chat:
        return await query.answer("No data available", show_alert=True)

    await query.answer("Processing... Please wait")
    overall_dict = {}
    total = 0

    for i, k in chat.items():
        if i in {"chat", "_id"}:
            continue
        for j, l in k.items():
            overall_dict[j] = overall_dict.get(j, 0) + l
        total += sum(k.values())

    t = "🔰 **Overall Top Users :**\n\n"
    pos = 1
    for i, k in sorted(overall_dict.items(), key=lambda x: x[1], reverse=True)[:10]:
        name = await get_name(app, i)
        t += f"**{pos}.** {name} - {k}\n"
        pos += 1

    t += f'\n✉️ Today messages: {total}'
    await query.message.edit_text(t, reply_markup=create_reply_markup("Today's Ranking", "today"))

@app.on_callback_query(filters.regex("today"))
async def show_top_today_callback(_, query: CallbackQuery):
    logging.info(f"Showing today's top in {query.message.chat.id}")
    chat = chatdb.find_one({"chat": query.message.chat.id})
    today = str(date.today())

    if not chat or today not in chat:
        return await query.answer("No data available", show_alert=True)

    await query.answer("Processing... Please wait")
    t = "🔰 **Today's Top Users :**\n\n"
    pos = 1

    for i, k in sorted(chat[today].items(), key=lambda x: x[1], reverse=True)[:10]:
        name = await get_name(app, i)
        t += f"**{pos}.** {name} - {k}\n"
        pos += 1

    total = sum(chat[today].values())
    t += f'\n✉️ Today messages: {total}'

    await query.message.edit_text(t, reply_markup=create_reply_markup("Overall Ranking", "overall"))

if __name__ == "__main__":
    logging.info("Bot started")
    app.run()
