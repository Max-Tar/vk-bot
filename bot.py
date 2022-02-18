# -*- coding: utf-8 -*-
import logging
from random import randint

import requests
import vk_api
from pony.orm import db_session
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

import config
import handlers
from models import UserState, Registration

try:
    import settings
except ImportError:
    exit('DO cp settings.py.default settings.py and set TOKEN!')

log = logging.getLogger(name='bot')


def configure_logging():
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter('%(levelname)s %(message)s'))
    log.addHandler(stream_handler)
    stream_handler.setLevel(logging.INFO)

    file_handler = logging.FileHandler(filename='bot.log', mode='w', encoding='utf8', delay=False)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%d-%m-%Y, %H:%M'))
    log.addHandler(file_handler)
    file_handler.setLevel(logging.DEBUG)
    log.setLevel(logging.DEBUG)


class Bot:
    """
    Bot продажи билетов для vk.com
    Use python3.7
    """

    def __init__(self, group_id_bot, token_bot):
        """
        :param group_id_bot: group id из группа vk
        :param token_bot: token из группа vk
        """
        self.group_id = group_id_bot
        self.token = token_bot
        self.vk = vk_api.VkApi(token=self.token)
        self.long_poller = VkBotLongPoll(vk=self.vk, group_id=self.group_id)
        self.vk_session = self.vk.get_api()

    def run(self):
        """
        Запуск бота
        :return: None
        """
        for event in self.long_poller.listen():
            log.debug('Произошло событие!')
            try:
                self.events_work(event=event)
            except Exception:
                log.exception('Произошла ошибка в обработке')

    @db_session
    def events_work(self, event):
        """
        Обработка сообщения
        :param event: VkBotMessageEvent object
        :return: None
        """
        if event.type != VkBotEventType.MESSAGE_NEW:
            log.info(f'Неизвестное событие: {event.type}')
            return

        user_id = str(event.message.peer_id)
        text = event.message.text
        state = UserState.get(user_id=user_id)

        command_name = handlers.handle_command(command=text)
        if command_name:
            self.command(directive=command_name, user_id=user_id, state=state)
            log.debug(f'User make command {command_name}')

        elif state is not None:
            if state.step_name == 'step7' and text == 'Нет':
                # reset due to user input error
                self.send_data(text=config.MESSAGE_TRY_AGAIN, user_id=user_id)
                state.delete()
            else:
                log.debug(f'continue scenario {state.scenario_name}')
                self.continue_scenario(text=text, state=state, user_id=user_id)

        else:
            for intent in config.INTENTS:
                log.debug(f'User get {intent}')
                if any(token in text for token in intent['token']):
                    if intent['answer']:
                        self.send_data(text=intent['answer'], user_id=user_id)
                    else:
                        self.start_scenario(user_id=user_id, scenario_name=intent['scenario'])
                    break
            else:
                self.send_data(text=config.DEFAULT_ANSWER, user_id=user_id)

    def start_scenario(self, user_id, scenario_name):
        scenario = config.SCENARIOS[scenario_name]
        first_step = scenario['first_step']
        step = scenario['steps'][first_step]
        text_to_send = step['text']
        UserState(user_id=user_id, scenario_name=scenario_name, step_name=first_step, context={})
        self.send_data(text=text_to_send, user_id=user_id)

    def continue_scenario(self, text, state, user_id):
        steps = config.SCENARIOS[state.scenario_name]['steps']
        step = steps[state.step_name]
        handler = getattr(handlers, step['handler'])
        if handler(text=text, context=state.context):
            next_step = step['next_step']
            text_to_send = steps[next_step]['text'].format(**state.context)
            self.send_data(text=text_to_send, user_id=user_id, step=step, context=state.context)
            if steps[next_step]['next_step']:
                state.step_name = step['next_step']
            else:
                log.info('Оформлен заказ билета из города "{city_departure}" в город "{city_arrival}" на дату '
                         '{user_flight_date}, номер рейса: {user_flight}, количество мест: {seat}, '
                         'комментарий пассажира: {comment}, телефон: {telephone}'.format(**state.context))
                Registration(city_departure=state.context['city_departure_print'],
                             city_arrival=state.context['city_arrival_print'],
                             user_flight_date=state.context['user_flight_date'],
                             user_flight=state.context['user_flight'],
                             seat=state.context['seat'],
                             comment=state.context['comment'],
                             telephone=state.context['telephone'])
                state.delete()
        else:
            text_to_send = step['failure text'].format(**state.context)
            self.send_data(text=text_to_send, user_id=user_id)

    def command(self, directive, user_id, state):
        if directive['action']:
            if state is not None:
                state.delete()
            self.start_scenario(user_id=user_id, scenario_name=directive['action'])
        else:
            self.send_data(text=directive['answer'], user_id=user_id)

    def send_data(self, text, user_id, step=None, context=None):
        if step is not None and 'image' in step:
            handler = getattr(handlers, step['image'])
            image = handler(context)
            self.send_image(image=image, user_id=user_id)
        self.send_text(text=text, user_id=user_id)

    def send_image(self, image, user_id):
        upload_url = self.vk_session.photos.getMessagesUploadServer()['upload_url']
        upload_data = requests.post(upload_url, files={'photo': ('image.png', image, 'image/png')}).json()
        image_data = self.vk_session.photos.saveMessagesPhoto(**upload_data)
        owner_id = image_data[0]['owner_id']
        media_id = image_data[0]['id']
        attachment = f'photo{owner_id}_{media_id}'
        self.vk_session.messages.send(attachment=attachment,
                                      random_id=randint(0, 2 ** 20),
                                      peer_id=user_id)

    def send_text(self, text, user_id):
        self.vk_session.messages.send(message=text,
                                      random_id=randint(0, 2 ** 20),
                                      peer_id=user_id)


if __name__ == '__main__':
    configure_logging()
    bot = Bot(group_id_bot=settings.GROUP_ID, token_bot=settings.TOKEN)
    bot.run()
