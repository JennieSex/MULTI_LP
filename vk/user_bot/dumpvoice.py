import json
import time

from vk.user_bot import ND, dlp


@dlp.register('дампгс', receive=True)
def dumpgs(nd: ND):
    with open(f"database/users/{nd.db.user_id}/voices.json", "r", encoding="utf-8") as file:
        content = json.load(file)
        for i in content:
            if i["attachments"]:
                nd.msg_op(1, attachment=i["attachments"])
                time.sleep(3)
