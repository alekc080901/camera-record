import json

import redis

from typing import Literal
from itertools import chain


class RedisConnection:
    """
    Подключение к базе данных Redis.
    Singleton.
    """
    connection = None

    def __new__(cls, *args, **kwargs):
        if cls.connection is None:
            cls.connection = super().__new__(cls)
        return cls.connection

    def __init__(self, host='127.0.0.1', port=6379, db_num=0):
        self._r = redis.Redis(host=host, port=port, db=db_num)
        self._connection = self

    def __getitem__(self, item):
        if val := self._r.get(item):
            return json.loads(val)

    def __setitem__(self, key, value):
        self._r.set(key, json.dumps(value))

    def get_keys(self, pattern: str):
        """
        Получение списка ключей по паттерну.
        :param pattern: Шаблон поиска
        :return: Список ключей
        """
        results = self._r.keys(pattern)
        return [r.decode('utf-8') for r in results]

    def get_all_records(self):
        """
        Получение отложенных и регулярных записей в json-friendly формате.
        :return: Словарь со всеми записями
        """
        return {
            'records': {rec: self[rec] for rec in self.get_keys('videos:*')},
            'regularRecords': {rec: self[rec] for rec in self.get_keys('regular:*')}
        }

    def delete_record(self, name):
        """
        Удаление записи по имени.
        :param name: Имя записи
        """
        keys = chain(self._r.keys('videos:*'), self._r.keys('regular:*'))
        for key in keys:
            if self[key]['name'] == name:
                self._r.delete(key)
                self._r.delete(f'tasks:{key}')
                break

    def has(self, pattern: str) -> bool:
        """
        Есть ли ключ в БД.
        :param pattern: Шаблон поиска
        :return: True or False
        """
        return any(True for _ in self._r.scan_iter(pattern))

    def change_record_status(self, key: str, status_value: Literal['queued', 'in_progress', 'error', 'completed']):
        """
        Изменение статуса записи.
        :param key: Ключ записи
        :param status_value: 'queued', 'in_progress', 'error', 'completed'
        """
        content = self[key]
        content['status'] = status_value
        self[key] = content

    def init_task(self, key: str):
        """
        Создание таски записи.
        :param key: Ключ записи
        """
        self.change_record_status(key, 'in_progress')
        self[f'tasks:{key}'] = {}

    def task_is_running(self, key: str) -> bool:
        """
        Есть ли в БД запущенная таска.
        :param key: Ключ записи
        :return: True or False
        """
        return self[f'tasks:{key}'] is not None

    def complete_task(self, key: str):
        """
        Завершение таски (то есть ее удаление).
        :param key: Ключ записи
        """
        self._r.delete(f'tasks:{key}')
        self.change_record_status(key, 'completed')

    # Пока не используется
    def add_running_process(self, key: str, pid: int, path: str):
        """
        Добавление запущенного процесса записи в таску.
        :param key: Ключ записи
        :param pid: PID процесса
        :param path: Путь к записываемому файлу
        """
        task_info = self[f'tasks:{key}']
        task_info[pid] = path
        self[f'tasks:{key}'] = task_info

    # Пока не используется
    def complete_process(self, key: str, pid: int):
        """
        Завершение процесса из таски (его удаление).
        :param key: Ключ записи
        :param pid: PID процесса
        """
        task_info = self[f'tasks:{key}']
        del task_info[str(pid)]
        self[f'tasks:{key}'] = task_info

    def reset_tasks(self):
        """
        Удаление всех тасок из БД.
        """
        if keys := self._r.keys('tasks:*'):
            self._r.delete(*keys)

    def subscribe(self, channel: str):
        """
        Subscribe-метод из Redis Publisher-Subscriber.
        :param channel: Канал записи
        :return: Объект записи
        """
        p = self._r.pubsub()
        p.subscribe(channel)
        return p

    def publish(self, channel: str, message: str):
        """
        Subscribe-метод из Redis Publisher-Subscriber.
        :param channel: Канал записи
        :param message: Сообщение
        """
        self._r.publish(channel, message)


RedisConnection()  # Инициализируем Singleton на месте
