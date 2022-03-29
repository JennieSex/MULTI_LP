import datetime

import requests

from PIL import Image, ImageOps, ImageDraw, ImageFont
from vk.user_bot import ND, dlp
from vk.user_bot.utils import find_mention_by_message, format_push, crop, prepare_mask
from lib.microvk import VkApiResponseException


@dlp.register('доска', receive=True)
def doska(nd: ND):
    uid = find_mention_by_message(nd.msg, nd.vk)
    user_ = nd.vk('users.get', user_ids=uid, fields='photo_max_orig')[0]

    # автор цитаты
    name = f""" {user_["first_name"]} {user_["last_name"]}"""
    name_font = ImageFont.truetype("content/ttf/junegull_rg.ttf", 30, encoding='UTF-8')
    quote_template = Image.open("content/fon/doska1.jpg")
    draw = ImageDraw.Draw(quote_template)
    HEIGHT = 727
    margin = 4
    size = draw.textsize(name, name_font)
    horizontal_offset = (HEIGHT / 2) - (size[0] / 2) - (margin / 2)
    draw.text((horizontal_offset, 390), name, font=name_font, fill=0)
    url = user_['photo_max_orig']
    resp = requests.get(url, stream=True).raw
    avatar = Image.open(resp)
    # размер круглой
    size = (200, 200)
    avatar = crop(avatar, size)
    avatar.putalpha(prepare_mask(size, 4))
    # круглая ава координаты
    quote_template.paste(avatar, (263, 449), avatar)
    # date
    date = datetime.datetime.today().strftime("%d-%m-%Y")
    ttf_date = ImageFont.truetype("content/ttf/Akrobat-Light.ttf", 20, encoding='UTF-8')
    date_size = draw.textsize(date, ttf_date)
    horizontal_date = (HEIGHT / 2) - (date_size[0] / 2) - (margin / 2)
    draw.text((horizontal_date, 780), date, font=ttf_date, fill=0)
    quote_template.save("tmp/cit.png")
    upload_url = nd.vk('photos.getMessagesUploadServer')['upload_url']
    data = requests.post(upload_url, files={'photo': open('tmp/cit.png', 'rb')}).json()
    saved = nd.vk('photos.saveMessagesPhoto', photo=data['photo'], hash=data['hash'], server=data['server'])[0]
    nd.msg_op(2, f"Сертификат настоящей доске!", attachment=f"photo{saved['owner_id']}_{saved['id']}_{saved['access_key']}", keep_forward_messages=1)

