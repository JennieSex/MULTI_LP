import datetime
import re

from vk.user_bot import ND, dlp
from vk.user_bot.utils import find_mention_by_message, format_push


@dlp.register('зз', receive=True)
def zz(nd: ND):
    uid = find_mention_by_message(nd.msg, nd.vk)

    if uid < 0:
        return nd.msg_op(2, "чекать заразы сообщества???", keep_forward_messages=1)

    qs = f"id{nd.db.user_id} подверг заражению id{uid}"
    msgs = []
    toget = 200  # 50, 100, 200, 300, 400, etc
    rcount = 100  # per request (100 max)
    roffset = 0
    gotcha = False
    while not gotcha:
        response = nd.vk('messages.search',
                         q=qs,
                         count=rcount,
                         extended=False,
                         offset=roffset
                         )

        if response['count'] < 100:
            gotcha = True
        for msg in response['items']:
            msgs.append(msg)
        roffset += rcount
        if roffset >= toget:
            gotcha = True
    user_ = nd.vk('users.get', user_ids=uid)[0]
    hs = f"Как {format_push(user_)}\nмною заражен был:\n\n"
    count = 0
    for msg in msgs:
        if msg['text'].find('Служба безопасности лаборатории') > -1:
            continue
        i_p = msg['text'].find('подверг')
        i_s = msg['text'].find(f'{nd.db.user_id}')
        if i_s > i_p:
            continue
        go = False
        a = None
        b = None
        rows = msg['text'].split('\n')
        for row in rows:
            if row.find('Заражение на') > -1:
                sp = row.split(' ')
                for word in sp:
                    if word.isdigit():
                        a = word
                        go = True
            if row.find('био-опыта') > -1:
                sp = row.split('био-опыта')
                if len(sp) > 0:
                    b = sp[0]
                    go = True
        if go:
            a = int(a)
            dt = datetime.datetime.fromtimestamp(msg['date'])
            dt += datetime.timedelta(days=a)
            a = f'до {"" if dt.day > 9 else "0"}{dt.day}.{"" if dt.month > 9 else "0"}{dt.month}.{dt.year}'
            hs += f'{b}{a}\n'
            count += 1
            if count == 5:
                break
    if count == 0:
        hs = f"⚠ {format_push(user_)} ещё не был заражён мной, либо информация не найдена!"
    return nd.msg_op(2, hs, keep_forward_messages=1)


@dlp.register('еб', receive=True)
def eb(nd: ND):

    if 'reply' in nd.msg.keys() and nd.msg['reply']['text'].startswith('🦠') and nd.msg['reply']['from_id'] < 0:
        fwd_id = nd.msg['reply']['text'].split('[')[2].split('|')[0].replace('id', '')
        text = f'заразить [id{fwd_id}|беса]'
    elif 'reply' in nd.msg.keys() and nd.msg['reply']['text'].startswith('🕵‍♂') and nd.msg['reply']['from_id'] < 0:
        id_ = re.findall(r'\d+', str(nd.msg['reply']['text']))[2]
        text = f'заразить [id{id_}|беса]'
    else:
        uid = find_mention_by_message(nd.msg, nd.vk)
        text = f'заразить [id{uid}|беса]'
    nd.msg_op(1, text)
