import os
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

TOKEN = os.getenv("TOKEN")
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwPpGs3VCePvxvCDDq0CcEiFLjeP0O68LlOQx5MAuRYNESVOCAtdhNI6SkbzV6OIIhL/exec"

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hey! Send me a file and I’ll upload it to your Google Drive 😎")

# Handle files (document or photo)
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document or (update.message.photo[-1] if update.message.photo else None)

    if not file:
        await update.message.reply_text("Hmm... no file detected.")
        return

    tg_file = await file.get_file()
    file_url = f"https://api.telegram.org/file/bot{TOKEN}/{tg_file.file_path}"
    file_name = getattr(file, "file_name", "telegram_file.jpg")

    # Send to Google Apps Script
    response = requests.post(SCRIPT_URL, json={
        "file_url": file_url,
        "file_name": file_name
    })

    await update.message.reply_text(f"📁 Uploaded to Drive as: {file_name}\n\n🔗 Response: {response.text}")

# Main app runner
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_file))

    print("🤖 Bot running... Good")
    app.run_polling()

if __name__ == "__main__":
    main()
