from typing import Union
from lib.wtflog import get_boy_for_warden
import socket
import json
import sys

logger = get_boy_for_warden('LP', 'Модуль управления LP')

_lp_ports = []

for i, arg in enumerate(sys.argv):
    if '-lp' in arg:
        _lp_ports.append(int(sys.argv[i+1]))

if _lp_ports == []:
    print('Не указаны порты LP модулей (аргументы -lp)')
    sys.exit()

_TO_CATCHER = []
for port in _lp_ports:
    _TO_CATCHER.append(('localhost', port))

def send_to_lp(method: str, catcher: int = 0, **kwargs) -> Union[dict, None]:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(_TO_CATCHER[catcher])
    to_send = {'method': method}
    to_send.update(kwargs)
    data = json.dumps(to_send, ensure_ascii=False)
    client.send(bytes(data, encoding="utf-8"))
    logger.debug(f'Отправлено ловцу {catcher}: {data}')
    data = client.recv(4096)
    client.close()
    try:
        return json.loads(data)
    except Exception:
        pass
