import time
from vk.user_bot import dlp, ND
from longpoll.lp import send_to_lp, _lp_ports
from database.client import method
from vk.user_bot.ping import pingvk
from vk.user_bot.utils import get_plural
from vk.user_bot.admin.admin import check_moder


@dlp.register('stat', 'state', 'stats')
@dlp.wrap_handler(check_moder)
def stat(nd: ND):
    delta = round(nd.time - nd[4], 1)
    ct = time.time()
    lp_info = ""
    for i, _ in enumerate(_lp_ports):
        ct = time.time()
        data = send_to_lp('info', i)
        ping_lp = round((time.time() - ct) * 1000, 1)
        uptime = round(data['seconds']/60)
        lp_info += f"""-- LP модуль {i+1} --
    {ping_lp} мс | {uptime} минут{get_plural(uptime, 'а', 'ы', '')}
    {round(data['events']/data['seconds'], 1)} events/sec (msg: {round(data['messages']/data['events']*100)}% | cmd: {data['commands']})\n"""
    msg = f"""
    Получено за {delta}(±0.5) сек
    Обработано за {round((time.time() - nd.time) * 1000, 1)} мс
    Пинг execute: {pingvk(nd.vk)} мс
    Время затраченное на получение сообщения: {
        pingvk(nd.vk, 'messages.getById', message_ids=nd[1])} мс
    {lp_info}
    """.replace('    ', '')
    nd.msg_op(2, msg)
