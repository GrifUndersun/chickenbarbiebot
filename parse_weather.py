import datetime
import json

from config import WEATHER_TOKEN
import requests

api_key = WEATHER_TOKEN


def get_weather(city):
    try:
        r = requests.get(
            f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru'
        )
        data = r.json()

        name = data['name']
        delta_time = datetime.datetime.fromtimestamp(data['dt'])
        description = data['weather'][0]['description']
        humidity = data['main']['humidity']
        temp_max = data['main']['temp_max']
        temp_min = data['main']['temp_min']
        temp = '{0:+3.0f}'.format(data['main']['temp'])
        wind_speed = data['wind']['speed']
        wind_deg = data['wind']['deg']
        pressure = round(data['main']['pressure'] * 0.750063755419211, 2)
        sunrise = datetime.datetime.fromtimestamp(data['sys']['sunrise'])
        sunset = datetime.datetime.fromtimestamp(data['sys']['sunset'])
        day_len = datetime.datetime.strptime(str(sunset - sunrise), "%H:%M:%S")
        direction = ''
        if wind_deg > 337 or wind_deg < 23:
            direction = 'С'
        elif 23 <= wind_deg < 68:
            direction = 'СВ'
        elif 68 <= wind_deg < 113:
            direction = 'В'
        elif 113 <= wind_deg < 158:
            direction = 'ЮВ'
        elif 158 <= wind_deg < 203:
            direction = 'Ю'
        elif 203 <= wind_deg < 248:
            direction = 'ЮЗ'
        elif 248 <= wind_deg < 293:
            direction = 'З'
        elif 293 <= wind_deg < 338:
            direction = 'СЗ'
        result = f'🌤 Погода в городе {name} на данный момент\n' \
                 f'{description.capitalize()}\n\n' \
                 f'Температура сейчас: {temp}℃\n\n' \
                 f'🌇 Восход/Закат в {sunrise.strftime("%H:%M")}/{sunset.strftime("%H:%M")}\n' \
                 f'Продолжительность дня: {day_len.strftime("%H:%M")}\n\n' \
                 f'💨 Ветер: {wind_speed} м/с, {direction}\n' \
                 f'Давление: {pressure} мм рт. ст.\n' \
                 f'Влажность: {humidity}%\n\n' \
                 f'Данные обновлены в {delta_time.strftime("%d.%m.%Y %H:%M")}'
        return result
    except Exception as e:
        print('Exception (weather): ', e)
        return None


def get_forecast(city):
    try:
        res = requests.get(
            f"https://api.openweathermap.org/data/2.5/forecast?q={city}&cnt=8&appid={api_key}&units=metric"
            f"&lang=ru")
        data_list = res.json()
        data = data_list['list']
        # pprint(data)
        date = datetime.datetime.fromtimestamp(data[0]["dt"])
        r = datetime.datetime.fromisoformat(data[0]["dt_txt"]).strftime("%H:%M")
        # print(r)
        result = f'🌤 Погода на {date.strftime("%d.%m.%Y")}'
        for i in data:
            day_time = datetime.datetime.fromisoformat(i["dt_txt"]).strftime("%H:%M")
            temp = '{0:+3.0f}℃'.format(i['main']['temp'])
            dis = i["weather"][0]["description"].capitalize()
            # print(day_time, temp, dis)
            stroke = f'\n\n{day_time} {temp} {dis}'
            result += stroke
        print(result)
        return result
    except Exception as e:
        print("Exception (forecast):", e)
        return None


def openDB():
    try:
        with open('database_users_weather.json', 'r') as f:
            usersDB = json.load(f)
        return usersDB
    except Exception as e:
        print(e)
        return []


def saveDB(teleid, city, mailing):
    usersDB = openDB()
    new_db = []
    for x in usersDB:
        if x['id'] != teleid:
            print('p')
            new_db.append(x)

    new_db.append({
        'id': int(teleid),
        'city': str(city).capitalize(),
        'mailing': bool(mailing)
    })
    with open('database_users_weather.json', 'w') as f:
        json.dump(new_db, f)
    result = openDB()
    return result


def main():
    get_forecast('Архангельск')


if __name__ == '__main__':
    print(get_weather('Архангельск'))
