import datetime
import re
import time
import asyncio
import requests
from datetime import datetime

from vk.user_bot import ND, dlp
from vk.user_bot.utils import find_mention_by_message, format_push


@dlp.register('ферма')
def farm(nd: ND):
    r_id = -174105461
    item_id = 6713149
    comment_id = (
        nd.vk('wall.createComment', owner_id=r_id, post_id=item_id, message="Ферма"))["comment_id"]
    message = None
    print(comment_id)
    nd.msg_op(2, f"✅Иду собирать ферму :)")
    while not message:
        time.sleep(0.5)
        comments = (
            nd.vk('wall.getComments', owner_id=r_id, post_id=item_id, comment_id=comment_id))["items"]
        for comment in comments:
            if comment["from_id"] == r_id:
                message = comment ["text"]
            break
    text = f"✅Информация о ферме:\n{message}"
    nd.msg_op(2, text)