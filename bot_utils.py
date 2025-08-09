
import json
import requests
import threading
from secret import BOT_BASE_URL, BACKENT_BASE_URL
from register_user_kesh import (
    init_user, get_user_state, set_user_state,
    update_user_data, get_user_data, clear_user
)

from psql.db import engine, metadata, SessionLocal
from sqlalchemy.engine import reflection
from psql.Users import User

inspector = reflection.Inspector.from_engine(engine)
tables = inspector.get_table_names()

if 'user_list' not in tables:
    metadata.create_all(bind=engine)
    print("✅ user_list jadvali yaratildi.")
else:
    print("✅ user_list jadvali allaqachon mavjud.")


def register_request(url, data, chat_id):
    response = requests.post(url = url, data = data)
    if str(response.status_code) == "201":
        db = SessionLocal()
        new_user = User(
            id=chat_id,
            access_token=None,
            refresh_token=None,
        )
        db.add(new_user)
        db.commit()
        db.close()
        send_message(chat_id, response.json()['message'])
    else:
        send_message(chat_id, response.json()['error'][0])

def login_request(url, data, chat_id):
    response = requests.post(url = url, data = data)
    if str(response.status_code) == "200":
        db = SessionLocal()
        user = db.query(User).filter(User.id == chat_id).first()
        if user:
            user.access_token = response.json()['access_token']
            user.refresh_token = response.json()['refresh_token']
            db.commit()
        db.close()
        send_message(chat_id, "Tizimga kirdingiz")
    else:
        send_message(chat_id, response.json()['error'][0])


def logout_request(url, headers, data, chat_id):
    response = requests.post(url = url, headers=headers, data = data)
    if str(response.status_code) == "205":
        db = SessionLocal()
        user = db.query(User).filter(User.id == chat_id).first()
        if user:
            user.access_token = None
            user.refresh_token = None
            db.commit()
        db.close()
        send_message(chat_id, "Tizimdan muvoffaqiyatli chiqdingiz")
    else:
        send_message(chat_id, response.json()['detail'])

def refresh_token():
    pass

def set_city(chat_id, url, headers, payload):
    response = requests.post(url = url, headers = headers, data = payload)
    if response.status_code == 201:
        send_message(chat_id, f"{response.json()['city_name']} shahri o'rnatildi")


def weather(url, chat_id, headers, name = None):

    if name is None:
        r = requests.get(url = url, headers = headers)
        if r.status_code == 200:
            data = r.json()
            message = f"""
            📍 Shahar: {data['city_name']}, {data['country_code']}

🌤 Ob-havo: {data['weather_main']} — {data['weather_description'].capitalize()}
🌡 Harorat: {data['temperature']}°C
🤗 Sezilishicha: {data['feels_like']}°C
💧 Namlik: {data['humidity']}%
🌬 Shamol tezligi: {data['wind_speed']} m/s, yo'nalishi: {data['wind_deg']}°

☁ Bulutlilik: {data['clouds']}%
👁 Ko‘rinish: {data['visibility']} metr
📈 Bosim: {data['pressure']} hPa

🌅 Quyosh chiqishi: {data['sunrise'][11:16]}
🌇 Quyosh botishi: {data['sunset'][11:16]}

🕒 Ma’lumot vaqti: {data['timestamp'][11:16]} (mahalliy vaqt)"""
            send_message(chat_id, message)
        elif r.status_code == 404:
            data = r.json()
            send_message(chat_id, data['error'])
    else:
        final_url = url+name
        r = requests.get(url = final_url, headers = headers)
        if r.status_code == 200:
            data = r.json()
            message = f"""
            📍 Shahar: {data['city_name']}, {data['country_code']}

🌤 Ob-havo: {data['weather_main']} — {data['weather_description'].capitalize()}
🌡 Harorat: {data['temperature']}°C
🤗 Sezilishicha: {data['feels_like']}°C
💧 Namlik: {data['humidity']}%
🌬 Shamol tezligi: {data['wind_speed']} m/s, yo'nalishi: {data['wind_deg']}°

☁ Bulutlilik: {data['clouds']}%
👁 Ko‘rinish: {data['visibility']} metr
📈 Bosim: {data['pressure']} hPa"""
            send_message(chat_id, message)
        elif r.status_code == 404:
            send_message(chat_id, "Bunday shahar topilmadi")


def thread_send_message(chat_id, text_message):
    base_url = f"{BOT_BASE_URL}/sendMessage"
    payload = {"chat_id": str(chat_id), "text": str(text_message), "parse_mode": "HTML"}
    headers = {"Content-Type": "application/json"}
    requests.post(url = base_url, data = json.dumps(payload), headers = headers)




