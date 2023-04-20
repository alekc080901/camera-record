import json

import redis

from typing import Literal


class RedisConnection:
    """
    Подключение к базе данных Redis.
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
        results = self._r.keys(pattern)
        return [r.decode('utf-8') for r in results]

    def load_records_dict(self):
        return {
            'records': {rec: self[rec] for rec in self.get_keys('videos:*')},
            'regularRecords': {rec: self[rec] for rec in self.get_keys('regular:*')}
        }

    def has(self, pattern: str) -> bool:
        return any(True for _ in self._r.scan_iter(pattern))

    def change_record_status(self, key: str, status_value: Literal['queued', 'in_progress', 'error', 'completed']):
        content = self[key]
        content['status'] = status_value
        self[key] = content

    def drop_regular_statuses(self, default: Literal['queued', 'in_progress', 'error', 'completed'] = 'queued'):
        keys = self._r.keys('regular:*')
        for key in keys:
            val = self[key]

            if isinstance(val, dict) and 'status' in val:
                val['status'] = default

            self[key] = val

    def init_task(self, key: str):
        self.change_record_status(key, 'in_progress')

        self._r[f'tasks:{key}'] = 0

    def task_is_running(self, key: str) -> bool:
        return self[f'tasks:{key}'] is not None

    def complete_task(self, key: str):
        self._r.delete(f'tasks:{key}')
        self.change_record_status(key, 'completed')

    def reset_tasks(self):
        if keys := self._r.keys('tasks:*'):
            self._r.delete(*keys)

    def subscribe(self, channel: str):
        p = self._r.pubsub()
        p.subscribe(channel)
        return p

    def publish(self, channel: str, message: str):
        self._r.publish(channel, message)


RedisConnection()
