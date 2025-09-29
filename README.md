# 💕 Thanlar Dating Bot - Complete Telegram Dating Platform

A fully-featured Telegram dating bot built with Python, offering comprehensive dating functionality including profile creation, gender-based matching, super likes, and advanced search capabilities.

## 🌟 Features

### 👤 **Enhanced Profile Creation**
- **Personal Information**: Name, age, bio, location
- **Gender & Preferences**: 4 gender options with smart preference matching
- **Interests Selection**: 15+ interest categories to choose from
- **Relationship Goals**: Define what you're looking for
- **Photo Upload**: Profile pictures with validation

### 💕 **Smart Matching System**
- **Gender-Based Filtering**: Mutual gender preference matching
- **Like/Pass/Super Like**: Three interaction types for better engagement
- **Instant Match Detection**: Real-time notifications when mutual interest occurs
- **Daily Limits**: 50 regular likes, 5 super likes per day to encourage regular usage

### 🔍 **Advanced Features**
- **Advanced Search**: Filter by age, location, interests, gender
- **Messaging System**: View matches and contact information
- **Super Likes System**: Premium interaction with visibility boost
- **Settings Management**: Change preferences, reset likes, profile editing
- **Myanmar Language**: Fully localized for Myanmar users

### 📊 **User Engagement**
- **Statistics Tracking**: Super likes received counter
- **Daily Usage Limits**: Gamification to drive retention
- **Reset Functionality**: Allow users to re-see profiles
- **Match Notifications**: Instant feedback system

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/AungYeZawDev/telegram_bot.git
   cd telegram_bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**
   ```bash
   export TELEGRAM_TOKEN="your_bot_token_here"
   ```

4. **Run locally**
   ```bash
   python app.py
   ```

5. **Access your bot**
   - Open Telegram and search for your bot
   - Send `/start` to begin

## 🌐 Deployment

### Render.com (Recommended)

1. **Fork this repository**

2. **Create new Web Service on Render**
   - Connect your GitHub repository
   - Use the following settings:
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `hypercorn app:app --bind 0.0.0.0:$PORT`

3. **Set Environment Variables**
   ```
   TELEGRAM_TOKEN=your_bot_token_here
   RENDER=true
   ```

4. **Deploy**
   - Render will automatically deploy your bot
   - Webhook will be set to: `https://your-app-name.onrender.com/{TOKEN}`

### Other Platforms

The bot is compatible with any platform supporting Python web applications:
- Heroku
- Railway
- DigitalOcean App Platform
- AWS Elastic Beanstalk

## 📋 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `TELEGRAM_TOKEN` | Your Telegram Bot Token | Yes | None |
| `PORT` | Server port | No | 5000 |
| `RENDER` | Production deployment flag | No | false |

### Customization Options

#### Interest Categories
Edit `INTERESTS_OPTIONS` in `app.py`:
```python
INTERESTS_OPTIONS = [
    "🎵 Music", "🎬 Movies", "📚 Reading", "🏃 Sports", "🍳 Cooking", 
    "✈️ Travel", "🎮 Gaming", "🎨 Art", "💃 Dancing", "📸 Photography",
    # Add more interests...
]
```

#### Daily Limits
Adjust usage limits:
```python
DAILY_LIKES_LIMIT = 50
DAILY_SUPER_LIKES_LIMIT = 5
```

#### Gender Options
Modify gender and preference options:
```python
GENDER_OPTIONS = [
    "👨 Male", "👩 Female", "🏳️‍⚧️ Non-binary", "❓ Prefer not to say"
]

GENDER_PREFERENCE_OPTIONS = [
    "👨 Men", "👩 Women", "🏳️‍⚧️ Non-binary", "💫 Everyone"
]
```

## 🏗️ Architecture

### Technology Stack
- **Backend**: Python 3.8+
- **Web Framework**: Quart (Async Flask)
- **Telegram API**: python-telegram-bot 20.8
- **ASGI Server**: Hypercorn
- **Deployment**: Render.com

