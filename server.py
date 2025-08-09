import os
import sys
import time
import signal
import threading
import requests
from flask import Flask, request
from base_gunicorn import FlaskGunicornApp
from secret import BASE_PORT, BOT_TOKEN, BOT_BASE_URL
from bot_utils import filter_message
from ngrok_webhook import NgrokClass

stop_flag = False


# ---- Signal handling (Ctrl+C yoki SIGTERM) ----
def handle_stop_signal(signum, frame):
    global stop_flag
    stop_flag = True
    print("🛑 Server to‘xtatish signali qabul qilindi.")
    sys.exit(0)


signal.signal(signal.SIGINT, handle_stop_signal)
signal.signal(signal.SIGTERM, handle_stop_signal)


# ---- Flask app ----
bot = Flask(__name__)


@bot.route(f"/{BOT_TOKEN}", methods=["POST"])
def bot_updates():
    update = request.get_json()
    filter_message(update)
    return {"ok": True}


@bot.route("/health", methods=["GET"])
def health():
    """Render health check uchun endpoint"""
    return "OK", 200


# ---- Ngrok va webhook ishga tushirish ----
def ngrok_loop(webhook_url):
    """Webhook o‘rnatish va ngrok loop"""
    send_data = {"url": webhook_url}
    print(f"📡 Webhook URL: {send_data['url']}")

    try:
        response = requests.post(url=f"{BOT_BASE_URL}/setWebhook", data=send_data)
        data = response.json()
        print(f"✅ Webhook o‘rnatildi: {data.get('description', '')}")
    except Exception as e:
        print(f"❌ Webhook o‘rnatishda xatolik: {e}")

    # Uzluksiz ishlaydigan loop
    global stop_flag
    while not stop_flag:
        time.sleep(5)

    print("🛑 Ngrok loop to‘xtadi.")


def delayed_ngrok():
    print("ngrok uchun 10 soniya kutish")
    """Flask ishga tushgandan keyin ngrokni ishga tushirish"""
    time.sleep(10)  # Flask port ochilishi uchun biroz kutish
    ngrok_object = NgrokClass()
    webhook_url = ngrok_object.webhook_url()
    ngrok_loop(webhook_url)


# ---- Gunicorn bilan ishga tushirish ----
def start_with_gunicorn():
    # Faqat master process ngrok ishga tushirsin
    if os.environ.get("IS_MASTER_PROCESS") != "false":
        threading.Thread(target=delayed_ngrok, daemon=True).start()

    options = {
        "bind": f"0.0.0.0:{BASE_PORT}",
        "workers": 1,  # Render uchun 1 worker kifoya
    }
    FlaskGunicornApp(bot, options).run()


if __name__ == "__main__":
    os.environ["IS_MASTER_PROCESS"] = "true"
    start_with_gunicorn()
