# -*- coding: utf-8 -*- 
#Вывод текущей локали системы и возможно фикс
import sys

import locale

print('Параметры кодировки ДО: ')
print(sys.getfilesystemencoding())

print(locale.getpreferredencoding())
sys.stdout.reconfigure(encoding='utf-8')
print('Параметры кодировки ПОСЛЕ: ')
print(sys.getfilesystemencoding())
print(locale.getpreferredencoding())


import datetime
import re
import time
import asyncio
import requests
import random
import platform
import json
import dpath
import dpath.util

from dpath.util import *
from datetime import *
from shutil import *
import shutil
import itertools
from datetime import datetime


from vk.user_bot import ND, dlp
from vk.user_bot.utils import find_mention_by_message, format_push


###Начало говнокода ежа пп
##05.06.2021 17:45
def pp(searchpat):
    try:
        textpatog = searchpat
    except Exception as Err:                                                                                                          
        print(Err) 
    try:
        idforzbol = nd.vk('messages.search', count=100, q=f'Служба безопасности лаборатории подверг заражению патогеном {textpatog}')['items']
        try:
            deleteforw = dpath.util.delete(idforzbol, '**/fwd_messages') 
        except:
            print('ok')
        try:
            deleterepl = dpath.util.delete(idforzbol, '**/reply_message')
        except:
            print('ok')
        zarazadone = dpath.util.values(idforzbol, '*/text')
        zarazadone = ' '.join(zarazadone) 
        poiskpatogena = re.findall(r'Организатор заражения: (\[id\d{1,}\|.*\])', zarazadone)
        dupes = {}
        for el, group in itertools.groupby(sorted(poiskpatogena)):
            countdup = len(list(group))
            if countdup >= 1:  
                dupes[el] = countdup
        stropt = '' 
        dupeslist = list(dupes) 
        print(dupeslist)
        keychect = 0
        sortstring = []
        podschet = len(poiskpatogena)
        for patogenskey in dupes: 
            try:
                inde = dupeslist[keychect]
                valuekey = dupes[inde] 
                valuekey = (valuekey/podschet)*100
                valuekey = round(valuekey, 2)  
                sortstring.append(f'{valuekey}%: {inde}') 
                keychect += 1
            except:
                continue
        preparesort = sorted(sortstring, reverse=True)
        for keyssorted in preparesort:
            stropt += f'{keyssorted}\n'
        poiskpatogena = stropt
        if poiskpatogena == '' or poiskpatogena == ' ':
            pp_answ = '⚠ Не найден...'
            return pp_answ
        else:
            pp_answ = f'Всё что нашёл по патогену {textpatog} (beta):\n{poiskpatogena}' 
            return pp_answ
        
    except Exception as Err: 
        pp_answ = f'Ошибище: {Err}'
        return pp_answ

@dlp.register('пп')
def pisk_patogena(nd: ND):
    
    nd.msg_op(1, f"{pp_botl_answ}") 
###Конец говнокода ежа
    
        