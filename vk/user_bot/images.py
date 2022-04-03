import datetime
import random
import re

import requests

from PIL import Image, ImageDraw, ImageFont, ImageOps
from vk.user_bot import ND, dlp
from vk.user_bot.utils import find_mention_by_message, crop, prepare_mask, PhotoMessageUploader, DocMessageUploader

ADV_FONT = ImageFont.truetype("content/ttf/minecraft-rus.ttf", 40)


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
    dosk_gen = random.randint(0, 999999)
    dosk = f"tmp/doska_{dosk_gen}.png"
    quote_template.save(dosk)
    dosk_ = PhotoMessageUploader(dosk, nd.vk)
    nd.msg_op(2, f"Сертификат настоящей доске!", attachment=dosk_, keep_forward_messages=1)


@dlp.register('ачивка', receive=True)
def advancements(nd: ND):
    def e(text):
        nd.vk.msg_op(2, nd[3], text, msg_id=nd[1], delete=3)

    name = re.findall(r"([^|]+)\|?([^|]*)", ' '.join(nd.msg['args']))

    if not name:
        e("❗ Не указано название")
        return "ok"

    main_text = name[0][0].lower().strip()
    second_text = name[0][1].lower().strip()

    if len(main_text) > 220 or len(second_text) > 220:
        return nd.msg_op(2, 'Вы не можете использовать больше 220 символов')

    main_text_width = ADV_FONT.getsize(main_text)[0] + 180
    second_text_width = ADV_FONT.getsize(second_text)[0]

    adv_icon = Image.open("content/fon/default_icon.png").convert("RGBA")

    blank = Image.new(
        "RGBA",
        (
            main_text_width + 10
            if main_text_width > second_text_width
            else second_text_width + 50, 195,
        ),
    )

    adv_start = Image.open("content/fon/adv_start.png").convert("RGBA")
    adv_middle = Image.open("content/fon/adv_middle.png")
    adv_end = Image.open("content/fon/adv_end.png")
    adv_icon = adv_icon.resize((95, 90), Image.NEAREST)

    for i in range(blank.width):
        blank.paste(adv_middle, (i, 0))

    blank.paste(adv_start)
    blank.paste(adv_end, (blank.width - 10, 0))
    blank.paste(adv_icon, (40, 20), adv_icon)
    draw = ImageDraw.Draw(blank)
    draw.text((25, 135), second_text, font=ADV_FONT)
    draw.text((170, 40), main_text, font=ADV_FONT)

    blank = ImageOps.expand(blank, border=100, fill="white")

    # Сохранение и загрузка пхото
    name_adv = f"tmp/adv_final_{random.randint(0, 9999999)}.png"
    blank.save(name_adv)
    acv = PhotoMessageUploader(name_adv, nd.vk)
    nd.msg_op(2, f"Допустим", attachment=acv, keep_forward_messages=1)


@dlp.register('крыса', receive=True)
def rat(nd: ND):
    uid = find_mention_by_message(nd.msg, nd.vk)
    user_ = nd.vk('users.get', user_ids=uid, fields='photo_max_orig')[0]

    url = user_['photo_max_orig']
    resp = requests.get(url, stream=True).raw
    avatar = Image.open(resp)
    # размер круглой
    size = (180, 180)
    avatar = crop(avatar, size)
    avatar.putalpha(prepare_mask(size, 4))
    name = user_["first_name"]
    fon_rat = Image.open("content/fon/rat.png")
    draw = ImageDraw.Draw(fon_rat)
    name_font = ImageFont.truetype("content/ttf/junegull_rg.ttf", 30, encoding='UTF-8')
    fon_rat.paste(avatar, (58, 336), mask=avatar)
    w, h = draw.textsize(name.encode('UTF-8'))
    W, H = (237, 8)
    draw.text(((W - w) / 2, 298), name, font=name_font, fill=(255, 0, 255))
    name = random.randint(0, 100000000)
    file_s = f'tmp/rat_{name}.png'
    fon_rat.save(file_s)
    attach = PhotoMessageUploader(file_s, nd.vk)
    nd.msg_op(2, f"Допустим", attachment=attach, keep_forward_messages=1)


@dlp.register('сертификат', receive=True)
def dalb(nd: ND):
    uid = find_mention_by_message(nd.msg, nd.vk)
    user_ = nd.vk('users.get', user_ids=uid, fields='photo_max_orig')[0]
    name = f""" {user_["first_name"]} {user_["last_name"]}"""
    name_font = ImageFont.truetype("content/ttf/junegull_rg.ttf", 90, encoding='UTF-8')
    quote_template = Image.open("content/fon/dalb.jpg")
    draw = ImageDraw.Draw(quote_template)
    HEIGHT = 2560
    margin = 4
    size = draw.textsize(name, name_font)
    horizontal_offset = (HEIGHT / 2) - (size[0] / 2) - (margin / 2)
    draw.text((horizontal_offset, 940), name, font=name_font, fill=0)
    avatar = Image.open(requests.get(user_['photo_max_orig'], stream=True).raw)
    avatar = crop(avatar, (400, 400))
    avatar.putalpha(prepare_mask((400, 400), 4))
    quote_template.paste(avatar, (1022, 505), avatar)
    ttf_date = ImageFont.truetype("content/ttf/Akrobat-Light.ttf", 40, encoding='UTF-8')
    draw.text((820, 1500), datetime.datetime.today().strftime("%d-%m-%Y"), font=ttf_date, fill=0)
    dalb_gen = random.randint(0, 999999)
    dosk = f"tmp/dalb_{dalb_gen}.png"
    quote_template.save(dosk)
    attach_dalb = PhotoMessageUploader(dosk, nd.vk)
    nd.msg_op(2, f"Допустим", attachment=attach_dalb, keep_forward_messages=1)


@dlp.register('дурка', receive=True)
def pho(nd: ND):
    uid = find_mention_by_message(nd.msg, nd.vk)
    user_ = nd.vk('users.get', user_ids=uid)[0]
    name = user_["first_name"]
    name_font = ImageFont.truetype("content/ttf/Borsok.ttf", 25, encoding='UTF-8')
    quote_template = Image.open("content/fon/дурка.png")
    draw = ImageDraw.Draw(quote_template)
    draw.text((80, 380), f'я {name}', font=name_font, fill=(0, 0, 0))
    durka_gen = random.randint(0, 999999)
    durka = f"tmp/dalb_{durka_gen}.png"
    quote_template.save(durka)
    nd.msg_op(2, f"Допустим", attachment=PhotoMessageUploader(durka, nd.vk), keep_forward_messages=1)


@dlp.register('фото плс', receive=True)
def pho(nd: ND):
    uid = find_mention_by_message(nd.msg, nd.vk)
    user_ = nd.vk('users.get', user_ids=uid, fields='photo_max_orig')[0]

    url = user_['photo_max_orig']
    resp = requests.get(url, stream=True).raw
    avatar = Image.open(resp)
    # размер круглой
    size = (400, 400)
    avatar = crop(avatar, size)
    avatar.putalpha(prepare_mask(size, 4))
    avatar.save("tmp/ava1.png")
    nd.msg_op(1, f"Допустим", attachment=DocMessageUploader(nd.db.access_token, nd[3], f"tmp/ava1.png"))
