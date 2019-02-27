import datetime
import re
from os.path import join as pjoin, exists

import numpy.random
from numpy import argmax

from db_processing import db_read, db_write
from vk_requests import get_name


class Game:
    def __init__(self, vk_session, peer_id, chat_id, logger):
        self.chat_id = chat_id
        self.vk_session = vk_session
        self.user_id = peer_id
        self.logger = logger
        self.db = pjoin('data', 'rw' + str(self.chat_id) + '.db')
        if not (exists(self.db)):
            db_write(self.db, 'create_db')
        self.__keys = ['выбрать', 'топ', 'статистика', 'присоединиться', 'участники', 'помощь']
        self.commands = {'выбрать': self.command_play,
                         'топ': self.command_stats,
                         'статистика': self.command_personal_stats,
                         'присоединиться': self.command_new_player,
                         'участники': self.command_players,
                         'несколько команд': self.command_too_many,
                         'команда не определена': self.command_undefined,
                         'помощь': self.command_help}

    def __check_command(self, request):
        mask = [(not re.search(k, request) is None) for k in self.__keys]
        if sum(mask) > 1:
            return 'несколько команд'
        elif sum(mask) == 0:
            return 'команда не определена'
        else:
            return self.__keys[argmax(mask)]

    def current_players(self):
        return [p[0] for p in db_read(self.db, 'get_players')]

    def command_help(self):
        return """Присоединиться – присоединиться к "Пидору дня".
Выбрать – выбрать пидора дня.
Топ – топ пидоров за все время.
Статистика – персональная статистика по "Пидору дня".
Участники – список участников игры данного чата.
Помощь – посмотреть полный список комманд.
Список команд пополняется (да, я туповат)."""

    def command_undefined(self):
        return """Команда не распознана.
Для вывода списка комманд набери "помощь"."""

    def command_too_many(self):
        return """Несколько команд в одном запросе!
Делать мне нечего – выбирать за такого пидора, как ты!
Сначала определись, а потом пиши."""

    def command_new_player(self):
        if db_read(self.db, 'personal', user_id=self.user_id):
            return 'Эй, ты уже в игре!'
        else:
            db_write(self.db, 'new', user_id=self.user_id)
            return 'Добро пожаловать в игру!'

    def command_personal_stats(self):
        name = get_name(self.vk_session, self.user_id)
        try:
            count, date = db_read(self.db, 'personal', user_id=self.user_id)[0]
        except IndexError:
            return 'Сначала тебе стоит присоединиться к игре!'
        msg = '{}, ты был пидором дня {} раз!'.format(name, count)
        if count > 0:
            if date is None:
                date = 'я забыл, когда'
            elif date == str(datetime.date.today()):
                date = 'сегодня'
            elif date == str(datetime.date.today() - datetime.timedelta(1)):
                date = 'вчера'
            msg += '\nПоследний раз – {}.'.format(date)
        return msg

    def command_play(self):
        global last_id
        today = str(datetime.date.today())
        # For case there are no dates in the DB.
        try:
            the_day, last_id = db_read(self.db, 'last_day')[0]
        except Exception:
            the_day = '0000-00-00'

        if today == the_day:
            msg = 'Для тех, кто пропустил: сегодняшний пидор дня – {}!'.format(get_name(self.vk_session, last_id))
            return msg

        if len(self.current_players()) == 0:
            return 'Никто еще не присоединился, вот пидоры.'

        user_id = numpy.random.choice(self.current_players())
        db_write(self.db, 'increment', user_id=user_id)
        msg = 'Пидор дня - [id{}|{}]!'.format(user_id, get_name(self.vk_session, user_id))
        return msg

    def command_players(self):
        names = [get_name(self.vk_session, _id) for _id in self.current_players()]
        if len(names) == 0:
            return 'Какие участники? Никто еще не присоединился! Автопидоры!'
        msg = 'Всего игроков: {}, полный список: {}'. \
            format(len(names), ', '.join(names))
        return msg

    def command_stats(self):
        stats = db_read(self.db, 'overall')
        if len(self.current_players()) == 0:
            return "Еще никто не присоединился к игре."
        msg = 'Топ пидоров за все время:\n'
        for index, st in enumerate(stats):
            msg = msg + '{}. {}: {} раз(а)\n'.format(index + 1, get_name(self.vk_session, st[0]), st[1])
        return msg

    def run(self, request):
        return self.commands[self.__check_command(request)]()
