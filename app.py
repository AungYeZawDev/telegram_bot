import os
import random
import logging
import asyncio
from flask import Flask, request

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# --- Configuration ---
TOKEN = os.environ.get("TELEGRAM_TOKEN", "YOUR_FALLBACK_TOKEN")
WEBHOOK_URL = os.environ.get("RENDER_EXTERNAL_URL") # Render's public URL

# --- In-Memory "Database" ---
user_profiles = {}

# --- Conversation Handler States ---
NAME, AGE, BIO, PHOTO = range(4)

# --- Bot Functions (now async) ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message with three inline buttons attached."""
    keyboard = [
        [InlineKeyboardButton("👤 Profile ပြင်ဆင်/ဖန်တီးမည်", callback_data='create_profile')],
        [InlineKeyboardButton("❤️ မိတ်ဖက်ရှာဖွေမည်", callback_data='find_match')],
        [InlineKeyboardButton("📄 ကျွန်ုပ်၏ Profile ကြည့်မည်", callback_data='view_profile')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 မင်္ဂလာပါ။ Dating Bot မှ ကြိုဆိုပါတယ်။\n\n"
        "အောက်ပါ ခလုတ်များမှတစ်ဆင့် စတင်အသုံးပြုနိုင်ပါတယ်။",
        reply_markup=reply_markup,
    )

async def start_profile_creation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks for the user's name."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Profile ဖန်တီးမှုကို စတင်ပါပြီ။ သင်၏နာမည်ကို ထည့်သွင်းပေးပါ။")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the name and asks for their age."""
    context.user_data['name'] = update.message.text
    await update.message.reply_text(f"ကောင်းပါပြီ {context.user_data['name']}။ သင်၏အသက်ကို ပြောပြပေးပါ။")
    return AGE

async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the age and asks for their bio."""
    try:
        age = int(update.message.text)
        if 16 <= age <= 100:
            context.user_data['age'] = age
            await update.message.reply_text("သင်၏ ကိုယ်ရေးမိတ်ဆက် (Bio) အတိုချုံးကို ရေးပေးပါ။")
            return BIO
        else:
            await update.message.reply_text("အသက်သည် ၁၆ နှင့် ၁၀၀ ကြားဖြစ်ရပါမည်။ ကျေးဇူးပြု၍ ပြန်ထည့်ပါ။")
            return AGE
    except ValueError:
        await update.message.reply_text("ကျေးဇူးပြု၍ နံပါတ် (ဂဏန်း) ဖြင့်သာ ထည့်သွင်းပါ။")
        return AGE

async def get_bio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the bio and asks for a photo."""
    context.user_data['bio'] = update.message.text
    await update.message.reply_text("နောက်ဆုံးအနေနဲ့ သင့်ရဲ့ Profile ဓာတ်ပုံတစ်ပုံ ပေးပို့ပါ။")
    return PHOTO

async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the photo and ends the conversation."""
    user_id = update.effective_user.id
    photo_file = await update.message.photo[-1].get_file()
    
    user_profiles[user_id] = {
        'name': context.user_data['name'],
        'age': context.user_data['age'],
        'bio': context.user_data['bio'],
        'photo': photo_file.file_id,
        'username': update.effective_user.username,
    }
    
    await update.message.reply_text("✅ သင်၏ Profile ကို အောင်မြင်စွာ သိမ်းဆည်းပြီးပါပြီ။")
    await view_my_profile(update, context)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text("Profile ဖန်တီးမှုကို ပယ်ဖျက်လိုက်ပါသည်။")
    return ConversationHandler.END

async def view_my_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays the user's own profile."""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    # query ကနေလာတာလား message ကနေလာတာလား စစ်ဆေးခြင်း
    query = update.callback_query
    if query:
        await query.answer()

    if user_id in user_profiles:
        profile = user_profiles[user_id]
        caption = (
            f"👤 **{profile['name']}** ({profile['age']})\n\n"
            f"📝 **Bio:**\n{profile['bio']}\n\n"
            f"📞 **ဆက်သွယ်ရန်:** @{profile.get('username', 'N/A')}"
        )
        await context.bot.send_photo(chat_id=chat_id, photo=profile['photo'], caption=caption, parse_mode='Markdown')
    else:
        await context.bot.send_message(chat_id=chat_id, text="သင့်မှာ Profile မရှိသေးပါ။ '/start' မှတစ်ဆင့် ပြန်လည်စတင်နိုင်ပါတယ်။")

async def find_match(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Finds and displays a random profile."""
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    available_profiles = {uid: prof for uid, prof in user_profiles.items() if uid != user_id}
    
    if available_profiles:
        random_user_id = random.choice(list(available_profiles.keys()))
        profile = available_profiles[random_user_id]
        caption = (
            f"❤️ **Match Found!**\n\n"
            f"👤 **{profile['name']}** ({profile['age']})\n\n"
            f"📝 **Bio:**\n{profile['bio']}\n\n"
            f"💬 စကားပြောဖို့အတွက် @{profile.get('username', 'N/A')} ကို ဆက်သွယ်နိုင်ပါတယ်။"
        )
        await context.bot.send_photo(chat_id=chat_id, photo=profile['photo'], caption=caption, parse_mode='Markdown')
    else:
        await context.bot.send_message(chat_id=chat_id, text="တိုက်ဆိုင်စွာပဲ၊ လက်ရှိမှာ ပြသဖို့ တခြား profile မရှိသေးပါဘူး။")

# --- Application and Webhook Setup ---
application = Application.builder().token(TOKEN).build()

# Conversation handler for profile creation
conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_profile_creation, pattern='^create_profile$')],
    states={
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
        BIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_bio)],
        PHOTO: [MessageHandler(filters.PHOTO, get_photo)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)

application.add_handler(CommandHandler("start", start))
application.add_handler(conv_handler)
application.add_handler(CallbackQueryHandler(view_my_profile, pattern='^view_profile$'))
application.add_handler(CallbackQueryHandler(find_match, pattern='^find_match$'))

# --- Flask App ---
app = Flask(__name__)

@app.route(f'/{TOKEN}', methods=['POST'])
async def webhook():
    """Webhook endpoint to process updates."""
    update_data = request.get_json(force=True)
    update = Update.de_json(update_data, application.bot)
    await application.process_update(update)
    return 'ok'
    
@app.route('/set_webhook', methods=['GET', 'POST'])
async def set_webhook():
    """Sets the webhook."""
    if WEBHOOK_URL:
        await application.bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")
        return "Webhook set successfully"
    return "WEBHOOK_URL not set"

# This part is optional if you set the webhook manually
# It can be useful for initial setup.
@app.route('/')
def index():
    return 'Bot is running!'
