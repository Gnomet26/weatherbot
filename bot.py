from flask import Flask, request
import threading
import requests
from secret import WEBHOOK_URL, BOT_TOKEN
from bot_utils import filter_message

print("hello")

bot = Flask(__name__)


@bot.route(f"/{BOT_TOKEN}", methods = ["POST"])
def bot_update():
    update = request.get_json()
    filter_message(update)


@bot.route("/health", methods=["GET"])
def health():
    return "OK", 200
