import os
import random
from quart import Quart, request
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
daily_stats = {}  # Track daily usage for users

# --- Conversation Handler States ---
NAME, AGE, BIO, PHOTO, LOCATION, INTERESTS, LOOKING_FOR, GENDER, GENDER_PREFERENCE = range(9)

# --- Enhanced Data Structure ---
INTERESTS_OPTIONS = [
    "🎵 Music", "🎬 Movies", "📚 Reading", "🏃 Sports", "🍳 Cooking", 
    "✈️ Travel", "🎮 Gaming", "🎨 Art", "💃 Dancing", "📸 Photography",
    "🏔️ Hiking", "🏊 Swimming", "🧘 Yoga", "🎸 Guitar", "🐕 Animals"
]

LOOKING_FOR_OPTIONS = [
    "💕 Long-term relationship", "👫 Friendship", "💬 Casual dating", 
    "🤝 Networking", "🎯 Something serious"
]

# Gender options
GENDER_OPTIONS = [
    "👨 Male", "👩 Female", "🏳️‍⚧️ Non-binary", "❓ Prefer not to say"
]

GENDER_PREFERENCE_OPTIONS = [
    "👨 Men", "👩 Women", "🏳️‍⚧️ Non-binary", "💫 Everyone"
]

# Daily limits
DAILY_LIKES_LIMIT = 50
DAILY_SUPER_LIKES_LIMIT = 5

