import time
import datetime
import requests

from . import dlp, ND


@dlp.register('погода', receive=True)
def weather(nd: ND):
    city = nd.msg['args'][0]
    api_key = "8ccf72ecedd6eb76311755cb76799810"
    data = requests.get(
        f'http://api.openweathermap.org/data/2.5/weather',
        params={'q': city, 'appid': api_key, 'units': 'metric', 'lang': 'ru'}
    ).json()
    try:
        text = f"""
	💬 Погода в {data['name']}

	🌡️ Температура: {data['main']['temp']}°С
	☀️ Ощущается как: {data['main']['feels_like']}°С
	❄️ Макс/мин: {data['main']['temp_max']}°С/{data['main']['temp_min']}°С
	☁️ Погода: {data['weather'][0]['description'].capitalize()}
	🌀 Ветер: {data['wind']['speed']} м/с
	💧 Влажность: {data['main']['humidity']}%

	🌆 Закат: {str(datetime.datetime.fromtimestamp(data['sys']['sunset']))[11:]}
	🌅 Рассвет: {str(datetime.datetime.fromtimestamp(data['sys']['sunrise']))[11:]}

	☄ Давление: {data['main']['pressure']} мбар
	👀 Видимость: {data['visibility']}м""".replace("	", "")
        nd.msg_op(2, f"{text}")
    except Exception:
        time.sleep(0.5)
        nd.msg_op(2, f'Город не найден!\nПроверьте запрос!')