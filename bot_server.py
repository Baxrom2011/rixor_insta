from flask import Flask
import threading
import telebot

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "salom bot ishlayapti", 200

# ======================================
# BOT
TOKEN = "8452951891:AAFCy6LS3ARtl0WGgfyrWLZ5O8Qik8SIZO0"

bot = telebot.TeleBot(TOKEN)
# ======================================
# Botni kodlari


import instaloader
import os
from telebot import types
from moviepy import VideoFileClip
import uuid
import shutil



bot = telebot.TeleBot(TOKEN)

loader = instaloader.Instaloader(
    download_comments=False,
    download_geotags=False,
    download_pictures=False,
    download_video_thumbnails=False,
    save_metadata=False
)

video_file = None
folder_name = None


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🎥 Salom!\nAgar siz Instagram videongizning linkini tashlasangiz, biz sizga o‘sha videoni va audiosini yuklab beramiz — hech qanday reklamasiz! 🚫📲\n\nAgar siz bizning botimizni stories’da reklama qilsangiz va mening profilimni — @811.lvl — belgilasangiz,\nva sizning videongiz 25+ ta ko‘rish to‘plasa 👀,\nsizga 💸 10 000 so‘m beramiz! 😍🔥")


@bot.message_handler(func=lambda message: True)
def get_instagram_video(message):
    global video_file, folder_name
    url = message.text.strip()

    try:
        shortcode = url.split("/")[-2]
        folder_name = shortcode
    except IndexError:
        bot.reply_to(message, "Bu link instagram linki emas yoki noto'g'ri tashladingiz")
        return

    loader_message = bot.send_message(message.chat.id, "video yuklanyapti...")

    try:
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        loader.download_post(post, target=shortcode)

        for file in os.listdir(shortcode):
            if file.endswith(".mp4"):
                video_file = os.path.join(shortcode, file)
                break

        if video_file:
            with open(video_file, "rb") as video:
                markup = types.InlineKeyboardMarkup()
                btn1 = types.InlineKeyboardButton("Audiosi kerak", callback_data="get_audio")
                markup.add(btn1)
                bot.send_video(message.chat.id, video, reply_markup=markup)
            bot.delete_message(message.chat.id, loader_message.message_id)
        else:
            bot.delete_message(message.chat.id, loader_message.message_id)
            bot.reply_to(message, "video topilmadi")

    except Exception as e:
        bot.delete_message(message.chat.id, loader_message.message_id)
        bot.reply_to(message, f"xatoli: {e}")


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global video_file, folder_name
    if call.data == "get_audio":
        try:
            bot.send_message(call.message.chat.id, "audio yuklanyapti...")

            video = VideoFileClip(video_file)
            audio = video.audio
            audio_name = f"{uuid.uuid4()}.mp3"
            audio.write_audiofile(audio_name)
            video.close()

            with open(audio_name, "rb") as audio_:
                bot.send_audio(call.message.chat.id, audio_)
            os.remove(audio_name)

        except Exception as e:
            bot.reply_to(call.message, f"audio yuklashda xatolik: {e}")
        finally:
            if os.path.exists(folder_name):
                shutil.rmtree(folder_name, ignore_errors=True)

# ======================================
#  Botni va Serverni ishga tushrsh

def run_bot():
    bot.polling(non_stop=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=5000, debug=True)
