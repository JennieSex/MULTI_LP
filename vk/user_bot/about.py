from database import __version__
from database.client import method
from vk.user_bot.admin.warnings import get_warns
from . import dlp


@dlp.register('info', 'инфа', 'инфо')
def about(nd):
    db = nd.db
    settings = db.settings_get()
    message = f"""
    Случайный бот v{__version__}

    игнорируемых пользователей: {len(settings.ignore_list)}
    """.replace('    ', '') + get_warns()

    nd.vk.msg_op(2, nd[3], message, nd[1])
    return "ok"
