import random
import re
import time

import demapi
import requests

from lib.asyncio_utils import wait_coro
from lib.vkmini import VkApi
from longpoll.copy_server import Listener
from vk.user_bot import ND, dlp
from vk.user_bot.utils import digger

running_users = set()
waiter = None
urls = []



async def mentioner(token: str, peer_id: int, self_id: int):  # noqa
    vk = VkApi(token, excepts=True)
    time_stop = time.time() + 10
    with Listener(self_id) as lp:
        async for update in lp.listen():
            if update[0] != 4:
                continue
            if update[4] > time_stop:
                break
            if update[2] & 2 == 2:
                if update[5].lower() == 'выход':
                    break
                if update[3] == peer_id:
                    print(update)
                    await vk.msg_op(3, message_ids=update[1])
                    return update[5]


@dlp.register('дем', receive=True)
def stickers(nd: ND):
    global waiter

    def e(text):
        nd.vk.msg_op(2, nd[3], text, msg_id=nd[1], delete=3)

    name = re.findall(r"([^|]+)\|?([^|]*)", ' '.join(nd.msg['args']))

    if not name:
        e("❗ Не указано название")
        return "ok"

    atts = digger(nd.msg['raw'])
    main_text = name[0][0].lower().strip()
    second_text = name[0][1].lower().strip()

    if len(main_text) > 220 or len(second_text) > 220:
        return nd.msg_op(2, 'Вы не можете использовать больше 220 символов')

    if not atts:
        return nd.msg_op(2, '🙈 Ничего не найдено')

    for i in atts:
        if 'photo' in i:
            url = str(i['photo']['sizes'][-1]['url'])
            urls.append(url)
        else:
            return nd.msg_op(2, '🙈 Ничего не найдено')

    if len(urls) == 1:
        url = str(urls[0])
        urls.clear()
    else:
        nd.msg_op(2, f"""Было найдено {len(urls)} фотографий\nвыберите фото в течении 10 секунд""")
        if nd.db.user_id not in running_users:
            token = nd.db.access_token
            waiter = wait_coro(mentioner(token, nd[3], nd.db.user_id))
            if waiter is not None:
                if waiter.isnumeric():
                    if int(1) > int(waiter) or int(waiter) <= int(len(urls)):
                        running_users.add(nd.db.user_id)
                    else:
                        return nd.msg_op(2, 'Недопустимый диапазон')
                else:
                    return nd.msg_op(2, 'Должно содержать целое число')
            else:
                return nd.msg_op(2, 'Время вышло')
        else:
            return nd.msg_op(2, 'уже где-то запущено...')

        running_users.remove(nd.db.user_id)
        url = str(urls[int(waiter) - 1])

    name = random.randint(0, 100000000)
    file_s = f'tmp/{name}.png'
    r = requests.get(url)
    urls.clear()

    with open(file_s, 'wb') as f:
        for chunk in r.iter_content(chunk_size=128):
            f.write(chunk)

    conf = demapi.Configure(
        base_photo=file_s,
        title=main_text,
        explanation=second_text
    )

    image = conf.download()
    image.save(file_s)
    upload_url = nd.vk('photos.getMessagesUploadServer')['upload_url']
    data = requests.post(upload_url, files={'photo': open(file_s, 'rb')}).json()
    saved = nd.vk('photos.saveMessagesPhoto', photo=data['photo'], hash=data['hash'], server=data['server'])[0]
    nd.msg_op(2, attachment=f"photo{saved['owner_id']}_{saved['id']}_{saved['access_key']}", keep_forward_messages=1)
