import datetime
import re
from os.path import join as pjoin, exists
from numpy.random import choice
from numpy import argmax
from db_processing import dbRead, dbWrite
from vk_requests import getName

class game:
    def __init__(self, vk_session, peer_id, chat_id, logger):
        self.chat_id = chat_id
        self.vk_session = vk_session
        self.user_id = peer_id
        self.logger = logger
        self.db = pjoin('data', 'rw' + str(self.chat_id) + '.db')
        if not(exists(self.db)):
            dbWrite(self.db, 'create_db')
        self.__keys = ['выбрать', 'топ', 'статистика', 'присоединиться', 'участники', 'помощь']
        self.commands =  {'выбрать': self.commandPlay,
                          'топ': self.commandStats,
                          'статистика': self.commandPersonalStats,
                          'присоединиться': self.commandNewPlayer,
                          'участники': self.commandPlayers,
                          'несколько команд': self.commandTooMany,
                          'команда не определена': self.commandUndefined,
                          'помощь': self.commandHelp}

    def __checkCommand(self, request):
        mask = [(not re.search(k, request) is None) for k in self.__keys]
        if sum(mask) > 1:
            return 'несколько команд'
        elif sum(mask) == 0:
            return 'команда не определена'
        else:
            return self.__keys[argmax(mask)]

    def currentPlayers(self):
        return [p[0] for p in dbRead(self.db, 'get_players')]

    def commandHelp(self):
        return """Присоединиться – присоединиться к "Пидору дня".
Выбрать – выбрать пидора дня.
Топ – топ пидоров за все время.
Статистика – персональная статистика по "Пидору дня".
Участники – список участников игры данного чата.
Помощь – посмотреть полный список комманд.
Список команд пополняется (да, я туповат)."""

    def commandNewPlayer(self):
        if dbRead(self.db, 'personal', user_id=self.user_id):
            return('Эй, ты уже в игре!')
        else:
            dbWrite(self.db, 'new', user_id=self.user_id)
            return('Добро пожаловать в игру!')

    def commandPersonalStats(self):
        name = getName(self.vk_session, self.user_id)
        try:
            count, date = dbRead(self.db, 'personal', user_id=self.user_id)[0]
        except IndexError:
            return('Сначала тебе стоит присоединиться к игре!')
        msg = '{}, ты был пидором дня {} раз!'.format(name, count)
        if count > 0:
            if date == None:
                date = 'я забыл, когда'
            msg += '\nПоследний раз – {}.'.format(date)
        return msg

    def commandPlay(self):
        today = str(datetime.datetime.today())[:10]
        # For case there are no dates in the DB.
        try:
            the_day, last_id = dbRead(self.db, 'last_day')[0]
        except:
            the_day = '0000-00-00'

        if today == the_day:
            msg = 'Для тех, кто пропустил: сегодняшний пидор дня – {}!'.format(getName(self.vk_session, last_id))
            return msg

        if len(self.currentPlayers()) == 0:
            return('Никто еще не присоединился, вот пидоры.')

        user_id = choice(self.currentPlayers())
        dbWrite(self.db, 'increment', user_id=user_id)
        msg = 'Пидор дня - [id{}|{}]!'.format(user_id, getName(self.vk_session, user_id))
        return msg

    def commandPlayers(self):
        names = [getName(self.vk_session, id) for id in self.currentPlayers()]
        if len(names) == 0:
            return 'Какие участники? Никто еще не присоединился! Автопидоры!'
        msg = 'Всего игроков: {}, полный список: {}'.\
        format(len(names), ', '.join(names))
        return msg

    def commandStats(self):
        stats = dbRead(self.db, 'overall')
        if len(self.currentPlayers()) == 0:
            return "Еще никто не присоединился к игре."
        msg = 'Топ пидоров за все время:\n'
        for index, st in enumerate(stats):
            msg = msg + '{}. {}: {} раз(а)\n'.format(index + 1, getName(self.vk_session, st[0]), st[1])
        return msg

    def commandTooMany(self):
        return """Несколько команд в одном запросе!
Делать мне нечего – выбирать за такого пидора, как ты!
Сначала определись, а потом пиши."""

    def commandUndefined(self):
        return """Команда не распознана.
Для вывода списка комманд набери "помощь"."""

    def run(self, request):
        return self.commands[self.__checkCommand(request)]()
