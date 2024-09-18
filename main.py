from datetime import date
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import uvloop
from utils.db import get_name, increase_count, chatdb, user_db, get_ranking, get_bot_status, broadcast_message

uvloop.install()

app = Client(
    "rankingbot",
    api_id="8143727",
    api_hash="e2e9b22c6522465b62d8445840a526b1",
    bot_token="7455412177:AAH88hiP4bt_DsMdTWyyfRBNRth3Xyl53JE",
)

@app.on_message(filters.group & ~filters.bot & ~filters.forwarded & ~filters.via_bot & ~filters.service)
async def handle_message(_, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Increment message count
    increase_count(chat_id, user_id)

@app.on_message(filters.private & filters.command("start"))
async def start(_, message: Message):
    response = (
        "**Hello!**\n\n"
        "I'm a ranking bot that tracks the top users in a chat based on message count. You can see the rankings by using /top. "
        "For more details on how to use me, check out /help.\n\n"
        "Add me to your group and make me admin to get started!"
    )
    await message.reply_text(response)

@app.on_message(filters.private & filters.command("help"))
async def help_command(_, message: Message):
    response = (
        "**Help Menu**\n\n"
        "/top - See the top 10 users in a chat based on today's messages.\n"
        "/profile - View your profile and stats.\n"
        "/status - Get the bot status and stats.\n"
        "/broadcast <message> - Broadcast a message to all users (admin only).\n"
        "Add me to a group and make me admin to track and rank users!"
    )
    await message.reply_text(response)

@app.on_message(filters.private & filters.command("status"))
async def status(_, message: Message):
    total_users, total_chats = get_bot_status()
    response = (
        f"**Bot Status:**\n\n"
        f"Total Users: {total_users}\n"
        f"Total Chats: {total_chats}\n"
    )
    await message.reply_text(response)

@app.on_message(filters.private & filters.command("broadcast"))
async def broadcast(_, message: Message):
    if not message.reply_to_message:
        await message.reply_text("Please reply to a message to broadcast.")
        return
    broadcast_text = message.reply_to_message.text
    result = broadcast_message(broadcast_text)
    await message.reply_text(result)

@app.on_message(filters.private & filters.command("profile"))
async def profile(_, message: Message):
    user_id = message.from_user.id
    user_record = user_db.find_one({"user_id": str(user_id)})

    if user_record:
        level = user_record.get("level", 1)
        message_count = user_record.get("message_count", 0)
        response = (
            f"**Your Profile:**\n\n"
            f"**Level:** {level}\n"
            f"**Messages Sent:** {message_count}\n"
        )
    else:
        response = "You don't have a profile yet."

    await message.reply_text(response)

@app.on_message(filters.group & filters.command("top"))
async def show_top_today(_, message: Message):
    chat_id = message.chat.id
    today_rankings = get_ranking(chat_id, period='today')

    if not today_rankings:
        await message.reply_text("No data available for today.",
                                 reply_markup=InlineKeyboardMarkup(
                                     [[InlineKeyboardButton("Overall Ranking", callback_data="overall")]]
                                 ))
        return

    response = "🔰 **Today's Top Users :**\n\n"
    for pos, (user_id, count) in enumerate(today_rankings.items(), start=1):
        user_name = await get_name(app, user_id)
        response += f"**{pos}.** {user_name} - {count}\n"

    total_messages = sum(today_rankings.values())
    response += f'\n✉️ Today messages: {total_messages}'

    await message.reply_text(
        response,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Overall Ranking", callback_data="overall")]]
        )
    )

print("Bot started")
app.run()
