import subprocess
import sys

# 🔽 Auto install
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
    from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
except ImportError:
    print("[+] Installing library...")
    install("python-telegram-bot")
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
    from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# 🔥 CONFIG
BOT_TOKEN = "8466772134:AAE5i3HuuWowg4hz9mBkfrCx5ucxs0XmJ3A"
ADMIN_ID = 8670425757
MAIN_CHANNEL = "@pyayron"   # 👈 mandatory channel

channels = []
force_sub_enabled = True
welcome_msg = "✅ Welcome! Access Granted 🎉"

# 🔐 Admin check
def is_admin(user_id):
    return user_id == ADMIN_ID

# 📜 HELP
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = """
🤖 COMMAND PANEL

/start - Start bot
/addchannel @channel
/removechannel @channel
/list - Show channels
/setwelcome text
/forcesub - ON/OFF
/genlink - Links
"""
    await update.message.reply_text(msg)

# ➕ Add channel
async def add_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    try:
        ch = context.args[0]
        if ch not in channels:
            channels.append(ch)
            await update.message.reply_text(f"✅ Added {ch}")
    except:
        await update.message.reply_text("Usage: /addchannel @channel")

# ➖ Remove
async def remove_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    try:
        ch = context.args[0]
        channels.remove(ch)
        await update.message.reply_text(f"❌ Removed {ch}")
    except:
        await update.message.reply_text("Usage: /removechannel @channel")

# 📋 List
async def list_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not channels:
        await update.message.reply_text("❌ No channels")
    else:
        await update.message.reply_text("\n".join(channels))

# ✏️ Welcome
async def set_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global welcome_msg
    if not is_admin(update.effective_user.id):
        return
    welcome_msg = " ".join(context.args)
    await update.message.reply_text("✅ Updated")

# 🔒 Toggle
async def forcesub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global force_sub_enabled
    if not is_admin(update.effective_user.id):
        return
    force_sub_enabled = not force_sub_enabled
    await update.message.reply_text(f"ForceSub: {force_sub_enabled}")

# 🔗 Links
async def genlink(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not channels:
        await update.message.reply_text("❌ No channels")
        return

    buttons = [[InlineKeyboardButton(ch, url=f"https://t.me/{ch[1:]}")] for ch in channels]

    await update.message.reply_text(
        "🔗 Channel Links:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# 🔍 Check main channel
async def is_main_joined(user_id, context):
    try:
        member = await context.bot.get_chat_member(MAIN_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# 🔍 Check other channels
async def is_joined(user_id, context):
    for ch in channels:
        try:
            member = await context.bot.get_chat_member(ch, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

# 🚀 START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    menu = [
        ["/list", "/genlink"],
        ["/addchannel", "/removechannel"],
        ["/forcesub", "/help"]
    ]
    reply_markup = ReplyKeyboardMarkup(menu, resize_keyboard=True)

    # 🔒 Step 1: MAIN channel check
    if not await is_main_joined(user_id, context):
        buttons = [
            [InlineKeyboardButton("📢 Join Main Channel", url=f"https://t.me/{MAIN_CHANNEL[1:]}")],
            [InlineKeyboardButton("✅ I Joined", callback_data="maincheck")]
        ]

        await update.message.reply_text(
            "⚠️ Bot use karne ke liye pehle is channel ko join karna zaroori hai 👇",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    # 🔒 Step 2: Other channels
    if force_sub_enabled:
        if await is_joined(user_id, context):
            await update.message.reply_text(welcome_msg, reply_markup=reply_markup)
        else:
            buttons = [
                [InlineKeyboardButton(f"📢 Join {ch}", url=f"https://t.me/{ch[1:]}")]
                for ch in channels
            ]
            buttons.append([InlineKeyboardButton("✅ I Joined", callback_data="check")])

            await update.message.reply_text(
                "❌ Join all channels first",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    else:
        await update.message.reply_text(welcome_msg, reply_markup=reply_markup)

# 🔄 Main check button
async def main_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if await is_main_joined(user_id, context):
        await query.answer()
        await query.edit_message_text("✅ Verified! Ab /start dubara dabao 👍")
    else:
        await query.answer("❌ Abhi join nahi kiya!", show_alert=True)

# 🔄 Other check
async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if await is_joined(user_id, context):
        await query.answer()
        await query.edit_message_text(welcome_msg)
    else:
        await query.answer("❌ Not joined!", show_alert=True)

# ▶️ RUN
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_cmd))
app.add_handler(CommandHandler("addchannel", add_channel))
app.add_handler(CommandHandler("removechannel", remove_channel))
app.add_handler(CommandHandler("list", list_channels))
app.add_handler(CommandHandler("setwelcome", set_welcome))
app.add_handler(CommandHandler("forcesub", forcesub))
app.add_handler(CommandHandler("genlink", genlink))
app.add_handler(CallbackQueryHandler(main_check, pattern="maincheck"))
app.add_handler(CallbackQueryHandler(check, pattern="check"))

print("🤖 Bot Running...")
app.run_polling()