def send_message(chat_id, text_message):
    threading.Thread(target = lambda: thread_send_message(chat_id, text_message)).start()


def cancel_register(chat_id):
    user_id = chat_id
    clear_user(user_id)
    send_message(chat_id, "❌ Jarayon bekor qilindi. Istasangiz /start bilan qayta boshlang.")

def handler_registration(chat_id, message, update):

    user_id = chat_id
    state = get_user_state(user_id)
    text = message

    if not state:
        send_message(chat_id, "Iltimos, /register buyrug‘ini bosing.")
        return

    if state == "waiting_for_username":
        update_user_data(user_id, "username", text)
        set_user_state(user_id, "waiting_for_first_name")
        send_message(chat_id, "📛 Ismingizni kiriting:\n\nRegistratsiyani to'xtatish uchun /cancel ni yuboring")
    elif state == "waiting_for_first_name":
        update_user_data(user_id, "first_name", text)
        set_user_state(user_id, "waiting_for_last_name")
        send_message(chat_id, "👪 Familiyangizni kiriting:\n\nRegistratsiyani to'xtatish uchun /cancel ni yuboring")
    elif state == "waiting_for_last_name":
        update_user_data(user_id, "last_name", text)
        set_user_state(user_id, "waiting_for_password")
        send_message(chat_id, "🔑 Parol kiriting:\n\nRegistratsiyani to'xtatish uchun /cancel ni yuboring")
    elif state == "waiting_for_password":
        update_user_data(user_id, "password", text)

        data = get_user_data(user_id)
        resp = None
        threading.Thread(target = lambda: register_request(url = f"{BACKENT_BASE_URL}/v1/auth/register/", data = data, chat_id = chat_id)).start()
        clear_user(user_id)

    elif state == "waiting_for_login_username":
        update_user_data(user_id, "username", text)
        set_user_state(user_id, "waiting_for_login_password")
        send_message(user_id, "🔑 Parolingizni kiriting: ")

    elif state == "waiting_for_login_password":
        update_user_data(user_id, "password", text)
        data = get_user_data(user_id)
        threading.Thread(target = lambda: login_request(url = f"{BACKENT_BASE_URL}/v1/auth/login/", data = data, chat_id = chat_id)).start()
        clear_user(user_id)

