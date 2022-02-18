# -*- coding: utf-8 -*-
import re
from datetime import datetime, timedelta
import config
import schedule
from utils import dispatcher, generate_ticket

pattern_city = r'[А-Яа-я]\w+'
pattern_flight = r'KP-([0-9]*)'
pattern_date = r'[\d-]{10}'
pattern_time = r'[\d:]{5}'
test_answer = '4031 05-01-2022'
pattern_flight_user = r'[\d]{4}'


def handle_city_departure(text, context):
    city = check_city(text)
    if city:
        context['city_departure'] = city
        context['city_departure_print'] = context['city_departure'].capitalize()
        return True
    else:
        return False


def handle_city_arrival(text, context):
    city = check_city(text)
    if city:
        if city in schedule.FLIGHT_SCHEDULE[context['city_departure']]:
            context['city_arrival'] = city
            context['city_arrival_print'] = context['city_arrival'].capitalize()
            return True
        else:
            context['city_arrival'] = city
            context['failure text'] = config.MESSAGE_FAILURE_CITIES_0 + context[
                'city_departure_print'] + config.MESSAGE_FAILURE_CITIES_1 + context[
                                          'city_arrival'].capitalize() + config.MESSAGE_FAILURE_CITIES_2
            return False
    else:
        context['failure text'] = config.MESSAGE_FAILURE_ARRIVAL_CITY
        return False


def handle_data(text, context):
    try:
        date_user = datetime.strptime(text, '%d-%m-%Y')
    except ValueError:
        return False
    date_now = datetime.today()
    time_delta = date_now - date_user
    one_day = timedelta(days=1)
    if time_delta > one_day:
        return False

    context['flight_date'] = date_user.strftime('%d-%m-%Y')
    dispatcher(text=text, context=context)
    return True


def handle_command(command):
    for intent in config.COMMANDS:
        if any(text in command for text in intent['command']):
            return intent
    else:
        return False


def handle_seat(text, context):
    if text.isdigit():
        if 1 <= int(text) <= 5:
            context['seat'] = text
            return True
    return False


def handle_comment(text, context):
    context['comment'] = text
    return True


def handle_confirmation(text, context):
    if text == 'Да':
        return True
    elif text == 'Нет':
        return True
    else:
        return False


def handle_telephone(text, context):
    if text[0] != '+':
        return False
    elif text[1:].isdigit() and len(text) >= 10:
        context['telephone'] = text
        return True
    else:
        return False


def handle_flight(text, context):
    text_flights = context['flights']
    matched_flights = re.findall(pattern_flight, text_flights)
    matched_dates = re.findall(pattern_date, text_flights)
    matched_times = re.findall(pattern_time, text_flights)

    matched_flight_user = re.search(pattern_flight_user, text)
    matched_date_user = re.search(pattern_date, text)
    if matched_flight_user is None or matched_date_user is None:
        return False

    for i in range(len(matched_flights)):
        if matched_flights[i] == matched_flight_user.group(0):
            if matched_dates[i] == matched_date_user.group(0):
                context['user_flight'] = 'KP-' + matched_flights[i]
                context['user_flight_date'] = matched_dates[i] + config.DATE_JUMPER_TIME + matched_times[i]
                context['user_date'] = matched_dates[i]
                context['user_time'] = matched_times[i]
                return True
    return False


def check_city(word):
    matched = re.search(pattern_city, word)
    if matched is None:
        return False
    word = matched.group().lower()[:-1]
    for city, variants in config.CITIES_PATTERNS.items():
        if any(sample in word for sample in variants):
            return city
    else:
        return False


def ticket_handle(context):
    return generate_ticket(ticket_data=context)
