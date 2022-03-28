from typing import Union

from vk.user_bot import dlp, ND
from vk.user_bot.utils import (find_mention_by_message, get_index,
                               upload_photo, format_push)



@dlp.register('профиль','проф','profile', receive=True)
def profile_detail(nd: ND):
    uid = find_mention_by_message(nd.msg, nd.vk)
    if not uid:
        return nd.msg_op(2, '⚠ Не удалось найти пользователя')
    user = nd.vk(
            'users.get',
            user_ids = uid,
            fields = 'photo_50,status,bdate,blacklisted_by_me,'
                    'blacklisted,photo_max_orig,is_friend,'
                    'last_name_abl,first_name_abl,domain,'
                    'city,followers_count,last_seen,online,sex,is_closed'
        )[0]
    sex = nd.vk('users.get',user_ids = uid, fields = 'sex')[0]
    URL = nd.vk('utils.getShortLink',
                url = user["photo_max_orig"]
        )["key"]
    nd.vk('utils.deleteFromLastShortened', key = URL)
    city_name: str = user.get('city', {}).get('title', "Мухосранск")
    followers: str = user.get('followers_count', "Их нет...")
    date_dr: str = user.get('bdate', "Год не указан")
    platform = user.get('last_seen', {}).get('platform', "Не официальное ПО")

    user["blacklisted_by_me"] = b2s(user["blacklisted_by_me"])
    user["blacklisted"] = b2s(user["blacklisted"])
    user["is_closed"] = b2s(user["is_closed"])
    user["is_friend"] = b2s(user["is_friend"])
    user["online"] = 'Online' if user["online"] else 'Offline'

    if sex['sex'] == 1:
        sex = 'а'
    else:
        sex = ''

    if user['sex'] == 1:
        user['sex'] = "👱‍♀️"
    elif user['sex'] == 2:
        user['sex'] = "👨"
    else:
        user["sex"] = "Ламинат"

    if platform == 1:
        platform = "Мобильная версия"
    elif platform == 2:
        platform = "Приложение для iPhone"
    elif platform == 3:
        platform = "Приложение для iPad"
    elif platform == 4:
        platform = "Приложение для Android"
    elif platform == 5:
        platform = "Приложение для Windows Phone"
    elif platform == 6:
        platform = "Приложение для Windows 10"
    elif platform == 7:
        platform = "Полная версия сайта"
    else:
        platform = "Что ты такое?"

    msg = f"""
    Информация о {format_push(user)}
    {user["online"]}, {platform}

    ⚙ID: {user["id"]}
    ⚙Короткая ссылка: {user["domain"]}
    ⚙Имя: {user["first_name"]}
    ⚙Фамилия: {user["last_name"]}
    🎉Дата рождение: {date_dr}
    🌆Город: {city_name}
    👻Друзья: {user["is_friend"]}
    ✍🏻Подписчики: {followers}
    {user['sex']}Пол: {user["sex"]}
    🔒Закрытый прoфиль: {user["is_closed"]}
    💬Статус: {user["status"]}
    ⛔Я в чс: {user["blacklisted"]}
    ⛔Он{sex} в чс: {user["blacklisted_by_me"]}
    📷Фото: vk.cc/{URL}
    """.replace('    ', '')

    if get_index(nd.msg['args'], 0) == 'кратко':
        message = f'Пользователь {format_push(user)}:\n'
        message += f'ID: {user["id"]}\n'
        message += f'Дата рождения: {birthday(user)}\n'
        message += f''
        nd.msg_op(2, message)
    elif get_index(nd.msg['args'], 0) == "ава":
        photo = upload_photo(user['photo_max_orig'], nd.vk)
        nd.msg_op(2, f"Аватарка пользователя {format_push(user)}",
                  attachment=photo)
    else:
        nd.msg_op(2, f"{msg}")
def b2s(value: Union[bool, int]) -> str:
    if value:
        return "✅"
    return "🚫"

def birthday(user: dict) -> str:
    date = user.get('bdate')
    if date is None:
        return 'не указана'
    if date.count('.') == 1:
        return date + ', год не указан'
    return date
