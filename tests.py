# -*- coding: utf-8 -*-
from freezegun import freeze_time
import unittest
from copy import deepcopy
from unittest.mock import patch, Mock

from pony.orm import db_session, rollback
from vk_api.bot_longpoll import VkBotMessageEvent

import config
from bot import Bot
from utils import generate_ticket
import requests


def isolate_db(test_func):
    def wrapper(*args, **kwargs):
        with db_session:
            test_func(*args, **kwargs)
            rollback()

    return wrapper


class MyTestCase(unittest.TestCase):
    RAW = {'type': 'message_new', 'object': {'message': {'date': 1636892536, 'from_id': 525922826, 'id': 101, 'out': 0,
                                                         'peer_id': 525922826, 'text': 'Привет, Бот!',
                                                         'attachments': [],
                                                         'conversation_message_id': 95, 'fwd_messages': [],
                                                         'important': False, 'is_hidden': False, 'random_id': 0},
                                             'client_info': {'button_actions': ['text', 'vkpay', 'open_app', 'location',
                                                                                'open_link', 'callback',
                                                                                'intent_subscribe',
                                                                                'intent_unsubscribe'], 'keyboard': True,
                                                             'inline_keyboard': True, 'carousel': True, 'lang_id': 0}
                                             },
           'group_id': 206620859, 'event_id': 'eda4bbf7415277621ad984e84024e86cd4daaeb4'}

    INPUTS_1 = ['ку-ку!', 'привет', 'пока', '/help', '/ticket', 'пари', 'мадрид', '/ticket', 'qwerty', 'МАСКВА',
                'йцукен',
                'бЕРЛИ', '10/01/2020', 'ой!', '01-01-2020', '10-01-2022', '2030-11', 'фывапр', '2030 11-01-2022', '10',
                '3', 'комментарий', 'No', 'Нет', ]
    INPUTS_2 = ['/help', 'биле', 'ландон', 'москва', '20-05-2022', '1055 21-05-2022', '2', 'ку-ка-ре-ку!', 'Да',
                '12345', '12345678901', '+1234567890', ]
    EXPECTED_FLIGHTS_1 = ('\nРейс № KP-2020 вылетающий 10-01-2022 в 05:00'
                          '\nРейс № KP-2020 вылетающий 11-01-2022 в 05:00'
                          '\nРейс № KP-2030 вылетающий 11-01-2022 в 16:20'
                          '\nРейс № KP-2000 вылетающий 11-01-2022 в 20:05'
                          '\nРейс № KP-2020 вылетающий 12-01-2022 в 05:00')
    EXPECTED_FLIGHTS_2 = ('\nРейс № KP-1056 вылетающий 20-05-2022 в 17:30'
                          '\nРейс № KP-1056 вылетающий 21-05-2022 в 17:30'
                          '\nРейс № KP-1055 вылетающий 21-05-2022 в 21:05'
                          '\nРейс № KP-1056 вылетающий 22-05-2022 в 17:30'
                          '\nРейс № KP-1047 вылетающий 23-05-2022 в 03:20')
    EXPECTED_OUTPUTS_1 = [config.DEFAULT_ANSWER,
                          config.INTENTS[0]['answer'],
                          config.INTENTS[1]['answer'],
                          config.COMMANDS[1]['answer'],
                          config.SCENARIOS['Ticket issuance']['steps']['step1']['text'],
                          config.SCENARIOS['Ticket issuance']['steps']['step2']['text'],
                          config.MESSAGE_FAILURE_CITIES_0 + 'Париж' + config.MESSAGE_FAILURE_CITIES_1 + 'Мадрид' +
                          config.MESSAGE_FAILURE_CITIES_2,
                          config.SCENARIOS['Ticket issuance']['steps']['step1']['text'],
                          config.SCENARIOS['Ticket issuance']['steps']['step1']['failure text'],
                          config.SCENARIOS['Ticket issuance']['steps']['step2']['text'],
                          config.MESSAGE_FAILURE_ARRIVAL_CITY,
                          config.SCENARIOS['Ticket issuance']['steps']['step3']['text'],
                          config.SCENARIOS['Ticket issuance']['steps']['step3']['failure text'],
                          config.SCENARIOS['Ticket issuance']['steps']['step3']['failure text'],
                          config.SCENARIOS['Ticket issuance']['steps']['step3']['failure text'],
                          config.SCENARIOS['Ticket issuance']['steps']['step4']['text'].format(
                              flight_date='10-01-2022',
                              city_departure_print='Москва',
                              city_arrival_print='Берлин',
                              flights=EXPECTED_FLIGHTS_1),
                          config.SCENARIOS['Ticket issuance']['steps']['step4']['failure text'],
                          config.SCENARIOS['Ticket issuance']['steps']['step4']['failure text'],
                          config.SCENARIOS['Ticket issuance']['steps']['step5']['text'],
                          config.SCENARIOS['Ticket issuance']['steps']['step5']['failure text'],
                          config.SCENARIOS['Ticket issuance']['steps']['step6']['text'],
                          config.SCENARIOS['Ticket issuance']['steps']['step7']['text'].format(
                              city_departure_print='Москва',
                              city_arrival_print='Берлин',
                              user_flight='KP-2030',
                              user_flight_date='11-01-2022' + config.DATE_JUMPER_TIME + '16:20',
                              seat='3',
                              comment='комментарий'),
                          config.SCENARIOS['Ticket issuance']['steps']['step7']['failure text'],
                          config.MESSAGE_TRY_AGAIN,
                          ]
    EXPECTED_OUTPUTS_2 = [config.COMMANDS[1]['answer'],
                          config.SCENARIOS['Ticket issuance']['steps']['step1']['text'],
                          config.SCENARIOS['Ticket issuance']['steps']['step2']['text'],
                          config.SCENARIOS['Ticket issuance']['steps']['step3']['text'],
                          config.SCENARIOS['Ticket issuance']['steps']['step4']['text'].format(
                              flight_date='20-05-2022',
                              city_departure_print='Лондон',
                              city_arrival_print='Москва',
                              flights=EXPECTED_FLIGHTS_2),
                          config.SCENARIOS['Ticket issuance']['steps']['step5']['text'],
                          config.SCENARIOS['Ticket issuance']['steps']['step6']['text'],
                          config.SCENARIOS['Ticket issuance']['steps']['step7']['text'].format(
                              city_departure_print='Лондон',
                              city_arrival_print='Москва',
                              user_flight='KP-1055',
                              user_flight_date='21-05-2022' + config.DATE_JUMPER_TIME + '21:05',
                              seat='2',
                              comment='ку-ка-ре-ку!'),
                          config.SCENARIOS['Ticket issuance']['steps']['step8']['text'],
                          config.SCENARIOS['Ticket issuance']['steps']['step8']['failure text'],
                          config.SCENARIOS['Ticket issuance']['steps']['step8']['failure text'],
                          config.SCENARIOS['Ticket issuance']['steps']['step9']['text'],
                          ]
    CONTEXT_EXAMPLE = {'city_departure_print': 'Лондон',
                       'city_arrival_print': 'Москва',
                       'user_date': '21-05-2022',
                       'user_time': '21:05',
                       'user_flight': 'KP-1055',
                       'seat': '2',
                       }

    def test_run(self):
        count = 5
        obj = {'test': 100}
        events = [obj] * count
        long_poller_mock = Mock()
        long_poller_mock.listen = Mock(return_value=events)
        with patch('bot.vk_api.VkApi'):
            with patch('bot.VkBotLongPoll', return_value=long_poller_mock):
                bot = Bot('', '')
                bot.events_work = Mock()
                bot.send_image = Mock()
                bot.run()
        self.assertEqual(bot.events_work.assert_called(), None)
        self.assertEqual(bot.events_work.call_count, count)
        self.assertEqual(bot.events_work.assert_any_call(event=obj), None)

    @isolate_db
    @freeze_time("2022-01-10")
    def test_run_reset_user(self):
        send_mock = Mock()
        api_mock = Mock()
        api_mock.messages.send = send_mock
        events = []
        for input_text in self.INPUTS_1:
            event = deepcopy(self.RAW)
            event['object']['message']['text'] = input_text
            events.append(VkBotMessageEvent(raw=event))

        long_poller_mock = Mock()
        long_poller_mock.listen = Mock(return_value=events)

        with patch('bot.VkBotLongPoll', return_value=long_poller_mock):
            bot = Bot('', '')
            bot.vk_session = api_mock
            bot.send_image = Mock()
            bot.run()

        assert send_mock.call_count == len(self.INPUTS_1)
        real_output = []
        for call in send_mock.call_args_list:
            args, kwargs = call
            real_output.append(kwargs['message'])

        assert real_output == self.EXPECTED_OUTPUTS_1

    @isolate_db
    @freeze_time("2022-01-10")
    def test_run_to_end(self):
        send_mock = Mock()
        api_mock = Mock()
        api_mock.messages.send = send_mock
        events = []
        for input_text in self.INPUTS_2:
            event = deepcopy(self.RAW)
            event['object']['message']['text'] = input_text
            events.append(VkBotMessageEvent(raw=event))

        long_poller_mock = Mock()
        long_poller_mock.listen = Mock(return_value=events)

        with patch('bot.VkBotLongPoll', return_value=long_poller_mock):
            bot = Bot('', '')
            bot.vk_session = api_mock
            bot.send_image = Mock()
            bot.run()

        assert send_mock.call_count == len(self.INPUTS_2)
        real_output = []
        for call in send_mock.call_args_list:
            args, kwargs = call
            real_output.append(kwargs['message'])

        assert real_output == self.EXPECTED_OUTPUTS_2

    def test_generate_ticket(self):
        with open('files/example_avatar.png', mode='rb') as example_avatar:
            avatar_mock = Mock()
            avatar_mock.content = example_avatar.read()
        with patch('requests.get', return_value=avatar_mock):
            ticket_image = generate_ticket(ticket_data=self.CONTEXT_EXAMPLE)
        ticket = ticket_image.read()
        with open('files/example_ticket.png', mode='rb') as example_ticket:
            expected_ticket = example_ticket.read()

        assert ticket == expected_ticket


if __name__ == '__main__':
    unittest.main()
