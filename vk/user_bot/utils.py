import json
import textwrap

from PIL import Image, ImageDraw

from lib.microvk import VkApi
from lib.vkmini import LP
from lib.common_utils import parse_text
from database import VkDB
from time import sleep
from typing import List, Union, Any
from mutagen.mp3 import MP3
import requests
import random
import re
import io


class ExcReload(Exception):
    "Генерация этого исключения вызывает перезапуск поллера"
    pid: int = None
    text: str = None
    vk: VkApi

    def __init__(self, vk, text: str = None, pid: int = None):
        self.vk = vk
        self.text = text
        self.pid = pid


def is_int(str):
    try:
        int(str)
        return True
    except ValueError:
        return False


def VoiceMessageUploader(token, peer_id, name):
    a = requests.post('https://api.vk.com/method/docs.getMessagesUploadServer',
                      params={'access_token': token, 'v': 5.131, 'type': 'audio_message', 'peer_id': peer_id})
    a = requests.post(json.loads(a.text)['response']['upload_url'], files={'file': open(name, 'rb')})
    a = json.loads(a.text)
    a = requests.post('https://api.vk.com/method/docs.save',
                      params={'access_token': token, 'v': 5.131, 'file': a['file']})
    a = json.loads(a.text)['response']['audio_message']
    return f'doc{a["owner_id"]}_{a["id"]}'


def parseByID(vk, msg_id, atts=[]):
    msg = (vk('messages.getById', message_ids=msg_id)['items'][0])
    return parse(msg, atts)


def parse(msg: dict, atts: bool = [], cut_prefix: bool = True):
    cmd, args, payload = parse_text(msg['text'], cut_prefix)
    if atts:
        atts = att_parse(msg['attachments'])

    if type(msg) == str:  # я правда не помню, нахрена я так сделал
        msg = {'text': msg}

    return {'text': msg['text'], 'args': args, 'payload': payload, 'command': cmd, 'attachments': atts,
            'reply': msg.get('reply_message'), "fwd": msg.get('fwd_messages'), "raw": msg}


def digger(msg: dict) -> List[dict]:
    atts = []
    for fmsg in msg.get('fwd_messages', []):
        atts.extend(digger(fmsg))
    if msg.get('reply_message'):
        atts.extend(digger(msg['reply_message']))
    atts.extend(msg['attachments'])
    return atts


def att_parse(attachments: List[dict]) -> List[str]:
    atts = []
    for i in attachments:
        if type(i) == str:
            atts.append(i)
            continue
        att_t = i['type']
        if att_t in {'link', 'article'}: continue  # noqa
        atts.append(att_t + str(i[att_t]['owner_id']) +
                    '_' + str(i[att_t]['id']))
        if i[att_t].get('access_key'):
            atts[-1] += '_' + i[att_t]['access_key']
    return atts


def msg_op(mode: int, peer_id: str, message='', msg_id='', delete: int = 0, api=0, **kwargs):
    # mode: 1 - отправка, 2 - редактирование, 3 - удаление, 4 - удаления только для себя
    # if 2000000000 > peer_id > 1000000000:
    #     peer_id = ~peer_id + 1000000001

    if mode == 4:
        mode = 3
        dfa = 0
    else:
        dfa = 1

    mode = ['messages.send', 'messages.edit', 'messages.delete'][mode - 1]
    response = api(mode, peer_id=peer_id, message=message,
                   message_id=msg_id, delete_for_all=dfa, random_id=0, **kwargs)
    if delete:
        sleep(delete)
        api('messages.delete', message_id=msg_id, delete_for_all=1)
    return response


def get_my_messages(vk: VkApi, peer_id: int) -> List[dict]:
    messages = []
    for msg in vk('messages.getHistory', peer_id=peer_id, count=200)['items']:
        if msg['out']:
            messages.append(msg)
    return messages


def get_msgs(vk, peer_id, offset=0):
    return exe('''return (API.messages.getHistory({"peer_id":"%s",
    "count":"200", "offset":"%s"}).items) + (API.messages.getHistory({"peer_id":
    "%s", "count":"200", "offset":"%s"}).items);''' %
               (peer_id, offset, peer_id, offset + 200), vk)


