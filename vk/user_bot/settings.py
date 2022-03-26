from .utils import ExcReload, set_online_privacy
from database import VkDB
from vk.user_bot.admin.warnings import get_warns

from vk.running_on_tasks import rate_limit_friends


# TODO: ну хотя бы по длине разберись
def sets(nd, db: VkDB, vk, time):  # noqa
    message = nd[5]
    pid = nd[3]
    settings = db.settings_get()
    msg = '💅🏻 Были изменены следующие настройки:\n'

    if '+адвд' in message:
        settings.friends_add = True
        msg += '✅ Включен автоприем заявок в друзья\n'
    elif '-адвд' in message:
        settings.friends_add = False
        msg += '❎ Выключен автоприем заявок в друзья\n'

    if '+автоотписка' in message:
        settings.del_requests = True
        msg += '✅ Включена автоотписка\n'
    elif '-автоотписка' in message:
        settings.del_requests = False
        msg += '❎ Выключена автоотписка\n'

    if '+онлайн' in message:
        if settings.offline: message += '-оффлайн'
        elif '+оффлайн' in message: message = message.replace('+оффлайн', '')
        settings.online = True
        msg += '✅ Включен вечный онлайн\n'
    elif '-онлайн' in message:
        settings.online = False
        msg += '❎ Выключен вечный онлайн\n'
   
    if 'оффлайн' in message:
        if '+оффлайн' in message:
            if settings.online: settings.online = False
            if set_online_privacy(db):
                msg += '✅ Онлайн скрыт\n'
                settings.offline = True
            else:
                msg += '⚠️ Произошла ошибка при установке оффлайна\n'
        elif '-оффлайн' in message:
            if set_online_privacy(db, 'all'):
                msg += '✅ Вечный оффлайн выключен\n'
                settings.offline = False
            else:
                msg += '⚠️ Произошла ошибка при снятии оффлайна\n'

    if '+редач' in message:
        settings.delete['editcmd'] = True
        msg += f'''✅ При удалении сообщений с помощью "{settings.delete['deleter']}-" команда будет редактироваться\n'''
    elif '-редач' in message:
        settings.delete['editcmd'] = False
        msg += f'''❎ При удалении сообщений с помощью "{settings.delete['deleter']}-" команда не будет редактироваться\n'''

    if '+ферма' in message:
        settings.farm['on'] = True
        settings.farm['soft'] = False
        msg += '✅ Автоферма включена\n'
    elif '-ферма' in message:
        settings.farm['on'] = False
        msg += '❎ Автоферма отключена\n'

    if '+удпушей' in message:
        settings.mentions['mine'] = True
        msg += '✅ Сообщения содержащие пуш, будут удаляться\n'
    elif '-удпушей' in message:
        settings.mentions['mine'] = False
        msg += '❎ Сообщения содержащие пуш, не будут удаляться\n'

    if '+удсобак' in message:
        settings.dogs_del = True
        msg += '✅ Удаление заблокированных пользователей включено\n'
    elif '-удсобак' in message:
        settings.dogs_del = False
        msg += '❎ Удаление заблокированных пользователей отключено\n'

    if '+удвсех' in message:
        settings.mentions['all'] = True
        msg += '✅ Сообщения, содержащие пуши типа @аll, будут удаляться\n'
    elif '-удвсех' in message:
        settings.mentions['all'] = False
        msg += '❎ Сообщения, содержащие пуши типа @аll, не будут удаляться\n'

    if '+повторялка' in message:
        settings.repeater['on'] = True
        msg += '✅ Повторялка включена. Убедись, что в доверенных только те люди, которым ты действительно доверяешь!\n'
    elif '-повторялка' in message:
        settings.repeater['on'] = False
        msg += '❎ Повторялка выключена\n'

    if '+автовыход' in message:
        settings.leave_chats = True
        msg += '✅ Автовыход из бесед включен\n'
    elif '-автовыход' in message:
        settings.leave_chats = False
        msg += '❎ Автовыход из бесед отключен\n'

    if '+автостатус' in message:
        if settings.autostatus_format == '':
            msg = '⚠️ Форматтер статуса не установлен'
        else:
            settings.autostatus_on = True
            msg += '✅ Автоматическое обновление статуса включено\n'
    elif '-автостатус' in message:
        settings.autostatus_on = False
        msg += '❎ Автоматическое обновление статуса отключено\n'

    if message.startswith('нд префикс '):
        if "\r" in message or "&" in message:
            msg = '😕 Эээ не, чел, не надо так делать'
        elif message[11:].startswith(settings.delete['deleter']):
            msg = '🤔 Если префикс будет начинаться с удалялки, то как будут работать команды?'
        elif message[11:].startswith('!!'):
            msg = ('🤷‍♀ Префиксы с двумя восклицательными знаками служебные и ' +
                   'не могут быть использованы как кастомный префикс')
        elif message[11:].startswith('нд'):
            msg = ('🤷‍♀ "нд" - служебный префикс и ' +
                   'не может быть использован как кастомный')
        else:
            if ' ' in message[11:]:
                msg = '🤷‍♀ Префикс не может содержать пробелы'
            else:
                settings.prefix = f'{message[11:]} '
                msg = f'''✅ Установлен префикс "{settings.prefix.replace(' ','')}"'''

    if message.startswith('нд повторялка '):
        if message[14:]:
            settings.repeater['prefix'] = message[14:]
            msg = f'''✅ Установлен префикс для повторялки "{settings.repeater['prefix']}"'''

    elif message.startswith('нд удалялка '):
        if message[12:].startswith(settings.prefix):
            msg = '🤔 Если удалялка будет начинаться с префикса, то как будут работать команды?'
        else:
            for char in message[12:]:
                if char.isdigit():
                    msg = '🤷‍♀ Удалялка не должна содержать цифр'
                    break
            if msg != '🤷‍♀ Удалялка не должна содержать цифр':
                if message[12:] == '\r':
                    settings.delete['deleter'] = '&#13;'
                else:
                    settings.delete['deleter'] = message[12:]
                msg = f'''✅ Установлена удалялка "{settings.delete['deleter']}". Все сообщения, начинающиеся с нее, будут расцениваться, как команда 💃'''

    elif message.startswith('нд редач'):
        if message[8:]:
            if len(message[8:]) < 500:
                settings.delete['editor'] = message[8:].replace(' ', '', 1)
                msg = f'''✅ Теперь при удалении сообщений с помощью "{settings.delete['deleter']}-" сообщения будут редактироваться на "{settings.delete['editor']}"'''
            else:
                msg = '😐 Давай-ка уложимся в 500 символов'

    elif message == 'нд старый редач':
        settings.delete['old_type'] = True
        msg = f'''✅ Теперь при удалении сообщений с помощью "{settings.delete['deleter']}-" сообщения будут сначала редактироваться, а потом удаляться вместе'''

    elif message == 'нд новый редач':
        settings.delete['old_type'] = False
        msg = f'''✅ Теперь при удалении сообщений с помощью "{settings.delete['deleter']}-" сообщения будут редактироваться и тут же удаляться'''

    if message == 'нд помощь':
        vk.msg_op(1, pid, f"""
        Основной список команд - "{settings.prefix} команды"

        Все нижеуказанные команды вводятся с префиксом "нд" и знаками +/-
        Можно ввести сразу несколько команд через пробел
        Пример: "нд +онлайн +автоотписка -адвд"

        адвд -- автодобавление в друзья
        онлайн -- вечный онлайн
        оффлайн -- скрытие онлайна (был в сети недавно)
        удсобак -- удаление из друзей удаленных и заблокированных страниц
        автоотписка -- отмена исходящих заявок в друзья
        удпушей -- удаление сообщений с пушем тебя
        удвсех -- удаление сообщений с пушами типа @аll
        автовыход -- автоматический выход при приглашении в беседу
        """.replace('    ', ''))

    elif msg == '💅🏻 Были изменены следующие настройки:\n':
        mentions_on = settings.mentions['all'] or settings.mentions['mine']
        mentions_all = settings.mentions['all'] and settings.mentions['mine']
        vk.msg_op(1, pid, f'''
        🤝 Автодобавление в друзья: {
            '⚠️ Rate limit' if rate_limit_friends.get(db.user_id) else
            ('✅' if settings.friends_add else '❌')
        }
        🐶 Автоудаление "собачек": {'✅' if settings.dogs_del else '❌'}
        🙅‍♀ Автовыход из бесед: {'✅' if settings.leave_chats else '❌'}
        🚯 Удаление пушей: {'❌' if not mentions_on else '✅ ' +
            '@аll и пуши меня' if mentions_all else ('только ' +
            'пуши всех' if settings.mentions['all'] else 'пуши меня')}
        👤 Вечный оффлайн: {'✅' if settings.offline else '❌'}
        👩‍💻 Вечный онлайн: {'✅' if settings.online else '❌'}
        ⛏  Автоферма Ириса: {'✅' if settings.farm['on'] else '❌'}
        🤦 Автоотписка: {'✅' if settings.del_requests else '❌'}
        👩‍🔧 Автостатус: {'✅' if settings.autostatus_on else '❌'}
        📯 Повторялка: {f'✅ Префикс: "{settings.repeater["prefix"]}"'
                        if settings.repeater['on'] else '❌'}
        Установленный префикс: "{settings.prefix.replace(' ','')}"\n
        Удалялка: "{settings.delete['deleter']}", редактируется на "{settings.delete['editor']}", {
            'вместе с командой' if settings.delete['editcmd'] else 'команда не редактируется'}\n
        {'<br>⚠️ Шаблоны привязаны к чату<br>' if settings.templates_bind else '<br>'}
        Список команд - "нд помощь"'''.replace('    ', '') + get_warns())
    else:
        db.settings_set(settings)
        raise ExcReload(pid=pid, text=msg, vk=vk)
