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
    print("📴 Server to‘xtatish signali qabul qilindi.")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_stop_signal)
signal.signal(signal.SIGTERM, handle_stop_signal)

bot = Flask(__name__)

@bot.route("/health", methods=["GET"])
def health():
    return "OK", 200

@bot.route(f"/{BOT_TOKEN}", methods=["POST"])
def bot_updates():
    update = request.get_json()
    filter_message(update)
    return {"ok": True}

def ngrok_loop(url):
    send_data = {"url": url}
    print(f"📡 Webhook URL: {send_data['url']}")

    try:
        response = requests.post(url=f"{BOT_BASE_URL}/setWebhook", data=send_data)
        data = response.json()
        print(f"✅ Webhook o‘rnatildi: {data.get('description', '')}")
    except Exception as e:
        print(f"❌ Webhook o‘rnatishda xatolik: {e}")

    while not stop_flag:
        print("🔄 Ngrok loop ishlayapti...")
        time.sleep(5)

    print("⏹ Ngrok loop to‘xtadi.")

def on_startup_once():
    ngrok_object = NgrokClass()
    webhook_url = ngrok_object.webhook_url()
    threading.Thread(target=ngrok_loop, args=(webhook_url,), daemon=True).start()

def start_with_gunicorn():
    if os.environ.get("IS_MASTER_PROCESS") != "false":
        on_startup_once()

    options = {
        "bind": f"0.0.0.0:{BASE_PORT}",
        "workers": 3,  # ishlashga qarab sozlashing mumkin
    }
    FlaskGunicornApp(bot, options).run()

if __name__ == "__main__":
    os.environ["IS_MASTER_PROCESS"] = "true"
    start_with_gunicorn()
