import asyncio
import glob
import os
import sys
from asyncio import Event
from typing import List, Dict

from .client import method

_lp_modules = 0

for arg in sys.argv:
    if '-lp' in arg:
        _lp_modules += 1


vk_users: List[int] = []
catchers: Dict[int, int] = {}

tg_users: List[int] = []

users_added = Event()

recheck = Event()


def _check():
    vk_users.clear()
    i = 0
    for account in method.billing_get_accounts():
        if account['vk_longpoll']:
            vk_users.append(account['user_id'])
        if account['user_id'] in catchers:
            continue
        catchers[account['user_id']] = i
        i += 1
        if i == _lp_modules:
            i = 0


async def async_users_filler():
    _check()
    users_added.set()

    while True:
        await recheck.wait()
        recheck.clear()
        _check()


async def tmp_cleaner():
    while True:
        for f in glob.glob('venv/*'):
            os.remove(f)
        await asyncio.sleep(3600 * 24)
