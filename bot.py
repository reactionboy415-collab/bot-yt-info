import os
import requests
import telebot
from telebot import types
from flask import Flask
from threading import Thread
import io

# --- AUTHENTICATION & CONFIGURATION ---
BOT_TOKEN = "8163888185:AAGPXuJJ__xGZUqZkCFVp43cSmU0s900Dmo"
YT_API_ENDPOINT = "https://yt-data-api-ccjp.onrender.com/api/fetch"
IG_API_ENDPOINT = "https://chiragopisthebest.vercel.app/api/analyze"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# --- RENDER HEALTH CHECK ---
@app.route('/health')
def health_check():
    return "Service Operational", 200

@app.route('/')
def main_index():
    return "🔱 YT & IG Data Master Bot is currently active.", 200

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- KEYBOARD INTERFACES ---

def get_main_reply_keyboard():
    """Under-keyboard buttons for navigation"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_yt = types.KeyboardButton("📺 Youtube Video Info")
    btn_ig = types.KeyboardButton("📸 Instagram ID INFO")
    btn_dev = types.KeyboardButton("😎 Developer")
    markup.add(btn_yt, btn_ig, btn_dev)
    return markup

def get_inline_dev_keyboard():
    """Inline buttons for social links"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_sample = types.InlineKeyboardButton("📺 Sample Video", url="https://youtu.be/97XtKuwWBkQ")
    btn_dev = types.InlineKeyboardButton("😎 Main Developer", url="https://t.me/dev2dex")
    btn_api = types.InlineKeyboardButton("🔱 API Support", url="https://t.me/dex4dev")
    markup.add(btn_sample, btn_dev, btn_api)
    return markup

# --- BOT EVENT HANDLERS ---

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_first_name = message.from_user.first_name
    greeting = (
        f"🔱 *Greetings, {user_first_name}!*\n\n"
        "Welcome to the *Ultimate Data Extraction Terminal*.\n\n"
        "Select a service from the menu below to initiate the extraction sequence."
    )
    bot.send_message(
        message.chat.id, 
        greeting, 
        parse_mode="Markdown", 
        reply_markup=get_main_reply_keyboard()
    )

# --- NAVIGATION HANDLERS ---

@bot.message_handler(func=lambda m: m.text == "😎 Developer")
def handle_dev_info(message):
    bot.send_message(
        message.chat.id, 
        "🔱 *Developer Intelligence Profile:*\n\n"
        "• *Lead Coder:* @dev2dex\n"
        "• *API Architect:* @dex4dev\n"
        "• *Project:* IG & YT Intelligence System",
        parse_mode="Markdown",
        reply_markup=get_inline_dev_keyboard()
    )

@bot.message_handler(func=lambda m: m.text == "📺 Youtube Video Info")
def prompt_youtube(message):
    bot.send_message(message.chat.id, "📍 *Protocol:* Please provide a valid YouTube URL.", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📸 Instagram ID INFO")
def prompt_instagram(message):
    bot.send_message(message.chat.id, "📍 *Protocol:* Please send the Instagram Username (e.g., `cristiano`).", parse_mode="Markdown")

# --- INSTAGRAM DATA EXTRACTION (NEW FEATURE) ---

@bot.message_handler(func=lambda m: not ("youtube.com" in m.text or "youtu.be" in m.text or "/" in m.text or m.text in ["📺 Youtube Video Info", "📸 Instagram ID INFO", "😎 Developer"]))
def handle_instagram_request(message):
    chat_id = message.chat.id
    username = message.text.strip().replace('@', '')
    
    status_msg = bot.send_message(chat_id, "⚙️ *Accessing Instagram Infrastructure...*", parse_mode="Markdown")
    
    try:
        # Calling your Vercel FastAPI
        response = requests.get(f"{IG_API_ENDPOINT}?username={username}", timeout=25)
        res_data = response.json()

        if res_data.get("success"):
            profile = res_data["data"]["profile"]
            media_list = res_data["data"]["media"]

            report = (
                f"🔱 *INSTAGRAM INTELLIGENCE REPORT*\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 *Identity:* `{profile['full_name']}`\n"
                f"📊 *Followers:* `{profile['followers']:,}`\n"
                f"📉 *Following:* `{profile['following']:,}`\n"
                f"📝 *Bio:* {profile['bio'] or 'No bio provided'}\n"
                f"🔒 *Privacy:* {'Restricted' if profile['is_private'] else 'Open Source'}\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"🛡️ *Developer:* @dex4dev"
            )

            # 1. Download & Send Profile Pic (Native File)
            pic_content = requests.get(profile['profile_pic']).content
            bot.send_photo(chat_id, io.BytesIO(pic_content), caption=report, parse_mode="Markdown")

            # 2. Fetch Latest Media Previews (Top 2 for performance)
            if media_list:
                bot.send_message(chat_id, "🎬 *Extracting Latest Media Files...*", parse_mode="Markdown")
                for item in media_list[:2]:
                    media_content = requests.get(item['preview']).content
                    bot.send_photo(
                        chat_id, 
                        io.BytesIO(media_content), 
                        caption=f"🔗 [Native Post Link]({item['url']})\n❤️ Likes: {item['likes']:,}", 
                        parse_mode="Markdown"
                    )

            bot.delete_message(chat_id, status_msg.message_id)
        else:
            bot.edit_message_text("❌ *Error:* Profile unreachable or non-existent.", chat_id, status_msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"⚠️ *Protocol Error:* API extraction timed out or refused connection.", chat_id, status_msg.message_id)

# --- YOUTUBE DATA EXTRACTION (RETAINED) ---

@bot.message_handler(func=lambda m: "youtube.com" in m.text or "youtu.be" in m.text)
def handle_youtube_request(message):
    chat_id = message.chat.id
    status_msg = bot.send_message(chat_id, "⚙️ *Initializing YT extraction sequence...*", parse_mode="Markdown")
    
    try:
        response = requests.get(f"{YT_API_ENDPOINT}?url={message.text.strip()}", timeout=30)
        json_res = response.json()

        if json_res.get("success"):
            video = json_res["data"]["video_metadata"]
            channel = json_res["data"]["channel_details"]
            
            report = (
                f"🔱 *YOUTUBE METADATA REPORT*\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"🎬 *Title:* `{video['title']}`\n"
                f"👤 *Author:* {channel['name']}\n"
                f"📊 *Views:* {video['views']}\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"🛡️ *Developer:* @dev2dex"
            )

            asset_url = json_res["data"]["thumbnails"]["max_res"] if json_res["data"]["thumbnails"]["max_res"] != "N/A" else json_res["data"]["thumbnails"]["standard"]
            bot.send_photo(chat_id, asset_url, caption=report, parse_mode="Markdown")
            bot.delete_message(chat_id, status_msg.message_id)

        else:
            bot.edit_message_text("❌ *Extraction Failure:* Link invalid or private.", chat_id, status_msg.message_id)

    except Exception:
        bot.edit_message_text("⚠️ *Protocol Error:* YouTube server unresponsive.", chat_id, status_msg.message_id)

# --- INITIALIZATION ---
if __name__ == "__main__":
    print("🔱 Multi-Utility Data Bot is launching...")
    Thread(target=run_web_server).start()
    bot.infinity_polling()
