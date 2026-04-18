import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# 🔥 CONFIG
BOT_TOKEN = os.getenv("8466772134:AAE5i3HuuWowg4hz9mBkfrCx5ucxs0XmJ3A")   # 🔐 env se lega
ADMIN_ID = 8670425757
MAIN_CHANNEL = "@pyayron"

channels = []
force_sub_enabled = True
welcome_msg = "✅ Welcome! Access Granted 🎉"

# 🔐 Admin check
def is_admin(user_id):
    return user_id == ADMIN_ID

# 📜 HELP
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""
🤖 COMMAND PANEL

/start - Start bot
/addchannel @channel
/removechannel @channel
/list - Show channels
/setwelcome text
/forcesub - ON/OFF
/genlink - Links
""")

# ➕ Add channel
async def add_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    if context.args:
        ch = context.args[0]
        channels.append(ch)
        await update.message.reply_text(f"✅ Added {ch}")

# ➖ Remove
async def remove_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    if context.args:
        ch = context.args[0]
        if ch in channels:
            channels.remove(ch)
            await update.message.reply_text(f"❌ Removed {ch}")

# 📋 List
async def list_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("\n".join(channels) if channels else "❌ No channels")

# 🔗 Links
async def genlink(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [[InlineKeyboardButton(ch, url=f"https://t.me/{ch[1:]}")] for ch in channels]
    await update.message.reply_text("🔗 Links:", reply_markup=InlineKeyboardMarkup(buttons))

# 🔍 Check main channel
async def is_main_joined(user_id, context):
    try:
        member = await context.bot.get_chat_member(MAIN_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# 🚀 START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not await is_main_joined(user_id, context):
        buttons = [
            [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{MAIN_CHANNEL[1:]}")],
            [InlineKeyboardButton("✅ I Joined", callback_data="maincheck")]
        ]
        await update.message.reply_text("❌ Join channel first", reply_markup=InlineKeyboardMarkup(buttons))
        return

    await update.message.reply_text("✅ Welcome! Bot Ready 🚀")

# 🔄 Verify
async def main_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if await is_main_joined(user_id, context):
        await query.answer()
        await query.edit_message_text("✅ Verified! Use /start again")
    else:
        await query.answer("❌ Not joined!", show_alert=True)

# ▶️ RUN
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_cmd))
app.add_handler(CommandHandler("addchannel", add_channel))
app.add_handler(CommandHandler("removechannel", remove_channel))
app.add_handler(CommandHandler("list", list_channels))
app.add_handler(CommandHandler("genlink", genlink))
app.add_handler(CallbackQueryHandler(main_check, pattern="maincheck"))

print("🤖 Bot Running...")
app.run_polling()
