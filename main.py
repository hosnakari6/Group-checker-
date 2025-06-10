from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from collections import defaultdict
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
)
from flask import Flask, request
import os
import asyncio

# API اطلاعات
api_id = 25262108
api_hash = '4ffb214ab07139ed3c5a7fceb18b9beb'
bot_token = '7665032941:AAH4rhhFnpp83zpCXcITY7RY7cFvcEKTLOk'

telethon_client = TelegramClient('myuser', api_id, api_hash)

# پیام خوش‌آمدگویی
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! لینک یا آیدی گروه رو بفرست تا سال ساخت و تعداد پیام‌ها رو بهت بگم.")

# ذخیره پیام‌ها
def save_message(user_id, message_text):
    with open("messages.txt", "a", encoding="utf-8") as f:
        f.write(f"{user_id} >> {message_text}\n")

# پردازش پیام کاربر
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    user_id = update.message.from_user.id
    save_message(user_id, text)

    if "t.me/" in text:
        username = text.split("/")[-1]
    elif text.startswith("@"):
        username = text[1:]
    else:
        username = text

    if not username:
        await update.message.reply_text("❗ لطفاً لینک یا آیدی گروه رو درست وارد کن.")
        return

    try:
        await telethon_client.start()
        entity = await telethon_client.get_entity(username)
        offset_id = 0
        limit = 100
        years_count = defaultdict(int)
        oldest_date = None

        while True:
            history = await telethon_client(GetHistoryRequest(
                peer=entity,
                offset_id=offset_id,
                offset_date=None,
                add_offset=0,
                limit=limit,
                max_id=0,
                min_id=0,
                hash=0
            ))
            messages = history.messages
            if not messages:
                break
            for msg in messages:
                date = msg.date
                years_count[date.year] += 1
                if not oldest_date or date < oldest_date:
                    oldest_date = date
            offset_id = messages[-1].id
            if len(messages) < limit:
                break

        if oldest_date:
            response = f"📆 سال ساخت گروه: {oldest_date.year}\n📊 تعداد پیام‌ها:\n"
            for year in sorted(years_count):
                response += f"{year}: {years_count[year]} پیام\n"
        else:
            response = "❗ پیامی پیدا نشد یا دسترسی ندارم."

        await update.message.reply_text(response)

    except Exception as e:
        await update.message.reply_text(f"❌ خطا:\n{str(e)}")

# راه‌اندازی بات
app = ApplicationBuilder().token(bot_token).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, handle_message))

# Flask App
web_app = Flask(__name__)

@web_app.route(f"/{bot_token}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), app.bot)
    asyncio.get_event_loop().create_task(app.process_update(update))
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 80))
    web_app.run(host="0.0.0.0", port=port)

