# -*- coding: utf-8 -*-
from schedule import CITIES

DEFAULT_ANSWER = ('Не знаю что ответить. Я могу помочь оформить и купить билет на самолет между городами: '
                  + CITIES + '.')
MESSAGE_CONFIRMATION = (
    'Проверим Ваш заказ: \nВы заказали билет из города "{city_departure_print}" в город "{city_arrival_print}"'
    ' на рейс номер {user_flight} улетающий {user_flight_date}\n количество забронированных мест {seat}. '
    '\nВаше пожелание: "{comment}".\nВсе верно?\nЕсли все верно введите "Да", если не верно введите "Нет".')
MESSAGE_TRY_AGAIN = 'Вы можете начать все сначала введя команду /ticket'
MESSAGE_FAILURE_CITIES_0 = 'Из города "'
MESSAGE_FAILURE_CITIES_1 = '" в город "'
MESSAGE_FAILURE_CITIES_2 = ('" нет рейсов. Выберите другой город назначения или начните оформление '
                            'билетов заново командой /ticket')
MESSAGE_FAILURE_ARRIVAL_CITY = 'Неверное название города прибытия, укажите город из списка: ' + CITIES
DATE_JUMPER_TIME = ', время вылета: '

INTENTS = [
    {
        'name': 'Приветствие',
        'command': None,
        'token': ('прив', 'здравств', 'хай', 'hi', 'добры',),
        'scenario': None,
        'answer': 'Здравствуйте! Вас приветствует бот авиакомпании "Крутое пике"!',
    },
    {
        'name': 'Прощание',
        'command': None,
        'token': ('досвидан', 'пока', 'чао',),
        'scenario': None,
        'answer': 'До свидание! Спасибо, что воспользовались нашими услугами!',
    },
    {
        'name': 'Регистрация',
        'command': None,
        'token': ('купит', 'регистр', 'биле', 'оформит'),
        'scenario': 'Ticket issuance',
        'answer': None,
    }
]

COMMANDS = [
    {
        'name': 'Оформление билетов',
        'command': ('/ticket',),
        'action': 'Ticket issuance',
        'answer': None,
    },
    {
        'name': 'Справка',
        'command': ('/help',),
        'action': None,
        'answer': ('Бот для оформления и покупки билетов на самолеты между городами: '
                   + CITIES + ', введите команду /ticket для начала работы.'),
    },
]

SCENARIOS = {
    'Ticket issuance': {
        'first_step': 'step1',
        'steps': {
            'step1': {
                'text': 'Введите название города отправления',
                'failure text': 'Неверное название города отправления. Выберите один город из списка: ' + CITIES + '.',
                'handler': 'handle_city_departure',
                'next_step': 'step2',
            },
            'step2': {
                'text': 'Введите название города прибытия',
                'failure text': '{failure text}',
                'handler': 'handle_city_arrival',
                'next_step': 'step3',
            },
            'step3': {
                'text': 'Введите дату вылета в формате 01-05-2019',
                'failure text': 'Неверный формат даты или прошедшая дата, повторите ввод даты в формате 01-05-2019',
                'handler': 'handle_data',
                'next_step': 'step4',
            },
            'step4': {
                'text': ('Вывожу пять ближайших рейсов к дате {flight_date} из города "{city_departure_print}" в город '
                         '"{city_arrival_print}": {flights}\nВыберите рейс и введите его номер '
                         '(только четыре цифры) и через пробел дату в формате "01-01-2020".'),
                'failure text': 'Введите номер рейса и дату из предложенных вариантов',
                'handler': 'handle_flight',
                'next_step': 'step5',
            },
            'step5': {
                'text': 'Сколько мест Вы бронируете на указанный рейс?',
                'failure text': 'Количество бронируемых мест должно быть от 1-го до 5-ти.',
                'handler': 'handle_seat',
                'next_step': 'step6'
            },
            'step6': {
                'text': 'Если у Вас есть пожелание или комментарий, то введите его здесь',
                'failure text': None,
                'handler': 'handle_comment',
                'next_step': 'step7'
            },
            'step7': {
                'text': MESSAGE_CONFIRMATION,
                'failure text': ('Введите "Да" если все верно или "Нет", если есть ошибки в заказе. '
                                 'Ответ "Нет" сбросит все введенные данные'),
                'handler': 'handle_confirmation',
                'next_step': 'step8'
            },
            'step8': {
                'text': 'Введите номер своего телефона, начиная с "+", для связи с Вами.',
                'image': 'ticket_handle',
                'failure text': 'Введите корректный номер телефона',
                'handler': 'handle_telephone',
                'next_step': 'step9'
            },
            'step9': {
                'text': ('Спасибо, что воспользовались нашими услугами! Билет прикреплен к этому сообщению.'
                         'В ближайшее время с Вами свяжутся для окончания оформления билетов.'),
                'failure text': None,
                'handler': None,
                'next_step': None
            },
        },
    },
}

CITIES_PATTERNS = {
    'москва': ('маск', 'моск', 'маскв', 'москв',),
    'лондон': ('лонд', 'ланд', 'ландо', 'лондо',),
    'берлин': ('берл', 'бэрл', ',берли', 'бэрли',),
    'париж': ('пар', 'пари',),
    'мадрид': ('мадр', 'мадри',),
}
