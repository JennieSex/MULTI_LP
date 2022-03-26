import requests

from vk.user_bot import ND, dlp
from .utils import find_mention_by_message, format_push


def get_vkmp3mod():
    resp = requests.post(
        "http://vkmp3mod.somee.com/Json",
        headers={
            "Content-Type": "application/octet-stream",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 10; HRY-LX1 Build/HONORHRY-L21)",
            "Host": "vkmp3mod.somee.com",
            "Accept-Encoding": "gzip",
            "Connection": "keep-alive",
            "Content-Length": "64"
        },
        data=bytes.fromhex(
            '43 e3 f5 d6 d9 39 ea 12 fc c4 fe fc 4d 00 59 87 41 32 84 b2 fb 81 41 c9 1c 2c c0 c0 8e '
            'a3 2c 7b 39 9f 45 79 15 82 d5 57 f5 a0 1f 3d 16 31 a4 65 27 b8 9c 59 d7 0f 95 ce db e3 '
            'd8 ef 5f 52 61 d2'
        ),
        timeout=5
    )
    return resp.json()


def get_vk_coffee():
    resp = requests.get(
        "http://vkcoffee.operator555.su/repository/direct.php",
        headers={
            "User-Agent": "VKCoffee/8.03-55 (Android 10; SDK 29; armeabi-v7a; HUAWEI HRY-LX1; ru)",
            "Accept-Encoding": "gzip"
        },
        timeout=5
    )
    return resp.json()


def get_sova():
    return requests.get(
        "https://utkacraft.ru/sova/lite/verif.php",
        headers={
            "Host": "utkacraft.ru",
            "Accept-Encoding": "gzip",
            "User-Agent": "okhttp/4.8.0",
        },
        timeout=5
    ).json()


def get_toaster():
    return requests.post(
        "https://gdlbo.net/vktoaster/getGalo4kiBatch",
        headers={
            "User-Agent": "okhttp/4.8.0",
        },
        json=dict(types=[0, 228, 404, 1337]),
        timeout=5
    ).json()


@dlp.register('галки', receive=True)
def galki(nd: ND):
    uid = find_mention_by_message(nd.msg, nd.vk)

    if not uid:
        return nd.msg_op(2, '⚠️ Необходимо указать пользователя')

    try:
        mp3_data = get_vkmp3mod()
        mp3_ver_list = [int(ver_id) for ver_id in mp3_data['verified'].split(',') if
                        ver_id.replace('-', '').isdigit()]
        mp3_mod = '✅' if uid in mp3_ver_list else '🚫'
    except:
        mp3_mod = "N/A"

    try:
        vk_coffee_data = get_vk_coffee()['don']
        vk_coffee = "✅" if any([
            uid in vk_coffee_data['category_lite'],
            uid in vk_coffee_data['category_medium'],
            uid in vk_coffee_data['category_full']
        ]) else '🚫'
    except:
        vk_coffee = "N/A"

    try:
        sova_data = get_sova()
        sova = '🚫'
        for k, v in sova_data.items():
            if not isinstance(v, list):
                continue
            if uid in [int(uid) for uid in v if uid.replace("-", '').isdigit()]:
                sova = "✅"
                break
    except:
        sova = "N/A"

    try:
        toaster = '🚫'
        toaster_data = get_toaster()
        for k, v in toaster_data.items():
            if not isinstance(v, list):
                continue
            if uid in [int(uid) for uid in v if uid.replace("-", '').isdigit()]:
                toaster = "✅"
                break
    except:
        toaster = "N/A"

    user = nd.vk('users.get', user_ids=uid, fields='verified')[0]

    text = (
        f"Галки пользователя {format_push(user)}:\n"
        f"🏦|VK: {'✅' if user['verified'] else '🚫'}\n"
        f"🎧|VK MP3 MOD: {mp3_mod}\n"
        f"☕|VK Coffee: {vk_coffee}\n"
        f"🦉|SOVA: {sova}\n"
        f"🍞|VTosters: {toaster}\n"
    ).replace('    ', '')

    nd.msg_op(2, text, keep_forward_messages=1)