# --- Main Functions ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bot စတင်အသုံးပြုသည့်အခါ ပင်မ Menu ကိုပြသပေးသည်"""
    keyboard = [
        [InlineKeyboardButton("👤 Profile ပြင်ဆင်/ဖန်တီးမည်", callback_data='create_profile')],
        [InlineKeyboardButton("❤️ မိတ်ဖက်ရှာဖွေမည်", callback_data='find_match')],
        [InlineKeyboardButton("📄 ကျွန်ုပ်၏ Profile ကြည့်မည်", callback_data='view_profile')],
        [InlineKeyboardButton("🔍 Advanced Search", callback_data='advanced_search')],
        [InlineKeyboardButton("💌 Messages", callback_data='view_messages')],
        [InlineKeyboardButton("⭐ Super Likes", callback_data='super_likes')],
        [InlineKeyboardButton("⚙️ Settings", callback_data='settings')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_msg = (
        "👋 မင်္ဂလာပါ။ Dating Bot မှ ကြိုဆိုပါတယ်။\n\n"
        "🔥 New Features:\n"
        "• Advanced search filters\n"
        "• Super likes system\n" 
        "• Private messaging\n"
        "• Location-based matching\n\n"
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
    elif command == 'advanced_search':
        return await advanced_search_menu(update, context)
    elif command == 'view_messages':
        return await view_messages(update, context)
    elif command == 'super_likes':
        return await super_likes_menu(update, context)
    elif command == 'settings':
        return await settings_menu(update, context)
    elif command == 'main_menu':
        return await show_main_menu(update, context)
    elif command == 'reset_likes':
        return await reset_likes(update, context)
    elif command == 'change_gender_pref':
        return await change_gender_preference(update, context)
    elif command == 'search_age':
        return await search_by_age(update, context)
    elif command == 'search_location':
        return await search_by_location(update, context)
    elif command == 'search_interests':
        return await search_by_interests(update, context)
    elif command.startswith('age_'):
        return await perform_age_search(update, context)
    elif command.startswith('loc_'):
        return await perform_location_search(update, context)
    elif command.startswith('int_'):
        return await perform_interest_search(update, context)
    elif command.startswith('changepref_'):
        return await handle_gender_preference_change(update, context)
    elif command.startswith('like_'):
        return await handle_like(update, context)
    elif command.startswith('pass_'):
        return await handle_pass(update, context)
    elif command.startswith('superlike_'):
        return await handle_super_like(update, context)

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show main menu"""
    keyboard = [
        [InlineKeyboardButton("👤 Profile ပြင်ဆင်/ဖန်တီးမည်", callback_data='create_profile')],
        [InlineKeyboardButton("❤️ မိတ်ဖက်ရှာဖွေမည်", callback_data='find_match')],
        [InlineKeyboardButton("📄 ကျွန်ုပ်၏ Profile ကြည့်မည်", callback_data='view_profile')],
        [InlineKeyboardButton("🔍 Advanced Search", callback_data='advanced_search')],
        [InlineKeyboardButton("💌 Messages", callback_data='view_messages')],
        [InlineKeyboardButton("⭐ Super Likes", callback_data='super_likes')],
        [InlineKeyboardButton("⚙️ Settings", callback_data='settings')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.message.reply_text(
        "🏠 **Main Menu**\n\nဘာလုပ်ချင်သလဲ ရွေးချယ်ပါ:",
        reply_markup=reply_markup
    )

async def reset_likes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reset user's likes to see profiles again"""
    user_id = update.effective_user.id
    
    if user_id in user_profiles:
        user_profiles[user_id]['likes_given'] = []
        await update.callback_query.message.reply_text(
            "🔄 Preferences ကို reset လုပ်ပြီးပါပြီ! အားလုံးကို ပြန်ကြည့်နိုင်ပါပြီ။"
        )
    else:
        await update.callback_query.message.reply_text("Profile မရှိသေးပါ။")

async def change_gender_preference(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Allow user to change gender preference"""
    user_id = update.effective_user.id
    
    if user_id not in user_profiles:
        await update.callback_query.message.reply_text("ရှေးဦးစွာ Profile ဖန်တီးပါ။")
        return
    
    # Show gender preference options
    keyboard = []
    for i, option in enumerate(GENDER_PREFERENCE_OPTIONS):
        keyboard.append([InlineKeyboardButton(option, callback_data=f'changepref_{i}')])
    
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data='main_menu')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    current_pref = user_profiles[user_id].get('gender_preference', 'Not set')
    await update.callback_query.message.reply_text(
        f"🏳️‍🌈 **Change Gender Preference**\n\n"
        f"လက်ရှိ: {current_pref}\n\n"
        f"အသစ်ရွေးချယ်ပါ:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_gender_preference_change(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle gender preference change"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    pref_idx = int(query.data.split('_')[1])
    
    if user_id in user_profiles:
        user_profiles[user_id]['gender_preference'] = GENDER_PREFERENCE_OPTIONS[pref_idx]
        # Also reset likes so they can see new matches
        user_profiles[user_id]['likes_given'] = []
        
        await query.message.reply_text(
            f"✅ Gender preference ကို {GENDER_PREFERENCE_OPTIONS[pref_idx]} သို့ ပြောင်းလဲပြီးပါပြီ!\n\n"
            f"🔄 Like history ကိုလည်း reset လုပ်ပေးထားပါတယ်။"
        )
        
        # Show main menu
        await show_main_menu(update, context)

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
    """User ၏ အသက်ကို လက်ခံပြီး Gender မေးသည်"""
    try:
        age = int(update.message.text)
        if 16 <= age <= 100:
            context.user_data['age'] = age
            
            # Show gender options
            keyboard = []
            for i, option in enumerate(GENDER_OPTIONS):
                keyboard.append([InlineKeyboardButton(option, callback_data=f'gender_{i}')])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "သင်၏ လိင်ကို ရွေးချယ်ပေးပါ:",
                reply_markup=reply_markup
            )
            return GENDER
        else:
            await update.message.reply_text("အသက်သည် ၁၆ နှင့် ၁၀၀ ကြားဖြစ်ရပါမည်။ ကျေးဇူးပြု၍ ပြန်ထည့်ပါ။")
            return AGE
    except ValueError:
        await update.message.reply_text("ကျေးဇူးပြု၍ နံပါတ် (ဂဏန်း) ဖြင့်သာ ထည့်သွင်းပါ။")
        return AGE

async def get_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle gender selection"""
    query = update.callback_query
    await query.answer()
    
    gender_idx = int(query.data.split('_')[1])
    context.user_data['gender'] = GENDER_OPTIONS[gender_idx]
    
    # Show gender preference options
    keyboard = []
    for i, option in enumerate(GENDER_PREFERENCE_OPTIONS):
        keyboard.append([InlineKeyboardButton(option, callback_data=f'genderpref_{i}')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(
        "သင် ဘယ်လိင်ကို ရှာဖွေချင်သလဲ?",
        reply_markup=reply_markup
    )
    return GENDER_PREFERENCE

async def get_gender_preference(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle gender preference selection"""
    query = update.callback_query
    await query.answer()
    
    pref_idx = int(query.data.split('_')[1])
    context.user_data['gender_preference'] = GENDER_PREFERENCE_OPTIONS[pref_idx]
    
    await query.message.reply_text("သင်၏ ကိုယ်ရေးမိတ်ဆက် (Bio) အတိုချုံးကို ရေးပေးပါ။")
    return BIO

async def get_bio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User ၏ Bio ကိုလက်ခံပြီး Location တောင်းသည်"""
    context.user_data['bio'] = update.message.text
    await update.message.reply_text(
        "သင့်ရဲ့ မြို့/ဒေသ ကို ပြောပြပေးပါ။ (ဥပမာ: Yangon, Mandalay)"
    )
    return LOCATION

async def get_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User ၏ Location ကိုလက်ခံပြီး Interests တောင်းသည်"""
    context.user_data['location'] = update.message.text
    
    # Create interests keyboard
    keyboard = []
    for i in range(0, len(INTERESTS_OPTIONS), 2):
        row = []
        row.append(InlineKeyboardButton(INTERESTS_OPTIONS[i], callback_data=f'interest_{i}'))
        if i + 1 < len(INTERESTS_OPTIONS):
            row.append(InlineKeyboardButton(INTERESTS_OPTIONS[i + 1], callback_data=f'interest_{i+1}'))
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("✅ ပြီးပါပြီ", callback_data='interests_done')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "သင်ကြိုက်သော အကြိုက်များကို ရွေးချယ်ပါ (၃ခု အနည်းဆုံး):",
        reply_markup=reply_markup
    )
    return INTERESTS

async def handle_interests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle interest selections"""
    query = update.callback_query
    await query.answer()
    
    if 'selected_interests' not in context.user_data:
        context.user_data['selected_interests'] = []
    
    if query.data == 'interests_done':
        if len(context.user_data['selected_interests']) < 3:
            await query.message.reply_text("အနည်းဆုံး ၃ခု ရွေးချယ်ပေးပါ။")
            return INTERESTS
        
        # Show looking for options
        keyboard = []
        for i, option in enumerate(LOOKING_FOR_OPTIONS):
            keyboard.append([InlineKeyboardButton(option, callback_data=f'looking_{i}')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            "သင် ဘာရှာနေသလဲ?",
            reply_markup=reply_markup
        )
        return LOOKING_FOR
    else:
        # Handle interest selection
        interest_idx = int(query.data.split('_')[1])
        interest = INTERESTS_OPTIONS[interest_idx]
        
        if interest in context.user_data['selected_interests']:
            context.user_data['selected_interests'].remove(interest)
        else:
            context.user_data['selected_interests'].append(interest)
        
        # Recreate the keyboard with updated selections
        keyboard = []
        for i in range(0, len(INTERESTS_OPTIONS), 2):
            row = []
            # First interest in row
            interest_text = INTERESTS_OPTIONS[i]
            if interest_text in context.user_data['selected_interests']:
                interest_text += " ✅"
            row.append(InlineKeyboardButton(interest_text, callback_data=f'interest_{i}'))
            
            # Second interest in row (if exists)
            if i + 1 < len(INTERESTS_OPTIONS):
                interest_text = INTERESTS_OPTIONS[i + 1]
                if interest_text in context.user_data['selected_interests']:
                    interest_text += " ✅"
                row.append(InlineKeyboardButton(interest_text, callback_data=f'interest_{i+1}'))
            
            keyboard.append(row)
        
        # Add done button
        selected_count = len(context.user_data['selected_interests'])
        done_text = f"✅ ပြီးပါပြီ ({selected_count}/15)"
        keyboard.append([InlineKeyboardButton(done_text, callback_data='interests_done')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        selected_text = "ရွေးချယ်ပြီး: " + ", ".join(context.user_data['selected_interests']) if context.user_data['selected_interests'] else "မရွေးချယ်ရသေးပါ"
        
        await query.edit_message_text(
            f"သင်ကြိုက်သော အကြိုက်များကို ရွေးချယ်ပါ (၃ခု အနည်းဆုံး):\n\n{selected_text}",
            reply_markup=reply_markup
        )
        return INTERESTS

async def get_looking_for(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle what user is looking for selection"""
    query = update.callback_query
    await query.answer()
    
    looking_idx = int(query.data.split('_')[1])
    context.user_data['looking_for'] = LOOKING_FOR_OPTIONS[looking_idx]
    
    await query.message.reply_text("နောက်ဆုံးအနေနဲ့ သင့်ရဲ့ Profile ဓာတ်ပုံတစ်ပုံ ပေးပို့ပါ။")
    return PHOTO

async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User ၏ ဓာတ်ပုံကို လက်ခံပြီး Profile ကို သိမ်းဆည်းသည်"""
    user_id = update.effective_user.id
    photo_file = await update.message.photo[-1].get_file()
    
    user_profiles[user_id] = {
        'name': context.user_data['name'],
        'age': context.user_data['age'],
        'gender': context.user_data['gender'],
        'gender_preference': context.user_data['gender_preference'],
        'bio': context.user_data['bio'],
        'location': context.user_data['location'],
        'interests': context.user_data['selected_interests'],
        'looking_for': context.user_data['looking_for'],
        'photo': photo_file.file_id,
        'username': update.effective_user.username,
        'super_likes_received': 0,
        'likes_given': [],
        'super_likes_given': [],
        'matches': [],
        'created_at': context.bot_data.get('current_time', 'recent')
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
        interests_text = ", ".join(profile.get('interests', []))
        
        caption = (
            f"👤 **{profile['name']}** ({profile['age']})\n"
            f"🆔 **Gender:** {profile.get('gender', 'Not specified')}\n"
            f"💖 **Looking for:** {profile.get('gender_preference', 'Not specified')}\n"
            f"📍 **Location:** {profile.get('location', 'Not specified')}\n\n"
            f"📝 **Bio:**\n{profile['bio']}\n\n"
            f"🎯 **Relationship Goal:** {profile.get('looking_for', 'Not specified')}\n"
            f"❤️ **Interests:** {interests_text}\n"
            f"⭐ **Super Likes Received:** {profile.get('super_likes_received', 0)}\n\n"
            f"📞 **Contact:** @{profile.get('username', 'N/A')}"
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
    """Enhanced matching with like/pass system and gender filtering"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    if user_id not in user_profiles:
        await context.bot.send_message(
            chat_id=chat_id, 
            text="ရှေးဦးစွာ Profile ဖန်တီးပါ။"
        )
        return ConversationHandler.END
    
    current_user = user_profiles[user_id]
    liked_users = set(current_user.get('likes_given', []))
    user_gender_pref = current_user.get('gender_preference', '💫 Everyone')
    
    # Filter by gender preference
    def matches_gender_preference(profile):
        user_gender = profile.get('gender', '')
        
        # If user wants everyone, show all
        if user_gender_pref == '💫 Everyone':
            return True
        # If user wants men, show only men
        elif user_gender_pref == '👨 Men' and user_gender == '👨 Male':
            return True
        # If user wants women, show only women  
        elif user_gender_pref == '👩 Women' and user_gender == '👩 Female':
            return True
        # If user wants non-binary, show only non-binary
        elif user_gender_pref == '🏳️‍⚧️ Non-binary' and user_gender == '🏳️‍⚧️ Non-binary':
            return True
        
        return False
    
    # Mutual gender preference check
    def mutual_gender_match(profile, profile_user_id):
        # Check if the other user's preference matches current user's gender
        other_gender_pref = profile.get('gender_preference', '💫 Everyone')
        current_gender = current_user.get('gender', '')
        
        if other_gender_pref == '💫 Everyone':
            return True
        elif other_gender_pref == '👨 Men' and current_gender == '👨 Male':
            return True
        elif other_gender_pref == '👩 Women' and current_gender == '👩 Female':
            return True
        elif other_gender_pref == '🏳️‍⚧️ Non-binary' and current_gender == '🏳️‍⚧️ Non-binary':
            return True
        
        return False
    
    available_profiles = {
        uid: prof for uid, prof in user_profiles.items() 
        if (uid != user_id and 
            uid not in liked_users and 
            matches_gender_preference(prof) and
            mutual_gender_match(prof, uid))
    }
    
    if len(available_profiles) > 0:
        random_user_id = random.choice(list(available_profiles.keys()))
        profile = available_profiles[random_user_id]
        interests_text = ", ".join(profile.get('interests', []))
        
        # Create action buttons
        keyboard = [
            [
                InlineKeyboardButton("💚 Like", callback_data=f'like_{random_user_id}'),
                InlineKeyboardButton("⭐ Super Like", callback_data=f'superlike_{random_user_id}'),
                InlineKeyboardButton("❌ Pass", callback_data=f'pass_{random_user_id}')
            ],
            [InlineKeyboardButton("🔙 Main Menu", callback_data='main_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        caption = (
            f"💕 **Potential Match!**\n\n"
            f"👤 **{profile['name']}** ({profile['age']})\n"
            f"🆔 **Gender:** {profile.get('gender', 'Not specified')}\n"
            f"📍 **Location:** {profile.get('location', 'Not specified')}\n\n"
            f"📝 **Bio:**\n{profile['bio']}\n\n"
            f"🎯 **Looking for:** {profile.get('looking_for', 'Not specified')}\n"
            f"❤️ **Interests:** {interests_text}\n\n"
            f"⭐ **Super Likes:** {profile.get('super_likes_received', 0)}"
        )
        
        await context.bot.send_photo(
            chat_id=chat_id, 
            photo=profile['photo'], 
            caption=caption, 
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    else:
        keyboard = [
            [InlineKeyboardButton("🔄 Reset Preferences", callback_data='reset_likes')],
            [InlineKeyboardButton("⚙️ Change Gender Preference", callback_data='change_gender_pref')],
            [InlineKeyboardButton("🔙 Main Menu", callback_data='main_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.send_message(
            chat_id=chat_id, 
            text="💔 သင်၏ gender preference နှင့် ကိုက်ညီတဲ့ profiles မရှိသေးပါ!\n\nPreferences ကို ပြောင်းလဲခြင်း သို့မဟုတ် reset လုပ်ခြင်းကို စဉ်းစားကြည့်ပါ။",
            reply_markup=reply_markup
        )
    return ConversationHandler.END

# --- New Features ---

async def handle_like(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular like"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    liked_user_id = int(query.data.split('_')[1])
    
    # Add to likes given
    if user_id in user_profiles:
        if 'likes_given' not in user_profiles[user_id]:
            user_profiles[user_id]['likes_given'] = []
        user_profiles[user_id]['likes_given'].append(liked_user_id)
        
        # Check if it's a match
        if (liked_user_id in user_profiles and 
            user_id in user_profiles[liked_user_id].get('likes_given', [])):
            # It's a match!
            user_profiles[user_id].setdefault('matches', []).append(liked_user_id)
            user_profiles[liked_user_id].setdefault('matches', []).append(user_id)
            
            await query.message.reply_text(
                f"🎉 **IT'S A MATCH!** 💕\n\n"
                f"သင်နှင့် {user_profiles[liked_user_id]['name']} တို့ အပြန်အလှန် ကြိုက်နှစ်သက်ကြပါတယ်!\n\n"
                f"@{user_profiles[liked_user_id].get('username', 'N/A')} ကို ဆက်သွယ်နိုင်ပါတယ်။"
            )
        else:
            await query.message.reply_text("💚 Like ပေးပြီးပါပြီ! ကြည့်ရှုခြင်းကို ဆက်လက်လုပ်ဆောင်ပါ။")
    
    # Continue to next profile
    await find_match(update, context)

async def handle_super_like(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle super like"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    super_liked_user_id = int(query.data.split('_')[1])
    
    if user_id in user_profiles:
        # Add to super likes given
        if 'super_likes_given' not in user_profiles[user_id]:
            user_profiles[user_id]['super_likes_given'] = []
        user_profiles[user_id]['super_likes_given'].append(super_liked_user_id)
        
        # Add to likes given as well
        if 'likes_given' not in user_profiles[user_id]:
            user_profiles[user_id]['likes_given'] = []
        user_profiles[user_id]['likes_given'].append(super_liked_user_id)
        
        # Increase super like count for target user
        if super_liked_user_id in user_profiles:
            user_profiles[super_liked_user_id]['super_likes_received'] = \
                user_profiles[super_liked_user_id].get('super_likes_received', 0) + 1
        
        await query.message.reply_text("⭐ Super Like ပေးပြီးပါပြီ! သူများသိရှိမည်ဖြစ်ပါတယ်။")
    
    # Continue to next profile
    await find_match(update, context)

async def handle_pass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle pass"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    passed_user_id = int(query.data.split('_')[1])
    
    if user_id in user_profiles:
        if 'likes_given' not in user_profiles[user_id]:
            user_profiles[user_id]['likes_given'] = []
        user_profiles[user_id]['likes_given'].append(passed_user_id)
    
    await query.message.reply_text("👋 Pass လုပ်ပြီးပါပြီ။")
    
    # Continue to next profile
    await find_match(update, context)

async def advanced_search_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Advanced search options"""
    keyboard = [
        [InlineKeyboardButton("🔍 By Age Range", callback_data='search_age')],
        [InlineKeyboardButton("📍 By Location", callback_data='search_location')],
        [InlineKeyboardButton("❤️ By Interests", callback_data='search_interests')],
        [InlineKeyboardButton("🔙 Back", callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.message.reply_text(
        "🔍 **Advanced Search Options:**\n\nကြိုက်တဲ့ filter ကို ရွေးချယ်ပါ:",
        reply_markup=reply_markup
    )

async def search_by_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search profiles by age range"""
    user_id = update.effective_user.id
    
    if user_id not in user_profiles:
        await update.callback_query.message.reply_text("ရှေးဦးစွာ Profile ဖန်တီးပါ။")
        return
    
    # Age range options
    keyboard = [
        [InlineKeyboardButton("18-25", callback_data='age_18_25')],
        [InlineKeyboardButton("26-35", callback_data='age_26_35')],
        [InlineKeyboardButton("36-45", callback_data='age_36_45')],
        [InlineKeyboardButton("46-60", callback_data='age_46_60')],
        [InlineKeyboardButton("60+", callback_data='age_60_plus')],
        [InlineKeyboardButton("🔙 Back", callback_data='advanced_search')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.message.reply_text(
        "🔍 **Search by Age Range:**\n\nအသက်အပိုင်းအခြားကို ရွေးချယ်ပါ:",
        reply_markup=reply_markup
    )

async def search_by_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search profiles by location"""
    user_id = update.effective_user.id
    
    if user_id not in user_profiles:
        await update.callback_query.message.reply_text("ရှေးဦးစွာ Profile ဖန်တီးပါ။")
        return
    
    # Get all unique locations from profiles
    locations = set()
    for profile in user_profiles.values():
        location = profile.get('location', '').strip()
        if location:
            locations.add(location)
    
    if not locations:
        await update.callback_query.message.reply_text(
            "📍 လက်ရှိတွင် location information ရှိသော profiles မရှိသေးပါ။"
        )
        return
    
    # Create keyboard with available locations
    keyboard = []
    for location in sorted(locations):
        keyboard.append([InlineKeyboardButton(f"📍 {location}", callback_data=f'loc_{location}')])
    
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data='advanced_search')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.message.reply_text(
        "📍 **Search by Location:**\n\nမြို့/ဒေသကို ရွေးချယ်ပါ:",
        reply_markup=reply_markup
    )

async def search_by_interests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search profiles by interests"""
    user_id = update.effective_user.id
    
    if user_id not in user_profiles:
        await update.callback_query.message.reply_text("ရှေးဦးစွာ Profile ဖန်တီးပါ။")
        return
    
    # Create keyboard with interest options
    keyboard = []
    for i in range(0, len(INTERESTS_OPTIONS), 2):
        row = []
        row.append(InlineKeyboardButton(INTERESTS_OPTIONS[i], callback_data=f'int_{i}'))
        if i + 1 < len(INTERESTS_OPTIONS):
            row.append(InlineKeyboardButton(INTERESTS_OPTIONS[i + 1], callback_data=f'int_{i+1}'))
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data='advanced_search')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.message.reply_text(
        "❤️ **Search by Interests:**\n\nအကြိုက်တစ်ခုကို ရွေးချယ်ပါ:",
        reply_markup=reply_markup
    )

async def perform_age_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Perform age-based search and show results"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    age_range = query.data.split('_')[1:]  # e.g., ['18', '25'] or ['60', 'plus']
    
    if age_range[0] == '60':
        min_age, max_age = 60, 100
    else:
        min_age, max_age = int(age_range[0]), int(age_range[1])
    
    # Filter profiles by age range (excluding current user)
    current_user = user_profiles[user_id]
    user_gender_pref = current_user.get('gender_preference', '💫 Everyone')
    
    matching_profiles = []
    for uid, profile in user_profiles.items():
        if uid == user_id:
            continue
        
        age = profile.get('age', 0)
        if min_age <= age <= max_age:
            # Also apply gender preference filtering
            if matches_gender_preference_filter(profile, user_gender_pref, current_user):
                matching_profiles.append((uid, profile))
    
    await show_search_results(update, context, matching_profiles, f"Age {min_age}-{max_age if max_age != 100 else '+'}")

async def perform_location_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Perform location-based search and show results"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    search_location = query.data.replace('loc_', '')
    
    # Filter profiles by location (excluding current user)
    current_user = user_profiles[user_id]
    user_gender_pref = current_user.get('gender_preference', '💫 Everyone')
    
    matching_profiles = []
    for uid, profile in user_profiles.items():
        if uid == user_id:
            continue
        
        profile_location = profile.get('location', '').strip()
        if profile_location.lower() == search_location.lower():
            # Also apply gender preference filtering
            if matches_gender_preference_filter(profile, user_gender_pref, current_user):
                matching_profiles.append((uid, profile))
    
    await show_search_results(update, context, matching_profiles, f"Location: {search_location}")

async def perform_interest_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Perform interest-based search and show results"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    interest_idx = int(query.data.split('_')[1])
    search_interest = INTERESTS_OPTIONS[interest_idx]
    
    # Filter profiles by interest (excluding current user)
    current_user = user_profiles[user_id]
    user_gender_pref = current_user.get('gender_preference', '💫 Everyone')
    
    matching_profiles = []
    for uid, profile in user_profiles.items():
        if uid == user_id:
            continue
        
        profile_interests = profile.get('interests', [])
        if search_interest in profile_interests:
            # Also apply gender preference filtering
            if matches_gender_preference_filter(profile, user_gender_pref, current_user):
                matching_profiles.append((uid, profile))
    
    await show_search_results(update, context, matching_profiles, f"Interest: {search_interest}")

def matches_gender_preference_filter(profile, user_gender_pref, current_user):
    """Helper function to check gender preference match"""
    user_gender = profile.get('gender', '')
    current_gender = current_user.get('gender', '')
    other_gender_pref = profile.get('gender_preference', '💫 Everyone')
    
    # Check if current user's preference matches profile's gender
    user_match = (user_gender_pref == '💫 Everyone' or
                  (user_gender_pref == '👨 Men' and user_gender == '👨 Male') or
                  (user_gender_pref == '👩 Women' and user_gender == '👩 Female') or
                  (user_gender_pref == '🏳️‍⚧️ Non-binary' and user_gender == '🏳️‍⚧️ Non-binary'))
    
    # Check if profile's preference matches current user's gender
    profile_match = (other_gender_pref == '💫 Everyone' or
                     (other_gender_pref == '👨 Men' and current_gender == '👨 Male') or
                     (other_gender_pref == '👩 Women' and current_gender == '👩 Female') or
                     (other_gender_pref == '🏳️‍⚧️ Non-binary' and current_gender == '🏳️‍⚧️ Non-binary'))
    
    return user_match and profile_match

async def show_search_results(update: Update, context: ContextTypes.DEFAULT_TYPE, matching_profiles, search_criteria):
    """Display search results"""
    if not matching_profiles:
        keyboard = [[InlineKeyboardButton("🔙 Back to Search", callback_data='advanced_search')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.message.reply_text(
            f"🔍 **Search Results for {search_criteria}:**\n\n"
            f"😔 ကိုက်ညီတဲ့ profiles မတွေ့ပါ။\n\n"
            f"တခြား search criteria ကို စမ်းကြည့်ပါ။",
            reply_markup=reply_markup
        )
        return
    
    # Show first 5 results
    results_text = f"🔍 **Search Results for {search_criteria}:**\n\n"
    results_text += f"📊 **Found {len(matching_profiles)} matches**\n\n"
    
    for i, (uid, profile) in enumerate(matching_profiles[:5]):
        interests_text = ", ".join(profile.get('interests', [])[:3])  # Show first 3 interests
        results_text += (
            f"👤 **{profile['name']}** ({profile['age']})\n"
            f"🆔 {profile.get('gender', 'Not specified')}\n"
            f"📍 {profile.get('location', 'Not specified')}\n"
            f"❤️ {interests_text}{'...' if len(profile.get('interests', [])) > 3 else ''}\n"
            f"📞 @{profile.get('username', 'N/A')}\n\n"
        )
    
    if len(matching_profiles) > 5:
        results_text += f"... နှင့် {len(matching_profiles) - 5} ဦး ထပ်ရှိသေးသည်။"
    
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Search", callback_data='advanced_search')],
        [InlineKeyboardButton("🏠 Main Menu", callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.message.reply_text(
        results_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def view_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View matches and messages"""
    user_id = update.effective_user.id
    
    if user_id not in user_profiles:
        await update.callback_query.message.reply_text("ရှေးဦးစွာ Profile ဖန်တီးပါ။")
        return
    
    matches = user_profiles[user_id].get('matches', [])
    
    if not matches:
        await update.callback_query.message.reply_text(
            "💔 သင့်မှာ matches မရှိသေးပါ။\n\nMore people ကို like ပေးပြီး matches ရယူပါ!"
        )
        return
    
    text = "💕 **Your Matches:**\n\n"
    for match_id in matches:
        if match_id in user_profiles:
            profile = user_profiles[match_id]
            text += f"👤 {profile['name']} - @{profile.get('username', 'N/A')}\n"
    
    text += "\n💬 Direct message လုပ်ရန် username ကို click လုပ်ပါ။"
    
    await update.callback_query.message.reply_text(text, parse_mode='Markdown')

async def super_likes_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Super likes information"""
    user_id = update.effective_user.id
    
    if user_id not in user_profiles:
        await update.callback_query.message.reply_text("ရှေးဦးစွာ Profile ဖန်တီးပါ။")
        return
    
    profile = user_profiles[user_id]
    super_likes_received = profile.get('super_likes_received', 0)
    super_likes_given = len(profile.get('super_likes_given', []))
    
    text = (
        f"⭐ **Super Likes Status:**\n\n"
        f"📨 **Received:** {super_likes_received}\n"
        f"📤 **Given:** {super_likes_given}\n\n"
        f"Super Likes သည် သင့်ကို အထူးအာရုံစိုက်ကြောင်း ပြသပေးပါတယ်!"
    )
    
    await update.callback_query.message.reply_text(text, parse_mode='Markdown')

async def settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Settings and preferences"""
    keyboard = [
        [InlineKeyboardButton("✏️ Edit Profile", callback_data='edit_profile')],
        [InlineKeyboardButton("🏳️‍🌈 Change Gender Preference", callback_data='change_gender_pref')],
        [InlineKeyboardButton("🔄 Reset All Likes", callback_data='reset_likes')],
        [InlineKeyboardButton("❌ Delete Profile", callback_data='delete_profile')],
        [InlineKeyboardButton("🔙 Back", callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.message.reply_text(
        "⚙️ **Settings:**\n\nဘာလုပ်ချင်သလဲ ရွေးချယ်ပါ:",
        reply_markup=reply_markup
    )


# --- Quart ASGI Application ---
app = Quart(__name__)

# Initialize Application
ptb_application = Application.builder().token(TOKEN).updater(None).build()

# ConversationHandler for profile creation
conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_profile_creation, pattern='^create_profile$')],
    states={
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
        GENDER: [CallbackQueryHandler(get_gender)],
        GENDER_PREFERENCE: [CallbackQueryHandler(get_gender_preference)],
        BIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_bio)],
        LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_location)],
        INTERESTS: [CallbackQueryHandler(handle_interests)],
        LOOKING_FOR: [CallbackQueryHandler(get_looking_for)],
        PHOTO: [MessageHandler(filters.PHOTO, get_photo)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
    per_message=False,
    per_chat=True,
    per_user=True,
)

# Register handlers
ptb_application.add_handler(CommandHandler('start', start))
ptb_application.add_handler(CallbackQueryHandler(button_handler, pattern='^(find_match|view_profile|advanced_search|view_messages|super_likes|settings|main_menu|reset_likes|change_gender_pref|search_age|search_location|search_interests)$'))
ptb_application.add_handler(CallbackQueryHandler(button_handler, pattern='^(like_|pass_|superlike_|changepref_|age_|loc_|int_)'))
ptb_application.add_handler(conv_handler)

@app.before_serving
async def startup():
    """Initialize bot before serving requests"""
    await ptb_application.initialize()
    await ptb_application.start()
    
    # Set webhook for production deployment
    if os.environ.get('RENDER') == 'true':
        webhook_url = f"https://thanlar-telegram-bot.onrender.com/{TOKEN}"
        try:
            await ptb_application.bot.set_webhook(webhook_url)
            print(f"Webhook set to: {webhook_url}")
        except Exception as e:
            print(f"Error setting webhook: {e}")

@app.after_serving
async def shutdown():
    """Cleanup on shutdown"""
    await ptb_application.stop()
    await ptb_application.shutdown()

@app.route(f'/{TOKEN}', methods=['POST'])
async def webhook_handler():
    """Handle incoming webhook updates"""
    try:
        data = await request.get_json()
        update = Update.de_json(data, ptb_application.bot)
        await ptb_application.update_queue.put(update)
        return 'ok'
    except Exception as e:
        app.logger.error(f"Error processing update: {e}")
        return 'error', 500

@app.route('/')
async def index():
    return 'Telegram Bot is running!'

@app.route('/health')
async def health():
    return 'OK', 200

if __name__ == '__main__':
    import asyncio
    port = int(os.environ.get('PORT', 5000))
    
    # For local development
    if os.environ.get('RENDER') != 'true':
        app.run(host='0.0.0.0', port=port)
    else:
        # For Render deployment, hypercorn will handle this
        pass
