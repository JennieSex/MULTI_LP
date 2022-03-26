import datetime
import re
import time
import json
import requests
from datetime import datetime, timezone, timedelta

from vk.user_bot import ND, dlp
from vk.user_bot.utils import find_mention_by_message, format_push


@dlp.register('время')
def ping(nd: ND):
    current_time = datetime.now(timezone(timedelta(hours=+3))).strftime("%d of %B %Y (%j day in year)\n%H:%M:%S") 
    text = f"⚙ Сейчас время и дата: {current_time}"
    nd.msg_op(2, text)