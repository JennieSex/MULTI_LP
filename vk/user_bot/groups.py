import requests

from vk.user_bot import ND, dlp
from vk.user_bot.utils import find_mention_by_message


@dlp.register('группы', receive=True)
def groups(nd: ND):
    uid = find_mention_by_message(nd.msg, nd.vk)

    if uid < 0:
        return nd.msg_op(2, "Сообщество чекнуть????", keep_forward_messages=1)

    url = 'https://api.vknext.net/secret/groups'

    header = {
        "Host": "api.bago.si",
        "Connection": "keep-alive",
        "x-vk-sign": "vk_access_token_settings=video,wall,groups&vk_app_id=7183114&vk_are_notifications_enabled=0&vk_is_app_user=1&vk_is_favorite=0&vk_language=ru&vk_platform=desktop_web&vk_ref=other&vk_ts=1643299653&vk_user_id=266287518&sign=NNL5Hp58xYZ8WXAKC19Lds5xspxa6aQkup4CHKbgz4A",
        "DNT": "1",
        "sec-ch-ua-mobile": "?0",
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
        "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
        "sec-ch-ua-platform": "Windows",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "*/*",
        "Origin": "https://prod-app7183114-2d9093161c15.pages-ac.vk-apps.com",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://prod-app7183114-2d9093161c15.pages-ac.vk-apps.com/",
        "Accept-Language": "ru-RU,ru;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Content-Length": "23"
    }

    data = {f"id={uid}&v=656c68bf"}

    print(requests.post(url='https://api.bago.si/method/app.getGroups', headers=header, json=data))

    a = requests.post(url=url, headers=header, data=data).json()
    
    if 'response' in a:
        msg = f"У данного пользователя {a['response']['count']} возможных управляемых сообществ\n\n"
        c = 1
        for i in a['response']['items']:
            msg += f"\n{c}. [{i['screen_name']}|{i['name']}] (👥 {i['members_count']})"
            c += 1

        nd.msg_op(2, msg, keep_forward_messages=1)
    else:
        nd.msg_op(2, 'Походу этого челика не прочекать', keep_forward_messages=1)


