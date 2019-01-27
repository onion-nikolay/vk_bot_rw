import logging
import os

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.exceptions import AuthError, ApiError

from vk_requests import get_managers, send_message
from game import Game


def get_group_id(logger):
    try:
        with open('data/id') as f:
            group_id = f.readline()
            f.close()
    except FileNotFoundError:
        logger.info('No group id found.')
        try:
            group_id = int(input('Please print id of VK group: '))
        except ValueError:
            logger.error('Group id should be a number!')
            return -1
        with open('data/id', 'w') as f:
            f.write(str(group_id))
            f.close()
    return group_id


def get_token(logger):
    try:
        with open('data/key') as f:
            token = f.readline()
            f.close()
    except FileNotFoundError:
        logger.info('No token found.')
        token = input('Please print token of VK group: ')
        with open('data/key', 'w') as f:
            f.write(token)
            f.close()
    return token


def new_logger(name='main'):
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    if logger.hasHandlers():
        logger.handlers.clear()

    file_handler = logging.FileHandler("{}.log".format(name))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger


def session(logger):
    logger.info('Session started')
    group_id = get_group_id(logger)
    token = get_token(logger)
    try:
        vk_session = vk_api.VkApi(token=token)
    except AuthError as e:
        logger.exception(e)
        logger.error('Wrong token')
        os.remove('data/key')
        logger.info('Token removed.')
        return 1
    logger.info('Authorized successfully.')
    try:
        longpoll = VkBotLongPoll(vk_session, group_id=group_id)
    except ApiError as e:
        logger.exception(e)
        logger.error('Wrong group id')
        os.remove('data/id')
        logger.info('Group id removed.')
        return 1
    managers = get_managers(vk_session, group_id)
    for event in longpoll.listen():
        # New messages are interesting only
        if event.type != VkBotEventType.MESSAGE_NEW:
            continue
        msg = event.object
        logger.info('A request to bot: \nchat_id {}, user_id {} message {}'.format(msg.peer_id, msg.from_id, msg.text))
        # Direct message from admin
        if msg.peer_id in managers:
            logger.info('Dev mode')
            if msg.text == 'STOP':
                send_message(vk_session, 'Выключаюсь.', msg.peer_id, logger)
                return -1
            else:
                continue
        # Direct message from other user
        elif msg.peer_id < 2000000001:
            answer = 'К сожалению, сейчас здесь пусто. Бот открыт к предложениям по внутреннему наполнению. Stay tuned.'
            send_message(vk_session, answer, msg.peer_id, logger)
            continue
        # Got it! A message for me from a chat.
        params = {'vk_session': vk_session, 'chat_id': msg.peer_id, 'peer_id': msg.from_id, 'logger': logger}
        new_game = Game(**params)
        answer = new_game.run(msg.text.lower())
        send_message(vk_session, answer, msg.peer_id, logger)
        continue
