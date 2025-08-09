from flask import Flask, request
import threading
import requests
from secret import WEBHOOK_URL, BOT_TOKEN
from bot_utils import filter_message

print("hello")

bot = Flask(__name__)


@bot.route(f"/{BOT_TOKEN}", methods=["POST"])
def bot_updates():
    try:
        update = request.get_json(force=True, silent=True)
        if not update:
            return {"ok": False, "error": "Empty request"}, 400
        filter_message(update)
        return {"ok": True}, 200
    except Exception as e:
        print(f"❌ Xatolik: {e}")
        return {"ok": False, "error": str(e)}, 500



@bot.route("/health", methods=["GET"])
def health():
    return "OK", 200
