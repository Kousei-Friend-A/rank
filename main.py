from utils.db import get_name, increase_count, chatdb
import uvloop
from pyrogram.client import Client
from pyrogram import filters
from datetime import date
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

uvloop.install()
app = Client(
    "boto",
    api_id="8143727",
    api_hash="e2e9b22c6522465b62d8445840a526b1",
    bot_token="7410449895:AAEDKUZgESTW9WEDIk5CNiduYdtmnJoN1gQ",
)


@app.on_message(
    ~filters.bot
    & ~filters.forwarded
    & filters.group
    & ~filters.via_bot
    & ~filters.service
)
async def inc_user(_, message: Message):
    if message.text:
        if (
            message.text.strip() == "/topRankingX_bot"
            or message.text.strip() == "/top"
        ):
            return await show_top_today(_, message)
        if (
            message.text.strip() == "/start@RankingX_bot"
            or message.text.strip() == "/start"
        ):
            return await message.reply_text(
                "**Hi, I am a ranking bot.**\n\nI can rank the top 10 users in a chat based on the number of messages they have sent.\n\nClick /top to see the top 10 users in this chat."
            )

    chat = message.chat.id
    user = message.from_user.id
    increase_count(chat, user)
    print(chat, user, "increased")


@app.on_message(filters.private)
async def start(_, message: Message):
    await message.reply_text(
        "**Hi, I am a ranking bot.**\n\nI can rank the top 10 users in a chat based on the number of messages they have sent.\n\nAdd me to a group and make me admin.\n\nClick /top to see the top 10 users in the chat."
    )


@app.on_message(filters.private | filters.group)
async def status_command(_, message: Message):
    if message.text and message.text.strip() == "/status":
        # Fetch overall data from the database
        all_chats = chatdb.find()  # Retrieve all chat documents

        total_chats = 0
        total_users = set()  # Use a set to avoid counting duplicates
        total_messages = 0

        for chat in all_chats:
            total_chats += 1
            total_messages += sum(
                sum(user_counts.values()) for user_counts in chat.values() if isinstance(user_counts, dict)
            )
            total_users.update(chat.keys() - {"chat", "_id"})  # Add user IDs to the set

        response_text = (
            f"**Bot Status:**\n"
            f"- Total Chats: {total_chats}\n"
            f"- Total Users: {len(total_users)}\n"
            f"- Total Messages: {total_messages}\n"
        )
        
        await message.reply_text(response_text)


async def show_top_today(_, message: Message):
    print("today top in", message.chat.id)
    chat = chatdb.find_one({"chat": message.chat.id})
    today = str(date.today())

    if not chat:
        return await message.reply_text("no data available",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Overall Ranking", callback_data="overall")]]
        ),)

    if not chat.get(today):
        return await message.reply_text("no data available for today",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Overall Ranking", callback_data="overall")]]
        ),)

    t = "🔰 **Today's Top Users :**\n\n"

    pos = 1
    for i, k in sorted(chat[today].items(), key=lambda x: x[1], reverse=True)[:10]:
        i = await get_name(app, i)

        t += f"**{pos}.** {i} - {k}\n"
        pos += 1

    total = sum(chat[today].values())
    t += f'\n✉️ Today messages: {total}'

    await message.reply_text(
        t,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Overall Ranking", callback_data="overall")]]
        ),
    )


@app.on_callback_query(filters.regex("overall"))
async def show_top_overall_callback(_, query: CallbackQuery):
    print("overall top in", query.message.chat.id)
    chat = chatdb.find_one({"chat": query.message.chat.id})

    if not chat:
        return await query.answer("No data available", show_alert=True)

    await query.answer("Processing... Please wait")

    t = "🔰 **Overall Top Users :**\n\n"

    overall_dict = {}
    total = 0
    for i, k in chat.items():
        if i == "chat" or i == "_id":
            continue

        for j, l in k.items():
            if j not in overall_dict:
                overall_dict[j] = l
            else:
                overall_dict[j] += l

        total += sum(k.values())
    
    pos = 1
    for i, k in sorted(overall_dict.items(), key=lambda x: x[1], reverse=True)[:10]:
        i = await get_name(app, i)

        t += f"**{pos}.** {i} - {k}\n"
        pos += 1

    t += f'\n✉️ Today messages: {total}'

    await query.message.edit_text(
        t,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Today's Ranking", callback_data="today")]]
        ),
    )


@app.on_callback_query(filters.regex("today"))
async def show_top_today_callback(_, query: CallbackQuery):
    print("today top in", query.message.chat.id)
    chat = chatdb.find_one({"chat": query.message.chat.id})
    today = str(date.today())

    if not chat:
        return await query.answer("No data available", show_alert=True)

    if not chat.get(today):
        return await query.answer("No data available for today", show_alert=True)

    await query.answer("Processing... Please wait")

    t = "🔰 **Today's Top Users :**\n\n"

    pos = 1
    for i, k in sorted(chat[today].items(), key=lambda x: x[1], reverse=True)[:10]:
        i = await get_name(app, i)

        t += f"**{pos}.** {i} - {k}\n"
        pos += 1

    total = sum(chat[today].values())
    t += f'\n✉️ Today messages: {total}'

    await query.message.edit_text(
        t,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Overall Ranking", callback_data="overall")]]
        ),
    )


print("started")
app.run()
