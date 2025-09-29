import os
import random
import asyncio
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes
)

# --- Configuration ---
TOKEN = os.environ.get('TELEGRAM_TOKEN', '8020011113:AAHNrlcw6x0sTsmvsodnV0dZyWpVbX7zxMU')

# --- In-Memory "Database" ---
user_profiles = {}

# --- Conversation Handler States ---
NAME, AGE, BIO, PHOTO = range(4)

# --- Main Functions ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bot စတင်အသုံးပြုသည့်အခါ ပင်မ Menu ကိုပြသပေးသည်"""
    keyboard = [
        [InlineKeyboardButton("👤 Profile ပြင်ဆင်/ဖန်တီးမည်", callback_data='create_profile')],
        [InlineKeyboardButton("❤️ မိတ်ဖက်ရှာဖွေမည်", callback_data='find_match')],
        [InlineKeyboardButton("📄 ကျွန်ုပ်၏ Profile ကြည့်မည်", callback_data='view_profile')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_msg = (
        "👋 မင်္ဂလာပါ။ Dating Bot မှ ကြိုဆိုပါတယ်။\n\n"
        "အောက်ပါ ခလုတ်များမှတစ်ဆင့် စတင်အသုံးပြုနိုင်ပါတယ်။"
    )
    await update.message.reply_text(welcome_msg, reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inline Keyboard မှ ခလုတ်များကို နှိပ်လိုက်သည့်အခါ အလုပ်လုပ်သည်"""
    query = update.callback_query
    await query.answer()
    
    command = query.data
    
    if command == 'find_match':
        return await find_match(update, context)
    elif command == 'view_profile':
        return await view_my_profile(update, context)

# --- Profile Creation Conversation ---

async def start_profile_creation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Profile ဖန်တီးမှု လုပ်ငန်းစဉ်ကို စတင်သည်"""
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("Profile ဖန်တီးမှုကို စတင်ပါပြီ။ သင်၏နာမည်ကို ထည့်သွင်းပေးပါ။")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User ထည့်သွင်းလိုက်သော နာမည်ကို လက်ခံပြီး အသက်မေးသည်"""
    context.user_data['name'] = update.message.text
    await update.message.reply_text(f"ကောင်းပါပြီ {context.user_data['name']}။ သင်၏အသက်ကို ပြောပြပေးပါ။")
    return AGE

async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User ၏ အသက်ကို လက်ခံပြီး မိတ်ဆက်စာကြောင်းတောင်းသည်"""
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

async def get_bio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User ၏ Bio ကိုလက်ခံပြီး ဓာတ်ပုံတောင်းသည်"""
    context.user_data['bio'] = update.message.text
    await update.message.reply_text("နောက်ဆုံးအနေနဲ့ သင့်ရဲ့ Profile ဓာတ်ပုံတစ်ပုံ ပေးပို့ပါ။")
    return PHOTO

async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User ၏ ဓာတ်ပုံကို လက်ခံပြီး Profile ကို သိမ်းဆည်းသည်"""
    user_id = update.effective_user.id
    photo_file = await update.message.photo[-1].get_file()
    
    user_profiles[user_id] = {
        'name': context.user_data['name'],
        'age': context.user_data['age'],
        'bio': context.user_data['bio'],
        'photo': photo_file.file_id,
        'username': update.effective_user.username
    }
    
    await update.message.reply_text("✅ သင်၏ Profile ကို အောင်မြင်စွာ သိမ်းဆည်းပြီးပါပြီ။")
    await view_my_profile(update, context)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Profile ဖန်တီးမှုကို ပယ်ဖျက်သည်"""
    await update.message.reply_text("Profile ဖန်တီးမှုကို ပယ်ဖျက်လိုက်ပါသည်။")
    return ConversationHandler.END

# --- Other Features ---

async def view_my_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """လက်ရှိ User ၏ Profile ကို ပြန်လည်ပြသသည်"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    if user_id in user_profiles:
        profile = user_profiles[user_id]
        caption = (
            f"👤 **{profile['name']}** ({profile['age']})\n\n"
            f"📝 **Bio:**\n{profile['bio']}\n\n"
            f"📞 **ဆက်သွယ်ရန်:** @{profile.get('username', 'N/A')}"
        )
        await context.bot.send_photo(
            chat_id=chat_id, 
            photo=profile['photo'], 
            caption=caption, 
            parse_mode='Markdown'
        )
    else:
        await context.bot.send_message(
            chat_id=chat_id, 
            text="သင့်မှာ Profile မရှိသေးပါ။ 'Profile ပြင်ဆင်/ဖန်တီးမည်' မှ စတင်နိုင်ပါတယ်။"
        )
    return ConversationHandler.END

async def find_match(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """အခြား User တစ်ဦး၏ Profile ကို ကျပန်းရှာဖွေပြီး ပြသသည်"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    available_profiles = {uid: prof for uid, prof in user_profiles.items() if uid != user_id}
    
    if len(available_profiles) > 0:
        random_user_id = random.choice(list(available_profiles.keys()))
        profile = available_profiles[random_user_id]
        
        caption = (
            f"❤️ **Match Found!**\n\n"
            f"👤 **{profile['name']}** ({profile['age']})\n\n"
            f"📝 **Bio:**\n{profile['bio']}\n\n"
            f"💬 စကားပြောဖို့အတွက် @{profile.get('username', 'N/A')} ကို ဆက်သွယ်နိုင်ပါတယ်။"
        )
        await context.bot.send_photo(
            chat_id=chat_id, 
            photo=profile['photo'], 
            caption=caption, 
            parse_mode='Markdown'
        )
    else:
        await context.bot.send_message(
            chat_id=chat_id, 
            text="တိုက်ဆိုင်စွာပဲ၊ လက်ရှိမှာ ပြသဖို့ တခြား profile မရှိသေးပါဘူး။"
        )
    return ConversationHandler.END


# --- Flask Web Server & Webhook Setup ---
app = Flask(__name__)

# Initialize Application (do NOT call build() at module level)
application = None

def setup_application():
    """Initialize the telegram application"""
    global application
    if application is None:
        application = Application.builder().token(TOKEN).build()
        
        # ConversationHandler for profile creation
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
        
        # Register handlers
        application.add_handler(CommandHandler('start', start))
        application.add_handler(CallbackQueryHandler(button_handler, pattern='^(find_match|view_profile)$'))
        application.add_handler(conv_handler)
        
        # Initialize the application
        asyncio.run(application.initialize())
    
    return application

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook_handler():
    """Handle incoming webhook updates"""
    app_instance = setup_application()
    update = Update.de_json(request.get_json(force=True), app_instance.bot)
    
    # Process update in a new event loop
    asyncio.run(app_instance.process_update(update))
    
    return 'ok'

@app.route('/')
def index():
    return 'Telegram Bot is running!'

@app.route('/health')
def health():
    return 'OK', 200

if __name__ == '__main__':
    # For local testing only - use polling
    app_instance = setup_application()
    asyncio.run(app_instance.run_polling())