def commands(chat_id, command, update):
    command = command.split()
    size = len(command)
    comd = ""
    data = ""
    if size > 1:
        comd = command[0]
        del command[0]
        for i in command:
            data += (i + " ")
    else:
        comd = command[0]
    command_list = ["/start", "/help", "/setcity", "/weather", "/register", "/login", "/logout", "/cancel"]
    if comd in command_list:
        pass
    else:
        send_message(chat_id, "Bunday buyruq mavjud emas, ma'lumot uchun /help dan foydalaning")
        return 1

    if comd == "/start" and size == 1:
        db = SessionLocal()
        user = db.query(User).filter(User.id == chat_id).first()

        if not user:
             send_message(chat_id,"👋 Xush kelibsiz! Siz hali ro'yxatdan o'tmagansiz. Iltimos, /register buyrug'ini bosing.")
        elif not user.access_token:
            send_message(chat_id,"👋 Salom! Iltimos, tizimga kirish uchun /login buyrug'ini bosing.")
        else:
            send_message(chat_id,"✅ Xush kelibsiz, siz tizimga kirgansiz. Davom etishingiz mumkin./help orqali barcha ma'lumotlarni ko'ring")

        db.close()
    elif comd == "/help" and size == 1:
        message = f"""
🌀 <b>Botdan foydalanish qo‘llanmasi</b>

/register – 📝 Ro‘yxatdan o‘tish. Ismingiz, telefon raqamingiz va parolingizni kiriting.

/login – 🔐 Tizimga kirish (ro‘yxatdan o‘tgandan so‘ng).

/setcity <i>shahar_nomi</i> – 🏙 Profilingizga bitta shahar tanlang.
Misol: <code>/setcity Andijon</code>

/weather – 🌤 Profilingizda tanlangan shahar bo‘yicha ob-havo ma’lumotini ko‘rsatadi.

/weather <i>shahar_nomi</i> – 🌍 Istalgan shahar bo‘yicha ob-havo ma’lumotini ko‘rsatadi.
Misol: <code>/weather Samarqand</code>

/logout – 🚪 Tizimdan chiqish (profilingizdan log out qilish).
"""
        send_message(chat_id, message)

    elif comd == "/setcity" and size > 1:
        db = SessionLocal()
        user = db.query(User).filter(User.id == chat_id).first()

        if not user:
             send_message(chat_id,"👋 Xush kelibsiz! Siz hali ro'yxatdan o'tmagansiz. Iltimos, /register buyrug'ini bosing.")
        elif not user.access_token:
            send_message(chat_id,"👋 Salom! Iltimos, tizimga kirish uchun /login buyrug'ini bosing.")
        else:
            headers = {"Authorization": f"Bearer {user.access_token}"}
            payload = {"city_name": data}
            url = f"{BACKENT_BASE_URL}/v1/users/city/"
            set_city(chat_id = chat_id, url = url, headers = headers, payload = payload)

    elif comd == "/weather" and size == 1:
        db = SessionLocal()
        user = db.query(User).filter(User.id == chat_id).first()

        if not user:
             send_message(chat_id,"👋 Xush kelibsiz! Siz hali ro'yxatdan o'tmagansiz. Iltimos, /register buyrug'ini bosing.")
        elif not user.access_token:
            send_message(chat_id,"👋 Salom! Iltimos, tizimga kirish uchun /login buyrug'ini bosing.")
        else:

            headers = {"Authorization": f"Bearer {user.access_token}"}
            url = f"{BACKENT_BASE_URL}/v1/users/city/"
            weather(url = url, headers = headers, chat_id = chat_id)

    elif comd == "/weather" and size > 1:
        db = SessionLocal()
        user = db.query(User).filter(User.id == chat_id).first()

        if not user:
             send_message(chat_id,"👋 Xush kelibsiz! Siz hali ro'yxatdan o'tmagansiz. Iltimos, /register buyrug'ini bosing.")
        elif not user.access_token:
            send_message(chat_id,"👋 Salom! Iltimos, tizimga kirish uchun /login buyrug'ini bosing.")
        else:

            headers = {"Authorization": f"Bearer {user.access_token}"}
            url = f"{BACKENT_BASE_URL}/v1/weather/"
            weather(url = url, name = data,headers = headers, chat_id = chat_id)


    elif comd == "/register" and size == 1:
        user_id = chat_id

        db = SessionLocal()
        user = db.query(User).filter(User.id == chat_id).first()

        if user:
            send_message(chat_id, "Siz allaqachon tizimda borsiz")
        else:
            init_user(user_id)
            send_message(chat_id, "👤 Username kiriting:\n\nRegistratsiyani to'xtatish uchun /cancel ni yuboring")

    elif comd == "/login" and size == 1:
        init_user(chat_id)
        set_user_state(chat_id, "waiting_for_login_username")
        send_message(chat_id, "👤 Username kiriting:")

    elif comd == "/logout" and size == 1:
        db = SessionLocal()

        user = db.query(User).filter(User.id == chat_id).first()

        if user:
            if user.access_token != None and user.refresh_token != None:
                url = f"{BACKENT_BASE_URL}/v1/auth/logout/"
                data = {"refresh": user.refresh_token}
                headers = {"Authorization": f"Bearer {user.access_token}"}
                logout_request(url, headers, data, chat_id)
            else:
                send_message(chat_id, "Tizimga kirmagansiz yoki tokeningiz eskirgan")


    elif comd == "/cancel" and size == 1:
        cancel_register(chat_id)


def filter_command_or_text(chat_id, text_message, update):
    if text_message[0] != "/":
        db = SessionLocal()
        user = db.query(User).filter(User.id == chat_id).first()
        state_list = ["waiting_for_username", "waiting_for_first_name", "waiting_for_last_name", "waiting_for_password", "waiting_for_login_username", "waiting_for_login_password"]
        if not user:
            state = get_user_state(chat_id)
            if state in state_list:
                handler_registration(chat_id, text_message, update)
            else:
                send_message(chat_id,"👋 Xush kelibsiz! Siz hali ro'yxatdan o'tmagansiz. Iltimos, /register buyrug'ini bosing.")
        elif not user.access_token:
            state = get_user_state(chat_id)
            if state in state_list:
                handler_registration(chat_id, text_message, update)
            else:
                send_message(chat_id,"👋 Salom! Iltimos, tizimga kirish uchun /login buyrug'ini bosing.")
        else:
            send_message(chat_id, "Botga to'g'ridan to'g'ri xabar yuborib bo'lmaydi, ma'lumot olish uchun /help ni yuboring")
    else:
        commands(chat_id, text_message, update)


def filter_message(update):

    text_message = update.get("message").get("text")
    chat_id = update.get("message").get("from").get("id")
    print(chat_id)
    if text_message != None:
        filter_command_or_text(chat_id, text_message, update)
    else:
        first_name = update.get()
