import os
import random
import requests

from vk.user_bot import ND, dlp
from vk.user_bot.utils import VoiceMessageUploader


@dlp.register('ргс', receive=True)
def vgs(nd: ND):
    nd.msg_op(4)
    url = f'https://api.meowpad.me/v2/sounds/popular?skip={str(random.randint(1, 400))}'
    get = requests.get(url=url).json()
    res = get['sounds'][random.randint(0, 15)]

    url_d = f"https://api.meowpad.me/v1/download/{res['slug']}"
    file_s = f'tmp/{random.randint(0, 100000000)}'

    with open(file_s, 'wb') as f:
        for chunk in requests.get(url_d).iter_content(chunk_size=128):
            f.write(chunk)

    os.system(f"""ffmpeg -y -hide_banner -loglevel error -i {file_s} stereo.flac -ac 1 {file_s}.ogg""")

    nd.msg_op(1, f"{res['title']}", attachment=VoiceMessageUploader(nd.db.access_token, nd[3], f'{file_s}.ogg'))
