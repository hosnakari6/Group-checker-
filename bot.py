import asyncio
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from collections import defaultdict
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters,
)

# ⚙️ اطلاعات حساب و ربات
api_id = 25262108
api_hash = '4ffb214ab07139ed3c5a7fceb18b9beb'
bot_token = '7665032941:AAH4rhhFnpp83zpCXcITY7RY7cFvcEKTLOk'

telethon_client = TelegramClient('myuser', api_id, api_hash)

# 📩 ذخیره پیام دریافتی در فایل
def save_message(user_id, message_text):
    with open("messages.txt", "a", encoding="utf-8") as file:
        file.write(f"{user_id} >> {message_text}\n")

# ✅ پیام خوش‌آمدگویی
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "سلام! 🤖\n"
        "با این ربات می‌تونی سال ساخت گروه‌های تلگرام، آمار پیام‌ها و آیدی عددی رو ببینی 📆📊🆔\n\n"
        "📌 فقط کافیه لینک یا آیدی گروه عمومی رو بفرستی:\n"
        "- https://t.me/examplegroup\n"
        "- @examplegroup\n"
        "- یا فقط اسم گروه: examplegroup\n\n"
        "بعد از چند لحظه، من بهت اطلاعات دقیق رو می‌دم 😎"
    )
    await update.message.reply_text(welcome_text)

# 📬 بررسی و پاسخ به پیام‌های کاربر
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
        group_id = entity.id  # آی‌دی عددی گروه
        offset_id = 0
        limit = 100
        years_count = defaultdict(int)
        oldest_message_date = None

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

            for message in messages:
                msg_date = message.date
                years_count[msg_date.year] += 1
                if not oldest_message_date or msg_date < oldest_message_date:
                    oldest_message_date = msg_date

            offset_id = messages[-1].id
            if len(messages) < limit:
                break

        if oldest_message_date:
            created_year = oldest_message_date.year
            response = f"📆 سال ساخت گروه: {created_year}\n"
            response += f"🆔 آی‌دی عددی گروه: `{group_id}`\n\n"
            response += "📊 تعداد پیام‌ها بر اساس سال:\n"
            for year in sorted(years_count):
                response += f"📅 {year}: {years_count[year]} پیام\n"
        else:
            response = "❗ هیچ پیامی پیدا نشد. ممکنه گروه خالی باشه یا من دسترسی نداشته باشم."

        await update.message.reply_text(response, parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text(f"❌ خطا:\n{str(e)}")

# 🟢 اجرای بات بدون خطا در Termux
async def init():
    await telethon_client.start()

def main():
    asyncio.get_event_loop().run_until_complete(init())
    app = ApplicationBuilder().token(bot_token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    print("🤖 ربات با موفقیت راه‌اندازی شد.")
    app.run_polling(stop_signals=None)

if __name__ == "__main__":
    main()
