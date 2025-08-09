from datetime import datetime

users = {}

def init_user(user_id):
    users[user_id] = {
        "state": "waiting_for_username",
        "data": {},
        "created_at": datetime.now()
    }

def get_user_state(user_id):
    return users.get(user_id, {}).get("state")

def set_user_state(user_id, state):
    if user_id in users:
        users[user_id]["state"] = state

def update_user_data(user_id, key, value):
    if user_id in users:
        users[user_id]["data"][key] = value

def get_user_data(user_id):
    return users.get(user_id, {}).get("data", {})

def clear_user(user_id):
    if user_id in users:
        del users[user_id]

