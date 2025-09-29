import os
import random
from flask import Flask, request
import telegram
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, 
                          ConversationHandler, CallbackQueryHandler)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

# --- Configuration ---
TOKEN = os.environ.get('TELEGRAM_TOKEN', '8020011113:AAHNrlcw6x0sTsmvsodnV0dZyWpVbX7zxMU')

# --- In-Memory "Database" ---
# Production app အတွက်ဆိုရင် ဒီနေရာမှာ တကယ့် Database ကိုသုံးသင့်ပါတယ်
user_profiles = {}

# --- Conversation Handler States ---
# Profile ဖန်တီးမှုအတွက် အဆင့်များကို သတ်မှတ်ခြင်း
NAME, AGE, BIO, PHOTO = range(4)

# --- Main Functions ---

def start(update, context):
    """Bot စတင်အသုံးပြုသည့်အခါ ပင်မ Menu ကိုပြသပေးသည်"""
    user_id = update.effective_user.id
    
    # Keyboard Buttons
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
    update.message.reply_text(welcome_msg, reply_markup=reply_markup)

def button_handler(update, context):
    """Inline Keyboard မှ ခလုတ်များကို နှိပ်လိုက်သည့်အခါ အလုပ်လုပ်သည်"""
    query = update.callback_query
    query.answer() # loading animation ကို ရပ်တန့်စေသည်
    
    command = query.data
    
    if command == 'create_profile':
        return start_profile_creation(update, context)
    elif command == 'find_match':
        return find_match(update, context)
    elif command == 'view_profile':
        return view_my_profile(update, context)

# --- Profile Creation Conversation ---

def start_profile_creation(update, context):
    """Profile ဖန်တီးမှု လုပ်ငန်းစဉ်ကို စတင်သည်"""
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text="Profile ဖန်တီးမှုကို စတင်ပါပြီ။ သင်၏နာမည်ကို ထည့်သွင်းပေးပါ။")
    return NAME

def get_name(update, context):
    """User ထည့်သွင်းလိုက်သော နာမည်ကို လက်ခံပြီး အသက်မေးသည်"""
    user = update.message.from_user
    context.user_data['name'] = update.message.text
    update.message.reply_text(f"ကောင်းပါပြီ {context.user_data['name']}။ သင်၏အသက်ကို ပြောပြပေးပါ။")
    return AGE

def get_age(update, context):
    """User ၏ အသက်ကို လက်ခံပြီး မိတ်ဆက်စာကြောင်းတောင်းသည်"""
    try:
        age = int(update.message.text)
        if 16 <= age <= 100:
            context.user_data['age'] = age
            update.message.reply_text("သင်၏ ကိုယ်ရေးမိတ်ဆက် (Bio) အတိုချုံးကို ရေးပေးပါ။")
            return BIO
        else:
            update.message.reply_text("အသက်သည် ၁၆ နှင့် ၁၀၀ ကြားဖြစ်ရပါမည်။ ကျေးဇူးပြု၍ ပြန်ထည့်ပါ။")
            return AGE
    except ValueError:
        update.message.reply_text("ကျေးဇူးပြု၍ နံပါတ် (ဂဏန်း) ဖြင့်သာ ထည့်သွင်းပါ။")
        return AGE

def get_bio(update, context):
    """User ၏ Bio ကိုလက်ခံပြီး ဓာတ်ပုံတောင်းသည်"""
    context.user_data['bio'] = update.message.text
    update.message.reply_text("နောက်ဆုံးအနေနဲ့ သင့်ရဲ့ Profile ဓာတ်ပုံတစ်ပုံ ပေးပို့ပါ။")
    return PHOTO

def get_photo(update, context):
    """User ၏ ဓာတ်ပုံကို လက်ခံပြီး Profile ကို သိမ်းဆည်းသည်"""
    user_id = update.effective_user.id
    photo_file = update.message.photo[-1].get_file()
    
    # Profile data ကို global dictionary ထဲမှာ သိမ်းဆည်းခြင်း
    user_profiles[user_id] = {
        'name': context.user_data['name'],
        'age': context.user_data['age'],
        'bio': context.user_data['bio'],
        'photo': photo_file.file_id, # ဓာတ်ပုံကို file_id အနေနဲ့ သိမ်းထားပါမယ်။
        'username': update.effective_user.username
    }
    
    update.message.reply_text("✅ သင်၏ Profile ကို အောင်မြင်စွာ သိမ်းဆည်းပြီးပါပြီ။")
    view_my_profile(update, context) # Profile သိမ်းပြီးကြောင်း ပြန်ပြပေးခြင်း
    return ConversationHandler.END # Conversation ကို ရပ်တန့်လိုက်ခြင်း

def cancel(update, context):
    """Profile ဖန်တီးမှုကို ပယ်ဖျက်သည်"""
    update.message.reply_text("Profile ဖန်တီးမှုကို ပယ်ဖျက်လိုက်ပါသည်။")
    return ConversationHandler.END

# --- Other Features ---

def view_my_profile(update, context):
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
        context.bot.send_photo(chat_id=chat_id, photo=profile['photo'], caption=caption, parse_mode='Markdown')
    else:
        context.bot.send_message(chat_id=chat_id, text="သင့်မှာ Profile မရှိသေးပါ။ 'Profile ပြင်ဆင်/ဖန်တီးမည်' မှ စတင်နိုင်ပါတယ်။")
    return ConversationHandler.END

def find_match(update, context):
    """အခြား User တစ်ဦး၏ Profile ကို ကျပန်းရှာဖွေပြီး ပြသသည်"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    # ကိုယ့် profile မဟုတ်တဲ့ တခြား profile တွေကို list လုပ်ပါ
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
        context.bot.send_photo(chat_id=chat_id, photo=profile['photo'], caption=caption, parse_mode='Markdown')
    else:
        context.bot.send_message(chat_id=chat_id, text="တိုက်ဆိုင်စွာပဲ၊ လက်ရှိမှာ ပြသဖို့ တခြား profile မရှိသေးပါဘူး။")
    return ConversationHandler.END


# --- Flask Web Server & Webhook Setup ---
bot = telegram.Bot(token=TOKEN)
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

# ConversationHandler for profile creation
conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_profile_creation, pattern='^create_profile$')],
    states={
        NAME: [MessageHandler(Filters.text & ~Filters.command, get_name)],
        AGE: [MessageHandler(Filters.text & ~Filters.command, get_age)],
        BIO: [MessageHandler(Filters.text & ~Filters.command, get_bio)],
        PHOTO: [MessageHandler(Filters.photo, get_photo)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)

# Register handlers
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CallbackQueryHandler(button_handler, pattern='^(find_match|view_profile)$'))
dispatcher.add_handler(conv_handler) # Conversation handler ကိုထည့်သွင်းခြင်း

app = Flask(__name__)

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook_handler():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'ok'
