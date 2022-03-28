from vk.user_bot import dlp, ND


smiles = {
    'камень': '🗿',
    'зло': '👺',
    'зломаска': '👺',
    'ноготочки': '💅🏻',
    'рожа': '🥺',
    'морда': '👁👄👁',
    'шок': '😳',
    'солнце': '🌝',
    'уву': '👉👈',
    'пж': '🥺👉👈',
    'клоун': '🤡',
    'во': '👍🏻',
    'лайк': '👍',
    'диз': '👎',
    'пис': '✌',
    'ок': '👌🏻',
    'хм': '🤔',
    'ауф': '☝',
    'еее': '🤘🏻',
    'крутяк': '😳👍🏻',
    'лю': '❤',
    'сердце': '❤',
    'еша': '💚',
    'ксю': '🖤',
    ')': '🙂',
    'хе': '🌚',
    'гей': '🏳‍🌈',
    'пон': '🚬',
    'утка': '🦆',
    'картошка': '🥔',
    'глаз': '👁',
    'договорились': '🤝🏻',
    'легущька': '🐤',
    'бзз': '🐝',
    'паук': '🕷',
    'пес': '🐶',
    'сова': '🦉',
    'мда': '😐',
    'хы': '☺',
    'поиск': '🔎',
    'пока': '🔪',
    'эх': '😔✊',
    'хз': '¯\_(ツ)_/¯'
    # '': '',
}


@dlp.register('смайлы')
def smiles_count(nd: ND):
    nd.msg_op(f'Всего смайлов: {len(smiles.keys())}')


@dlp.register(*smiles.keys(), receive=True)
def smiles_misc(nd: ND):
    qty = 1
    if nd.msg['args']:
        if nd.msg['args'][0].isdigit():
            qty = int(nd.msg['args'].pop(0))

    if nd.msg['payload']:
        nd.msg['payload'] = '\n' + nd.msg['payload']

    message = f"{' '.join(nd.msg['args'])}{nd.msg['payload']} {qty * smiles[nd.msg['command']]}"  # noqa
    if len(message) > 1100:
        return nd.msg_op(1, 'а че так много 😳', reply_to=nd[1])

    nd.vk.msg_op(2, nd[3], message, nd[1], keep_forward_messages=1,
                 attachment=','.join(nd.msg['attachments']))
