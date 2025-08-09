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

def handle_stop_signal(signum, frame):
    global stop_flag
    stop_flag = True
    print("🛑 Server to‘xtatish signali qabul qilindi.")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_stop_signal)
signal.signal(signal.SIGTERM, handle_stop_signal)

bot = Flask(__name__)

@bot.route(f"/{BOT_TOKEN}", methods=["POST"])
def bot_updates():
    update = request.get_json()
    filter_message(update)
    return {"ok": True}

@bot.route("/health", methods=["GET"])
def health():
    return "OK", 200

def ngrok_loop(webhook_url):
    send_data = {"url": webhook_url}
    print(f"📡 Webhook URL: {send_data['url']}")

    try:
        response = requests.post(url=f"{BOT_BASE_URL}/setWebhook", data=send_data)
        data = response.json()
        print(f"✅ Webhook o‘rnatildi: {data.get('description', '')}")
    except Exception as e:
        print(f"❌ Webhook o‘rnatishda xatolik: {e}")

    global stop_flag
    while not stop_flag:
        time.sleep(5)

def start_ngrok_immediately():
    """Flask bilan parallel ravishda ngrokni ishga tushirish"""
    ngrok_object = NgrokClass()
    webhook_url = ngrok_object.webhook_url()
    ngrok_loop(webhook_url)

def start_with_gunicorn():
    if os.environ.get("IS_MASTER_PROCESS") != "false":
        threading.Thread(target=start_ngrok_immediately, daemon=True).start()

    # Gunicorn ishga tushadi, lekin ngrok keyin keladi
    options = {
        "bind": f"0.0.0.0:{BASE_PORT}",
        "workers": 1,
        "timeout": 0,  # Render restart qilmasligi uchun
    }
    FlaskGunicornApp(bot, options).run()
if __name__ == "__main__":
    os.environ["IS_MASTER_PROCESS"] = "true"
    start_with_gunicorn()
