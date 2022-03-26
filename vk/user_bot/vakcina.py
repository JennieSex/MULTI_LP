import datetime
import re
import time
import asyncio
import requests
import random
from datetime import datetime

from vk.user_bot import ND, dlp
from vk.user_bot.utils import find_mention_by_message, format_push


@dlp.register('вак')
def vak(nd: ND):
    nd.msg_op(1, "!купить вакцину")
    time.sleep(0.5)
    nd.msg_op(2, f"💉Иду покупать вакцину")
    
        