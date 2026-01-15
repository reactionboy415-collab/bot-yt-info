import os
import requests
import telebot
from telebot import types
from flask import Flask
from threading import Thread

# --- AUTHENTICATION & CONFIGURATION ---
# Using the token provided by the user
BOT_TOKEN = "8163888185:AAHqjYUWUJJDUC5kcZlXEjsgSyIvD8aK4xA"
API_ENDPOINT = "https://yt-data-api.onrender.com/api/fetch"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# --- RENDER HEALTH CHECK & KEEP-ALIVE ---
@app.route('/health')
def health_check():
    return "Service Operational", 200

@app.route('/')
def main_index():
    return "🔱 YT Data Master Bot is currently active.", 200

def run_web_server():
    # Render binds to a dynamic port; default to 10000 for Docker
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- KEYBOARD INTERFACES ---
def get_main_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_sample = types.InlineKeyboardButton("📺 Sample Video", url="https://youtu.be/97XtKuwWBkQ?si=0Fqf5b0_3vcWfeR2")
    btn_dev = types.InlineKeyboardButton("😎 Developer", url="https://t.me/dev2dex")
    markup.add(btn_sample, btn_dev)
    return markup

# --- BOT EVENT HANDLERS ---

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_first_name = message.from_user.first_name
    greeting = (
        f"🔱 *Greetings, {user_first_name}!*\n\n"
        "Welcome to the *YT Data Master Terminal*.\n\n"
        "I am a specialized utility designed to extract comprehensive YouTube metadata, "
        "channel analytics, and high-resolution assets directly via API.\n\n"
        "📍 *Instruction:* Please provide a valid YouTube URL to initiate data retrieval."
    )
    bot.send_message(message.chat.id, greeting, parse_mode="Markdown", reply_markup=get_main_keyboard())

@bot.message_handler(func=lambda m: "youtube.com" in m.text or "youtu.be" in m.text)
def handle_youtube_request(message):
    chat_id = message.chat.id
    # Immediate professional feedback
    status_msg = bot.send_message(chat_id, "⚙️ *Initializing extraction sequence... Please standby.*", parse_mode="Markdown")
    
    try:
        # Fetching data from the Render-hosted Python API
        response = requests.get(f"{API_ENDPOINT}?url={message.text.strip()}", timeout=30)
        json_res = response.json()

        if json_res.get("success"):
            data = json_res["data"]
            video = data["video_metadata"]
            channel = data["channel_details"]
            status = data["status"]

            # Constructing a high-fidelity professional report
            report = (
                f"🔱 *YOUTUBE METADATA REPORT*\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"🎬 *VIDEO ANALYTICS*\n"
                f"• *Title:* `{video['title']}`\n"
                f"• *Category:* {video['category']}\n"
                f"• *Duration:* {video['duration']}\n"
                f"• *Views:* {video['views']}\n"
                f"• *Published:* {video['uploaded_at']}\n\n"
                f"👤 *CHANNEL INSIGHTS*\n"
                f"• *Author:* {channel['name']}\n"
                f"• *Subscribers:* {channel['subscribers']}\n"
                f"• *Total Videos:* {channel['total_videos']}\n\n"
                f"⚖️ *SYSTEM CHECKS*\n"
                f"• *Copyright Status:* {status['copyright_free']}\n"
                f"• *Age Restricted:* {status['age_restricted']}\n"
                f"• *Privacy:* {status['privacy']}\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"🛡️ *Developer:* @dev2dex"
            )

            # Selecting the highest quality asset available
            asset_url = data["thumbnails"]["max_res"] if data["thumbnails"]["max_res"] != "N/A" else data["thumbnails"]["standard"]

            # Dispatching results with direct image injection
            bot.send_photo(chat_id, asset_url, caption=report, parse_mode="Markdown")
            bot.delete_message(chat_id, status_msg.message_id)

        else:
            bot.edit_message_text("❌ *Extraction Failure:* The provided link is either private or invalid.", chat_id, status_msg.message_id, parse_mode="Markdown")

    except Exception as error:
        bot.edit_message_text(f"⚠️ *Protocol Error:* Extraction timed out or server is unresponsive.", chat_id, status_msg.message_id, parse_mode="Markdown")

# --- INITIALIZATION ---
if __name__ == "__main__":
    print("🔱 YT Data Master Service is launching...")
    # Start the Flask server in a separate thread to satisfy Render's port binding
    Thread(target=run_web_server).start()
    # Start the bot engine
    bot.infinity_polling()
