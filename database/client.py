from .data_classes import Settings, Account, SettingsTG, AccountTG
from lib.wtflog import get_boy_for_warden
from typing import List
import shutil
import socket
import json
import time
import sys
import os

logger = get_boy_for_warden('DB', 'Клиент базы данных')


# да, я знаю, что так делать нельзя... но похуй))0)
class _tg:
    @staticmethod
    def start():
        return []

root_path = os.path.join(os.path.dirname(__file__), "users")

def read(user_id, filename):
    with open(os.path.join(root_path, f"{user_id}/{filename}.json"), "r", encoding="utf-8") as file:
        	return json.loads(file.read())

def write(user_id, filename, data):
    path = os.path.join(root_path, f"{user_id}/{filename}.json")
    try:
        with open(path, "r", encoding="utf-8") as file:
            backup_data = file.read()
    except:
        backup_data = ""
    with open(path, "w", encoding="utf-8") as file:
        try:
            file.write(
            	json.dumps(data, ensure_ascii=False, indent=4)
            )
        except Exception as e:
            file.write(backup_data)
            raise e

def get_typ(type_):
    return "templates" if type_ == "common" else "voices" if type_ == "voice" else "dutys"

class method:
    tg = _tg

    @staticmethod
    def start() -> List[int]:
        users = []
        for dir in os.listdir(root_path):
            if not dir.isdigit():
                continue
            users.append(int(dir))
        return users

    @staticmethod
    def die() -> None:
        return
        return _make_request('die')

    @staticmethod
    def ping() -> float:
        return "временно пасасать"
        ct = time.time()
        _make_request('ping')
        return round((time.time() - ct) * 1000, 1)

    @staticmethod
    def is_user(uid: int) -> bool:
        for dir in os.listdir(root_path):
            if not dir.isdigit():
                continue
            if int(dir) == uid:
                return True
        return False

    @staticmethod
    def add_user(uid: int):
        os.mkdir(os.path.join(
        	root_path, str(uid)
        ))
        write(uid, "user", {
          "catcher": 2,
          "user_id": uid,
        	"added_by": 0,
          "vk_longpoll": False,
          "prefix": ".л ",
          "farm": {
          	"on": False,
          	"soft": False,
          	"last_time": 0
          },
          "friends_add": False,
          "dogs_del": False,
          "ignore_list": [],
          "del_requests": False,
          "online": False,
          "offline": False,
          "templates_bind": 0,
          "trusted_users": [],
          "delete": {
          	"deleter": "дд",
          	"editor": "&#8300;",
          	"editcmd": True,
          	"old_type": True
          },
          "mentions": {
          	"all": False,
          	"mine": False
          },
          "leave_chats": False,
          "autostatus_on": False,
          "autostatus_format": "",
          "repeater": {
          	"on": False,
          	"prefix": ".."
          }
        })
        write(uid, "templates", [])
        write(uid, "voices", [])
        write(uid, "dutys", [])
        write(uid, "token", {
        	"access_token": "",
        	"me_token": "",
        	"online_token": ""
        })

    @staticmethod
    def remove_user(uid: int):
        shutil.rmtree(os.path.join(root_path, str(uid)))

    @staticmethod
    def remove_template(uid: int, type_: str, data: dict):
        typ = get_typ(type_)
        templates = read(uid, typ)
        for temp in templates:
            if temp['name'].lower() == data['name'].lower():
                templates.remove(temp)
                write(uid, typ, templates)
                return temp
        return {"name": ""}

    @staticmethod
    def get_settings(uid: int) -> dict:
        return read(uid, "user")

    @staticmethod
    def get_account(uid: int) -> dict:
        return read(uid, "user")

    @staticmethod
    def get_tokens(uid: int) -> dict:
        return read(uid, "token")

    @staticmethod
    def get_templates(uid: int, type_: str) -> dict:
        return read(uid, get_typ(type_))

    @staticmethod
    def get_all_templates_length() -> dict:
        return 666
        return _make_request('info', 'templates')

    @staticmethod
    def set_template(uid: int, type_: str, data: dict) -> dict:
        repl = {"name": ""}
        templates = read(uid, get_typ(type_))
        for i, temp in enumerate(templates):
            if temp['name'].lower() == data['name'].lower():
                repl = temp
                templates[i] = data
                break
        if not repl['name']:
            templates.append(data)
        write(uid, get_typ(type_), templates)
        return repl

    @staticmethod
    def update_token(uid: int, access_token: str = '', me_token: str = '',
                     online_token: str = ''):
        tokens = read(uid, "token")
        if access_token:
            tokens.update({"access_token": access_token})
        if me_token:
            tokens.update({"me_token": me_token})
        if online_token:
            tokens.update({"online_token": online_token})
        if not tokens:
            raise ValueError()
        write(uid, "token", tokens)

    @staticmethod
    def update_account(uid: int, account: Account):
        write(uid, "user", _search_updates(account))

    @staticmethod
    def update_settings(uid: int, settings: Settings):
        write(uid, "user", _search_updates(settings))

    @staticmethod
    def billing_get_accounts() -> List[dict]:
        accounts = []
        for uid in method.start():
            accounts.append(method.get_account(uid))
        return accounts

    @staticmethod
    def billing_get_balance(uid: int) -> float:
        return "нихуя"


def _search_updates(instance) -> dict:
    data = {}
    for att in instance.attributes:
        if getattr(instance, att, "not setted") != "not setted":
            data.update({att: getattr(instance, att)})
    if not data:
        raise ValueError()
    return data
