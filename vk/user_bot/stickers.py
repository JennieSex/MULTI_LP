import requests

from vk.user_bot import ND, dlp
from vk.user_bot.utils import find_mention_by_message, format_push
from lib.microvk import VkApiResponseException


@dlp.register('стики', 'паки', receive=True)
def stickers(nd: ND):
    uid = find_mention_by_message(nd.msg, nd.vk)

    if uid < 0:
        return nd.msg_op(2, "Сообщество чекнуть????", keep_forward_messages=1)

    url = 'https://api.vk.com/method/gifts.getCatalog'

    params = {
        "access_token": '',
        "v": "5.131",
        "user_id": uid
    }
    response = requests.get(url=url, params=params).json()

    stickers_list = []

    for i in response['response'][1]['items']:
        if 'disabled' in i.keys():
            stickers_list.append(
                {"name": i['sticker_pack']['title'],
                 "id": i['gift']['id'],
                 "fields": i}
            )

    user_ = nd.vk('users.get', user_ids=uid)[0]

    message = f"""Информация о стикерах пользователя «{format_push(user_)}»
    💡 Всего: {len(stickers_list)} из {len(response['response'][1]['items'])}

    😇 Стикер-паки: {', '.join(str(e) for e in [k['name'] for k in stickers_list])}
    """

    nd.msg_op(2, message, keep_forward_messages=1)
