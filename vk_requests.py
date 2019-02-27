import numpy.random
from time import sleep


def get_managers(vk_session, group_id):
    result = vk_session.method('groups.getMembers', {'group_id': group_id, 'filter': 'managers'})
    managers = result['items']
    return [manager['id'] for manager in managers]


def get_name(vk_session, user_id, _format='full'):
    user = vk_session.method('users.get', {'user_ids': user_id})[0]
    if format == 'full':
        return user['first_name'] + ' ' + user['last_name']
    elif format == 'first':
        return user['first_name']
    elif format == 'last':
        return user['last_name']
    else:
        raise KeyError('undefined format')


def send_message(vk_session, msg, chat_id, logger):
    vk_session.method('messages.send', {'peer_id': chat_id, 'message': msg, 'random_id': numpy.random.randint(2 ** 20)})
    logger.info('Bot sent a message: {}'.format(msg))
    sleep(1)
