from vk.user_bot import ND, dlp
from vk.user_bot.utils import find_mention_by_message, format_push
from lib.microvk import VkApiResponseException


@dlp.register('подарки', receive=True)
def gifs(nd: ND):
    try:

        uid = find_mention_by_message(nd.msg, nd.vk)

        if uid < 0:
            return nd.msg_op(2, "Сообщество чекнуть????", keep_forward_messages=1)

        try:
            gifts_user = nd.vk('gifts.get', user_id=uid, count=1000)
        except KeyError:
            return nd.msg_op(2, 'Всё по пизде', keep_forward_messages=1)

        users_packages = {}
        types = {'types_count': {"group": 0, "user": 0}}

        for i in gifts_user['items']:

            if i['from_id'] > 0:
                types['types_count']['user'] += 1
                if i['from_id'] not in users_packages.keys():
                    users_packages.update({i['from_id']: {"gifts": []}})

                else:
                    users_packages[i['from_id']]['gifts'].append({
                        'id': i['id'],
                        'message': i['message'],
                        'date': i['date'],
                        'gift': i['gift']
                    })
            else:
                types['types_count']['group'] += 1

        message = (
            f"❈︎Количество подарков ❈: {gifts_user['count']}\n"
            f"★︎от сообществ ★: {types['types_count']['group']}\n"
            f"✷ от пользователей ✷: {types['types_count']['user']}\n"
        )

        last_count = {"count": 0, "user_id": 0, "gift": {}}

        for i in users_packages:

            if last_count['count'] < len(users_packages[i]['gifts']):
                last_count['count'] = len(users_packages[i]['gifts'])
                last_count['user_id'] = i

        user_buy = nd.vk('users.get', user_ids=last_count['user_id'])[0]
        last_gift = users_packages[last_count['user_id']]['gifts'][0]

        message += f"""
        👑 Лучший пользователь который больше всего дарил подарки 👑: «{format_push(user_buy)}»
        с количеством: {last_count['count']}

        Информация о последнем подарке:
        -✪ Комментарии к подарку ✪: {last_gift['message'] if last_gift['message'] == 0 else 'отсутствует'}
        -✪ ID подарка ✪: {last_gift['id']} | {last_gift['gift']['id']}
        -✪ Изоброжение подарка ✪: {last_gift['gift']['thumb_48']}
        """.replace('    ', '')

        nd.msg_op(2, message, keep_forward_messages=1)

    except VkApiResponseException as ar:
        nd.msg_op(2, f"Код ошибки: {ar.error_code}\nСообщение о ошибке: {ar.error_msg}", keep_forward_messages=1)
