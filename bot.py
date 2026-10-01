import asyncio
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes
)

BOT_TOKEN = os.environ.get("8942556325:AAHBG_0oOQXSSUN1OylliW7F-WSDqW2HIR8")
CHANNEL_ID = "@MangaArchivet"
FILES_CHANNEL = -1003518383059


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    try:
        member = await context.bot.get_chat_member(CHANNEL_ID, user_id)
        if member.status not in ['member', 'administrator', 'creator']:
            await send_join(update, context)
            return
    except Exception as e:
        print("Error membership:", e)
        await send_join(update, context)
        return

    if context.args:
        arg = context.args[0]
        try:
            if "-" in arg and "_" not in arg:
                start_id, end_id = arg.split("-")
                start_id = int(start_id)
                end_id = int(end_id)
                if start_id > end_id:
                    start_id, end_id = end_id, start_id
                ids = list(range(start_id, end_id + 1))
                await send_multiple_files(update, context, ids)
            elif "_" in arg:
                ids = [int(x) for x in arg.split("_")]
                await send_multiple_files(update, context, ids)
            else:
                msg_id = int(arg)
                await send_single_file(update, context, msg_id)
        except ValueError:
            await update.message.reply_text("❌ شماره نامعتبر")
        return

    await update.message.reply_text(
        "👋 سلام!\nبرای دریافت فایل، روی لینک‌های داخل پست‌های کانال کلیک کن."
    )


async def send_single_file(update, context, msg_id):
    try:
        await context.bot.copy_message(
            chat_id=update.effective_user.id,
            from_chat_id=FILES_CHANNEL,
            message_id=msg_id
        )
    except Exception as e:
        print(f"خطا در ارسال {msg_id}: {e}")
        await update.message.reply_text(f"❌ خطا: {e}")


async def send_multiple_files(update, context, msg_ids):
    info = await update.message.reply_text(
        f"⏳ در حال ارسال {len(msg_ids)} فایل..."
    )
    success = 0
    failed = 0
    for i, msg_id in enumerate(msg_ids):
        try:
            await context.bot.copy_message(
                chat_id=update.effective_user.id,
                from_chat_id=FILES_CHANNEL,
                message_id=msg_id
            )
            success += 1
            if (i + 1) % 20 == 0:
                await asyncio.sleep(3)
            else:
                await asyncio.sleep(0.5)
        except Exception as e:
            print(f"خطا در ارسال {msg_id}: {e}")
            failed += 1

    await info.delete()
    report = f"✅ {success} فایل ارسال شد"
    if failed:
        report += f"\n❌ {failed} فایل خطا داشت"
    await update.message.reply_text(report)


async def send_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📢 عضویت در کانال", url="https://t.me/MangaArchivet")],
        [InlineKeyboardButton("✅ بررسی مجدد", callback_data="check")]
    ]
    await update.message.reply_text(
        "⛔️ برای دریافت فایل، ابتدا در کانال عضو شوید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    try:
        member = await context.bot.get_chat_member(CHANNEL_ID, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            await query.edit_message_text("✅ عضویت تایید شد! حالا روی لینک پست موردنظر بزن.")
        else:
            await query.answer("❌ هنوز عضو نشدی!", show_alert=True)
    except Exception:
        await query.answer("❌ خطا در بررسی!", show_alert=True)


app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(check, pattern="^check$"))

print("ربات روشن شد...")
app.run_polling(bootstrap_retries=-1)