def get_last_th_msgs(peer_id, vk):
    return exe('''return (API.messages.getHistory({"peer_id":"%(peer)s",
    "count":"200", "offset":0}).items) + (API.messages.getHistory({"peer_id":
    "%(peer)s", "count":"200", "offset":200}).items) + (API.messages.getHistory({"peer_id":
    "%(peer)s", "count":"200", "offset":400}).items) + (API.messages.getHistory({"peer_id":
    "%(peer)s", "count":"200", "offset":600}).items) + (API.messages.getHistory({"peer_id":
    "%(peer)s", "count":"200", "offset":800}).items);''' % {'peer': peer_id}, vk)


def upload_audio(att, vk):
    audio_url = att['audio_message']['link_mp3']
    response = requests.get(url=audio_url)
    audio_msg = io.BytesIO(response.content)
    audio_msg.name = 'voice.mp3'
    upload_url = vk('docs.getUploadServer',
                    type='audio_message')['upload_url']
    uploaded = requests.post(upload_url, files={'file': audio_msg}).json()['file']
    audio = vk('docs.save', file=uploaded)['audio_message']
    length = round(MP3(audio_msg).info.length, 1)
    del (audio_msg)
    return f"audio_message{audio['owner_id']}_{audio['id']}_{audio['access_key']}", length


def format_push(u: dict, group: bool = False) -> str:
    uid = u['id']
    if group:
        return f"[club{abs(uid)}|{u['name']}]"
    else:
        return f"[id{uid}|{u['first_name']} {u['last_name']}]"


def upload_sticker(att, vk):
    att = att['sticker']
    response = requests.get(url=att['images'][1]['url'])
    sticker = io.BytesIO(response.content)
    sticker.name = 'sticker.png'
    upload_url = vk('docs.getUploadServer', type='graffiti')['upload_url']
    uploaded = requests.post(upload_url, files={'file': sticker}).json()['file']
    sticker = vk('docs.save', file=uploaded)['graffiti']
    sticker = f"sticker{sticker['owner_id']}_{sticker['id']}_{sticker['access_key']}"
    return sticker


def upload_avatar(image_url, vk):
    'Возвращает post_id с обновлением фотографии'
    image = io.BytesIO(requests.get(url=image_url).content)
    image.name = 'avatar.jpg'
    upload_url = vk('photos.getOwnerPhotoUploadServer')['upload_url']
    data = requests.post(upload_url, files={'photo': image}).json()
    del (image)
    return vk('photos.saveOwnerPhoto', photo=data['photo'],
              hash=data['hash'], server=data['server'])['post_id']


def upload_photo(image_url: str, vk: VkApi) -> str:
    'Возвращает аттач'
    image = io.BytesIO(requests.get(url=image_url).content)
    image.name = 'someshit.jpg'
    upload_url = vk('photos.getMessagesUploadServer')['upload_url']
    data = requests.post(upload_url, files={'photo': image}).json()
    del (image)
    saved = vk('photos.saveMessagesPhoto', photo=data['photo'],
               hash=data['hash'], server=data['server'])[0]
    return f"photo{saved['owner_id']}_{saved['id']}_{saved['access_key']}"


def exe(code, vk):
    'Метод execute'
    return vk('execute', code=code)


def get_msg(api, peer_id, local_id):
    try:
        data = api("messages.getByConversationMessageId", peer_id=peer_id,
                   conversation_message_ids=local_id)
        return data['items'][0]
    except Exception:
        return None


def get_index(items: list, key: int, default: Any = None) -> Any:
    'Возвращает элемент с индексом key, при его отсутствии возвращает default'
    try:
        return items[key]
    except IndexError:
        return default


def find_time(text: str) -> int:
    hours = re.findall(r'\d+ ?ч\w*', text)
    secs = re.findall(r'\d+ ?с\w*', text)
    mins = re.findall(r'\d+ ?м\w*', text)
    print(hours)

    time = 0
    for i in hours:
        time += int(re.search(r'\d+', i)[0]) * 3600
    for i in mins:
        time += int(re.search(r'\d+', i)[0]) * 60
    for i in secs:
        time += int(re.search(r'\d+', i)[0])

    return time


