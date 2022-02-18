# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from io import BytesIO

import requests
from PIL import Image, ImageDraw, ImageFont, ImageColor

from schedule import FLIGHT_SCHEDULE

CONTEXT_TICKET = {'city_departure_print': 'Лондон',
                  'city_arrival_print': 'Москва',
                  'user_date': '21-05-2022',
                  'user_time': '21:05',
                  'user_flight': 'KP-1055',
                  'seat': '2',
                  }

COORD = {'city_departure_print': (45, 128), 'city_arrival_print': (45, 197), 'user_date': (280, 325),
         'user_time': (430, 325), 'user_flight': (45, 265), 'seat': (60, 325)}

URL_FONT = 'files/font_for_ticket.ttf'
URL_TICKET_TEMPLATE = 'files/ticket_template.png'
URL_DEFAULT_AVATAR = 'files/default_avatar.png'


def flight_search(date_flight, flight_name, flight_option):
    date_time_now = datetime.today()
    time_count = date_flight
    oneday = timedelta(days=1)
    i = 0
    schedule_for_user = []
    while i < 5:
        if flight_option['periodicity'] == 'weekly':
            day_control = time_count.isoweekday()
        else:
            day_control = time_count.day
        if day_control in flight_option['day']:
            time = datetime(year=time_count.year, month=time_count.month, day=time_count.day,
                            hour=int(flight_option['time'][0:2]),
                            minute=int(flight_option['time'][3:]))
            if time >= date_time_now:
                schedule_for_user.append({'flight': flight_name, 'date': time})
                i += 1
        time_count += oneday
    return schedule_for_user


def dispatcher(text, context):
    schedule = FLIGHT_SCHEDULE[context['city_departure']][context['city_arrival']]
    date_time_flight = datetime.strptime(context['flight_date'], '%d-%m-%Y')
    total_schedule = []
    for flight, option in schedule.items():
        total_schedule += flight_search(date_flight=date_time_flight, flight_name=flight, flight_option=option)

    total_schedule = sorted(total_schedule, key=lambda k: k['date'])[0:5]
    flights_to_send = ''
    for element in total_schedule:
        flights_to_send += (f'\nРейс № {element["flight"]} вылетающий {element["date"].strftime("%d-%m-%Y")} '
                            f'в {element["date"].strftime("%H:%M")}')

    context['flights'] = flights_to_send
    return True


def generate_ticket(ticket_data):
    size_font = 14
    ticket_image = Image.open(URL_TICKET_TEMPLATE)
    draw = ImageDraw.Draw(ticket_image)
    font = ImageFont.truetype(URL_FONT, size=size_font)
    for key, item in COORD.items():
        draw.text(xy=item, text=ticket_data[key], font=font, fill=ImageColor.colormap['black'], stroke_fill=0)

    city_dep = ticket_data['city_departure_print']
    city_arr = ticket_data['city_arrival_print']
    try:
        data_avatar = requests.get(
            url=f'https://eu.ui-avatars.com/api//?size=100&background=019cd3&name={city_dep}+{city_arr}')
        avatar_file = BytesIO(data_avatar.content)
    except requests.exceptions.ConnectionError:
        avatar_file = URL_DEFAULT_AVATAR
    avatar = Image.open(avatar_file)
    ticket_image.paste(avatar, box=(420, 80))

    temp_file = BytesIO()
    ticket_image.save(temp_file, 'png')
    temp_file.seek(0)
    #    ticket_image.show()
    return temp_file


if __name__ == '__main__':
    generate_ticket(ticket_data=CONTEXT_TICKET)
