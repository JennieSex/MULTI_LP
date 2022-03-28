import time

from lib.asyncio_utils import wait_coro
from longpoll.copy_server import Listener
from . import dlp, ND

running_users = set()


async def mentioner(peer_id: int, self_id: int):  # noqa
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
                    return update[5]


@dlp.register('вайт', receive=True)
def start_mentioning(nd: ND):
    if nd.db.user_id not in running_users:
        running_users.add(nd.db.user_id)
        nd.msg_op(2, 'напиши любое сообщение в течении 10 секунд')
        waiter = wait_coro(mentioner(nd.db.user_id))
        if waiter is not None:
            nd.msg_op(1, f'Введенный текст: {waiter}')
        running_users.remove(nd.db.user_id)
    else:
        nd.msg_op(2, 'уже где-то запущено...')
