import datetime
from datetime import datetime, timezone, timedelta

from vk.user_bot import ND, dlp


@dlp.register('время')
def ping(nd: ND):
    current_time = datetime.now(timezone(timedelta(hours=+3))).strftime("%d of %B %Y (%j day in year)\n%H:%M:%S") 
    text = f"⚙ Сейчас время и дата: {current_time}"
    nd.msg_op(2, text)