def execme(code: str, db: VkDB) -> int:
    if db.me_token == '':
        return "-1"
    vk = VkApi(access_token=db.me_token)
    return vk('execute', code=code)


def gen_secret(chars: str = 'abcdefghijklmnopqrstuvwxyz0123456789_-'):
    secret = ''
    length = random.randint(64, 80)
    while len(secret) < length:
        secret += chars[random.randint(0, 37)]
    return secret


def find_user_mention(text):
    uid = re.findall(r'\[(id|public|club)(\d*)\|', text)
    if uid:
        if uid[0][0] != 'id':
            uid = 0 - int(uid[0][1])
        else:
            uid = int(uid[0][1])
    return uid


# TODO: группы
def find_user_by_link(text, vk):
    user = re.findall(r"vk.com\/(id\d*|[^ \n]*\b)", text)
    if user:
        try:
            return vk('users.get', user_ids=user)[0]['id']
        except Exception:
            pass


def find_mention_by_message(msg: dict, vk: VkApi) -> Union[int, None]:  # noqa
    'Возвращает ID пользователя, если он есть в сообщении, иначе None'
    user_id = None
    if msg['args']:
        user_id = find_user_mention(' '.join(msg['args']))
    if msg['reply'] and not user_id:
        user_id = msg['reply']['from_id']
    if msg['fwd'] and not user_id:
        user_id = msg['fwd'][0]['from_id']
    if not user_id:
        user_id = find_user_by_link(msg['text'], vk)
    print(f'UID: {user_id}' if user_id else 'UID not found!')
    return user_id


def set_online_privacy(db, mode='only_me'):
    url = ('https://api.vk.me/method/account.setPrivacy?v=5.109&key=online&value=%s&access_token=%s'
           % (mode, db.me_token))
    ua = "VKAndroidApp/1.123-123 (Android 123; SDK 123; Random Bot Club; 1; ru; 123x123)"
    r = requests.get(url, headers={"user-agent": ua}).json()
    if r['response']['category'] == mode:
        return True
    else:
        return False


def get_plural(number: Union[int, float], one: str, few: str,
               many: str, other: str = '') -> str:
    """`one`  = 1, 21, 31, 41, 51, 61...\n
    `few`  = 2-4, 22-24, 32-34...\n
    `many` = 0, 5-20, 25-30, 35-40...\n
    `other` = 1.31, 2.31, 5.31..."""
    if type(number) == float:
        if not number.is_integer():
            return other
        else:
            number = int(number)
    if number % 10 in {2, 3, 4}:
        if not 10 < number < 20:
            return few
    number = str(number)
    if number[-1] == '1':
        return one
    return many


# TODO: мало используется
def get_text_from_message(msg: dict) -> str:
    if msg['payload'] == '':
        return ' '.join(msg['args'])
    else:
        return ' '.join(msg['args']) + '\n' + msg['payload']


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


######### И З О Б Р А Ж Е Н И Я ##############
def prepare_mask(size, antialias=2):
    mask = Image.new('L', (size[0] * antialias, size[1] * antialias), 0)
    ImageDraw.Draw(mask).ellipse((0, 0) + mask.size, fill=255)
    return mask.resize(size, Image.ANTIALIAS)


# тоже закругление
def crop(image, size):
    width, hight = image.size
    result = width / size[0] - hight / size[1]
    if result > 0:
        image = image.crop(((width - hight) / 2, 0, (width + hight) / 2, hight))
    elif result < 0:
        image = image.crop((0, (hight - width) / 2, width, (hight + width) / 2))
    return image.resize(size, Image.ANTIALIAS)


def draw_centered_text(image, font, text, color=(255, 255, 255)):
    draw = ImageDraw.Draw(image)
    margin, offset = image.size[0] / 100, image.size[1] / 4
    for line in textwrap.wrap(text, width=57):
        draw.text((margin, offset), line, font=font, color=color)
        offset += font.getsize(line)[1]
    return image