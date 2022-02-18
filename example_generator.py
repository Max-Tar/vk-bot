from io import BytesIO

import requests
from PIL import Image, ImageDraw, ImageFont, ImageColor

CONTEXT_EXAMPLE_GENERATOR = {'city_departure_print': 'Лондон',
                             'city_arrival_print': 'Москва',
                             'user_date': '21-05-2022',
                             'user_time': '21:05',
                             'user_flight': 'KP-1055',
                             'seat': '2',
                             }


def generate_ticket(ticket_data):
    size_font = 14
    coord = {'city_departure_print': (45, 128), 'city_arrival_print': (45, 197), 'user_date': (280, 325),
             'user_time': (430, 325), 'user_flight': (45, 265), 'seat': (60, 325)}

    ticket_image = Image.open('files/ticket_template.png')
    draw = ImageDraw.Draw(ticket_image)
    font = ImageFont.truetype('files/font_for_ticket.ttf', size=size_font)
    for key, item in coord.items():
        draw.text(xy=item, text=ticket_data[key], font=font, fill=ImageColor.colormap['black'], stroke_fill=0)

    city_dep = ticket_data['city_departure_print']
    city_arr = ticket_data['city_arrival_print']

    data_avatar = requests.get(
        url=f'https://eu.ui-avatars.com/api//?size=100&background=019cd3&name={city_dep}+{city_arr}')
    avatar_file = BytesIO(data_avatar.content)
    avatar = Image.open(avatar_file)

    data_avatar_default = requests.get(
        url='https://eu.ui-avatars.com/api//?size=100&background=019cd3&name=Крутое+Пике')
    avatar_default_file = BytesIO(data_avatar_default.content)
    avatar_default = Image.open(avatar_default_file)

    ticket_image.paste(avatar, box=(420, 80))

    with open('files/example_avatar.png', mode='wb') as file:
        avatar.save(file, 'png')
        # file.write(data_avatar.content)
    with open('files/default_avatar.png', mode='wb') as file:
        avatar_default.save(file, 'png')
    #        file.write(avatar_default_file.content)
    with open('files/example_ticket.png', mode='wb') as file:
        ticket_image.save(file, 'png')


if __name__ == '__main__':
    generate_ticket(ticket_data=CONTEXT_EXAMPLE_GENERATOR)
