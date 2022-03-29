import random
import re

from vk.user_bot import ND, dlp
from vk.user_bot.utils import find_mention_by_message, format_push, digger, find_time


@dlp.register('ст', receive=True)
def stickers(nd: ND):

    args = ' '.join(nd.msg['args'])
    nd.msg_op(1, f'Аргументы: {args}')

    regexp = r"(^[\S]+)|([\S]+)|(\n[\s\S \n]+)"
    _args = re.findall(regexp, args)
    nd.msg_op(1, str(_args))


