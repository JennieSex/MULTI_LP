import requests

from vk.user_bot import ND, dlp
from vk.user_bot.utils import find_mention_by_message


@dlp.register('группы', receive=True)
def groups(nd: ND):
    uid = find_mention_by_message(nd.msg, nd.vk)

    if uid < 0:
        return nd.msg_op(2, "Сообщество чекнуть????", keep_forward_messages=1)

    url = 'https://infoapp-api.i1l.ru/method/getGroups'

    header = {
        'Host': 'infoapp-api.i1l.ru',
        'Connection': 'keep-alive',
        'x-vk-sign': 'ваша авторизация',
        'DNT': '1',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.81 Safari/537.36',
        'sec-ch-ua': '"Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
        'sec-ch-ua-platform': "Windows",
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': '*/*',
        'Origin': "https://prod-app7183114-8ce09ea5ca95.pages-ac.vk-apps.com",
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://prod-app7183114-8ce09ea5ca95.pages-ac.vk-apps.com/',
        'Accept-Language': 'ru-RU,ru;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Content-Length': '23'
    }

    data = f"id={uid}&v=41eaff84"

    a = requests.post(url=url, headers=header, data=str(data)).json()

    if 'response' in a:
        if a['response']['count'] > 0:
            msg = f"У данного пользователя {a['response']['count']} возможных управляемых сообществ\n\n"
            c = 1
            for i in a['response']['items']:
                msg += f"\n{c}. [club{i['id']}|{i['name']}] (👥 {i['members_count']})"
                c += 1

            return nd.msg_op(2, msg, keep_forward_messages=1)
        else:
            return nd.msg_op(2, 'Пользователь скрыл управляемые сообщества или у него их нет!', keep_forward_messages=1)
    else:
        return nd.msg_op(2, 'Походу этого челика не прочекать', keep_forward_messages=1)
