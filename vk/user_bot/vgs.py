import os
import random
import requests

from vk.user_bot import ND, dlp
from vk.user_bot.utils import digger, VoiceMessageUploader

url = None


@dlp.register('вгс', receive=True)
def vgs(nd: ND):
    global url
    nd.msg_op(3)
    atts = digger(nd.msg['raw'])

    if not atts:
        return nd.msg_op(2, '🙈 Ничего не найдено')

    for i in atts:
        if 'audio' in i['type']:
            url = i.get("audio").get("url")
            break

    for i in atts:
        if 'audio' in i['type']:
            name = random.randint(0, 100000000)
            file_s = f'tmp/{name}'

            r = requests.get(url)

            with open(file_s, 'wb') as f:
                for chunk in r.iter_content(chunk_size=128):
                    f.write(chunk)

            os.system(f"""ffmpeg -y -hide_banner -loglevel error -i {file_s} stereo.flac -ac 1 {file_s}.ogg""")

            nd.msg_op(1, attachment=VoiceMessageUploader(nd.db.access_token, nd[3], f'{file_s}.ogg'))
        else:
            nd.msg_op(2, '🙈 Ничего не найдено')
