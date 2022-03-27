import time
import psutil
import inspect
import platform
from datetime import datetime

from vk.user_bot import dlp, ND
from vk.user_bot.utils import find_mention_by_message, get_index
from vk.user_bot.service import vk_users, lp_failed, vk_lp_running
from longpoll.lp import send_to_lp
from database.billing_manager import catchers
from database.client import method

from .admin import check_admin


@dlp.register('системинфо', 'хост', receive=True)
@dlp.wrap_handler(check_admin)
def check_system(nd: ND):
    nd.msg_op(2, "⌛Вычисляю данные...")
    my_system = platform.uname()
    totalsize = psutil.disk_usage('/').total / (2 ** 30)
    freesize = psutil.disk_usage('/').free / (2 ** 30)
    text = f''' 🚀Информация о сервере🚀
    🖥 Система: {my_system.system}
    🐍 Версия питона: {platform.python_version()}
    📈 Нагрузка ЦП: {psutil.cpu_percent(1)}%
    📈 Количество ядер: {psutil.cpu_count()}
    📗 Загрузка ОЗУ: {psutil.virtual_memory()[2]}%
    💽 Диск: {round(freesize, 1)}/{round(totalsize, 1)} GB
    '''
    nd.msg_op(2, f'{inspect.cleandoc(text)}')