### Project Structure
```
telegram_bot/
├── app.py                 # Main application file
├── requirements.txt       # Python dependencies
├── render.yaml           # Render deployment config
├── README.md             # This file
└── .github/
    └── copilot-instructions.md  # AI coding guidelines
```

### Data Flow
1. **User starts** with `/start` → Main menu display
2. **Profile creation** → Multi-step conversation flow
3. **Find matches** → Gender-filtered random selection
4. **Like/Pass/Super Like** → Interaction tracking
5. **Match detection** → Mutual like notifications
6. **Webhook handling** → Quart processes Telegram updates

## 🔧 Development

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run with auto-reload
python app.py

# Bot will be available at http://localhost:5000
# Use ngrok for webhook testing: ngrok http 5000
```

### Adding New Features

1. **New Menu Options**: Extend `start()` function keyboard
2. **Profile Fields**: Add conversation states and update data structure
3. **Matching Logic**: Modify `find_match()` function algorithms
4. **Search Filters**: Extend `advanced_search_menu()` options

### Database Integration

For production use, replace in-memory storage:

```python
# Current: In-memory dictionaries
user_profiles = {}

# Recommended: Database integration
# - MongoDB for document storage
# - PostgreSQL for relational data
# - Redis for session management
```

## 📊 User Guide

### For Users

1. **Getting Started**
   - Send `/start` to the bot
   - Create your profile with photos and interests
   - Set your gender and preferences

2. **Finding Matches**
   - Use "မိတ်ဖက်ရှာဖွေမည်" to browse profiles
   - Like, Super Like, or Pass on profiles
   - Get instant notifications for matches

3. **Advanced Features**
   - Use Advanced Search for specific criteria
   - Check Messages for your matches
   - Manage preferences in Settings

### Profile Creation Flow
1. Name → Age → Gender → Gender Preference
2. Bio → Location → Interests → Relationship Goals
3. Photo Upload → Profile Complete

## 🛡️ Privacy & Security

### Data Handling
- **In-Memory Storage**: Current implementation (development)
- **No Data Persistence**: Profiles reset on server restart
- **User Privacy**: Only displays public Telegram usernames
- **Myanmar Compliance**: All text in Myanmar language

### Security Considerations
- Bot token should be environment variable only
- Implement rate limiting for production
- Consider data encryption for sensitive information
- Regular security audits recommended

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📞 Support

### Issues & Bugs
- Create issue on [GitHub Issues](https://github.com/AungYeZawDev/telegram_bot/issues)
- Include error logs and reproduction steps

### Feature Requests
- Use GitHub Issues with `enhancement` label
- Describe use case and expected behavior

### Contact
- **Developer**: [@AungYeZawDev](https://github.com/AungYeZawDev)
- **Telegram**: [@aungyezaw](https://t.me/aungyezaw)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Telegram Bot API wrapper
- [Quart](https://github.com/pallets/quart) - Async web framework
- [Render.com](https://render.com) - Deployment platform
- Myanmar Unicode fonts for proper text display

## 🔮 Roadmap

### Version 2.0 Features
- [ ] Database integration (MongoDB/PostgreSQL)
- [ ] Real-time messaging system
- [ ] Photo verification system
- [ ] Location-based matching with maps
- [ ] Video call integration
- [ ] Premium subscription features
- [ ] Admin dashboard
- [ ] Analytics and insights
- [ ] Multi-language support
- [ ] Push notifications

### Business Features
- [ ] Monetization options (premium features)
- [ ] Advertisement integration
- [ ] Partnership programs
- [ ] User verification badges
- [ ] Advanced matching algorithms
- [ ] AI-powered recommendations

---

**Made with ❤️ in Myanmar** | **Built for the Myanmar Dating Community**

> Transform your Telegram into a complete dating platform! 🚀
