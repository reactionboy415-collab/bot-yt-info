import os
import requests
import telebot
from telebot import types
from flask import Flask
from threading import Thread
import io

# --- CONFIGURATION ---
BOT_TOKEN = "8163888185:AAGPXuJJ__xGZUqZkCFVp43cSmU0s900Dmo"
YT_API = "https://yt-data-api-ccjp.onrender.com/api/fetch"
IG_API = "https://chiragopisthebest.vercel.app/api/analyze"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# --- WEB SERVER (For Render/Vercel) ---
@app.route('/')
def main_index(): return "🔱 Overpowered Multi-Bot Active.", 200

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- NAVIGATION KEYBOARDS ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("📺 YouTube Info", "📸 Instagram Info", "😎 Developer")
    return markup

def inline_dev():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔱 Support Group", url="https://t.me/dex4dev"))
    return markup

# --- START COMMAND ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id, 
        f"🔱 *Welcome to the Data Master Terminal, {message.from_user.first_name}!*\n\n"
        "I am an overpowered utility to extract every single detail from IG and YT.",
        parse_mode="Markdown", 
        reply_markup=main_menu()
    )

# --- INSTAGRAM OVERPOWERED HANDLER ---
@bot.message_handler(func=lambda m: m.text == "📸 Instagram Info")
def ig_start(message):
    bot.send_message(message.chat.id, "📍 *Send the Instagram Username (without @):*", parse_mode="Markdown")

@bot.message_handler(func=lambda m: not ("youtube.com" in m.text or "youtu.be" in m.text) and len(m.text) < 30 and m.text not in ["📺 YouTube Info", "📸 Instagram Info", "😎 Developer"])
def handle_ig(message):
    chat_id = message.chat.id
    username = message.text.strip().replace('@', '')
    status = bot.send_message(chat_id, "⚙️ *Bypassing IG Security...*", parse_mode="Markdown")
    
    try:
        res = requests.get(f"{IG_API}?username={username}", timeout=25).json()
        if res.get("success"):
            p = res["data"]["profile"]
            # 🔱 Full Profile Report
            report = (
                f"🔱 *IG DEEP-SCAN REPORT*\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 *Full Name:* `{p['full_name']}`\n"
                f"🆔 *Username:* `@{username}`\n"
                f"📊 *Followers:* `{p['followers']:,}`\n"
                f"📉 *Following:* `{p['following']:,}`\n"
                f"📸 *Total Posts:* `{p.get('posts', 'N/A')}`\n"
                f"📝 *Bio:* `{p['bio']}`\n"
                f"🔒 *Private:* `{p['is_private']}`\n"
                f"✅ *Verified:* `{p.get('verified', False)}`\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"🛡️ *Developer:* @dex4dev"
            )
            
            # Send HD Profile Pic as File
            pic = requests.get(p['profile_pic']).content
            bot.send_photo(chat_id, io.BytesIO(pic), caption=report, parse_mode="Markdown")

            # Send Top 3 Media with full stats
            for item in res["data"]["media"][:3]:
                media_bytes = requests.get(item['preview']).content
                caption = (
                    f"🔗 [Post Link]({item['url']})\n"
                    f"❤️ Likes: `{item['likes']:,}` | 📺 Views: `{item.get('views', 0):,}`"
                )
                bot.send_photo(chat_id, io.BytesIO(media_bytes), caption=caption, parse_mode="Markdown")
            
            bot.delete_message(chat_id, status.message_id)
        else:
            bot.edit_message_text("❌ *Error:* Username invalid or server blocked.", chat_id, status.message_id)
    except:
        bot.edit_message_text("⚠️ *Critical Failure:* API Unresponsive.", chat_id, status.message_id)

# --- YOUTUBE OVERPOWERED HANDLER ---
@bot.message_handler(func=lambda m: m.text == "📺 YouTube Info")
def yt_start(message):
    bot.send_message(message.chat.id, "📍 *Send the YouTube Video URL:*", parse_mode="Markdown")

@bot.message_handler(func=lambda m: "youtube.com" in m.text or "youtu.be" in m.text)
def handle_yt(message):
    chat_id = message.chat.id
    status = bot.send_message(chat_id, "⚙️ *Extracting YT Metadata...*", parse_mode="Markdown")
    
    try:
        res = requests.get(f"{YT_API}?url={message.text.strip()}", timeout=30).json()
        if res.get("success"):
            v = res["data"]["video_metadata"]
            c = res["data"]["channel_details"]
            s = res["data"]["status"]
            
            # 🔱 Full YouTube Report
            report = (
                f"🔱 *YT DEEP-SCAN REPORT*\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"🎬 *Video Title:* `{v['title']}`\n"
                f"⏱️ *Duration:* `{v['duration']}`\n"
                f"👁️ *Views:* `{v['views']}`\n"
                f"📅 *Published:* `{v['uploaded_at']}`\n"
                f"📂 *Category:* `{v['category']}`\n\n"
                f"👤 *Channel:* `{c['name']}`\n"
                f"👥 *Subscribers:* `{c['subscribers']}`\n"
                f"🎥 *Total Videos:* `{c['total_videos']}`\n\n"
                f"⚖️ *System Checks:*\n"
                f"• Copyright Free: `{s['copyright_free']}`\n"
                f"• Privacy: `{s['privacy']}`\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"🛡️ *Developer:* @dev2dex"
            )
            
            # Max-res thumbnail
            thumb_url = res["data"]["thumbnails"]["max_res"] if res["data"]["thumbnails"]["max_res"] != "N/A" else res["data"]["thumbnails"]["standard"]
            bot.send_photo(chat_id, thumb_url, caption=report, parse_mode="Markdown")
            bot.delete_message(chat_id, status.message_id)
        else:
            bot.edit_message_text("❌ *Error:* Failed to fetch YT data.", chat_id, status.message_id)
    except:
        bot.edit_message_text("⚠️ *Critical Failure:* YT API Offline.", chat_id, status.message_id)

@bot.message_handler(func=lambda m: m.text == "😎 Developer")
def show_dev(message):
    bot.send_message(message.chat.id, "🔱 *Engineers:* @dev2dex & @dex4dev", reply_markup=inline_dev())

# --- LAUNCH ---
if __name__ == "__main__":
    print("🚀 Overpowered Bot Launching...")
    Thread(target=run_web_server).start()
    bot.infinity_polling()
