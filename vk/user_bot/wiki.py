import time
import wikipedia

from lib.microvk import VkApi
from . import dlp, ND


@dlp.register('вики', receive=True)
def wiki(nd: ND):
    try:
        text = nd.msg['args'][0]
        wikipedia.set_lang("RU")
        info = wikipedia.summary(text)
        page = wikipedia.page(text)
        url = nd.vk('utils.getShortLink',url=page.url)["key"]
        nd.vk('utils.deleteFromLastShortened', key=url)
        response = f'📄 Что я нашёл по запросу: {text}\n\n{info[:600]}\n\nСсылка на статью: vk.cc/{url}'
        nd.msg_op(2, f'{response}')
    except Exception as er:
        time.sleep(0.5)
        nd.msg_op(2, f'Ничего не найдено!\nПроверьте запрос!', delete=3)
