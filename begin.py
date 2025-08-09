import requests
from secret import WEBHOOK_URL, BOT_TOKEN, BOT_BASE_URL

send_data = {"url": WEBHOOK_URL}
print(f"📡 Webhook URL: {send_data['url']}")

try:
    response = requests.post(url=f"{BOT_BASE_URL}/setWebhook", data=send_data)
    data = response.json()
    print(f"✅ Webhook o‘rnatildi: {data.get('description', '')}")
except Exception as e:
    print(f"❌ Webhook o‘rnatishda xatolik: {e}")


